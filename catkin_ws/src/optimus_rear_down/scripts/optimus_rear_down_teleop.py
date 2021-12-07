#!/usr/bin/env python
import rospy

from std_msgs.msg import Float64

import sys, select, termios, tty

msg = """
Moving around:
   u    i    o
   j    k    l
   m    ,    .
q/w : increase/decrease max speeds by 10%
a/s : increase/decrease only linear speed by 10%
z/x : increase/decrease only angular speed by 10%
space key, k : force stop
anything else : stop smoothly

UR10 Control:

q/w : Shoulder Pan
a/s : Shoulder Lift
z/x : Elbow
q/w : Wrist 1
a/s : Wrist 2
z/x : Wrist 3

CTRL-C to quit
"""

moveBindings = {
        'i':(1,0),
        'o':(1,-1),
        'j':(0,1),
        'l':(0,-1),
        'u':(1,1),
        ',':(-1,0),
        '.':(-1,1),
        'm':(-1,-1),
           }

speedBindings={
        'q':(1.1,1.1),
        'w':(.9,.9),
        'a':(1.1,1),
        's':(.9,1),
        'z':(1,1.1),
        'x':(1,.9),
          }

UR10_bindings = ['e', 'r', 'd', 'f', 'c', 'v', 't', 'y', 'g', 'h', 'b', 'n']

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

speed = 8
turn = 0.5

SPP = 0.0
SLP = 0.0
EP = 0.0
W1P = 0.0
W2P = 0.0
W3P = 0.0

dock_flag = False

def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)
    
    rospy.init_node('optimus_control')

    # pub_right = rospy.Publisher('/optimus_FR_outer_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Right connector
    # pub_left = rospy.Publisher('/optimus_FL_outer_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Left connector
    # pub_right = rospy.Publisher('/optimus_FR_inner_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Right connector
    # pub_left = rospy.Publisher('/optimus_FL_inner_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Left connector
    pub_move_ROR = rospy.Publisher('/optimus_rear_namespace/optimus_RR_outer_wheel_controller/command', Float64, queue_size=10) # Publisher for Front-Right wheel
    pub_move_ROL = rospy.Publisher('/optimus_rear_namespace/optimus_RL_outer_wheel_controller/command', Float64, queue_size=10) # Publisher for Front-Left wheel
    pub_move_RIR = rospy.Publisher('/optimus_rear_namespace/optimus_RR_inner_wheel_controller/command', Float64, queue_size=10) # Publisher for Rear-Right wheel
    pub_move_RIL = rospy.Publisher('/optimus_rear_namespace/optimus_RL_inner_wheel_controller/command', Float64, queue_size=10) # Publisher for Rear-Left wheel

    # UR10 Control
    pub_shouler_pan = rospy.Publisher('/optimus_rear_namespace/UR10_shoulder_pan_joint_controller/command', Float64, queue_size=10)
    pub_shouler_lift = rospy.Publisher('/optimus_rear_namespace/UR10_shoulder_lift_joint_controller/command', Float64, queue_size=10)
    pub_elbow = rospy.Publisher('/optimus_rear_namespace/UR10_elbow_joint_controller/command', Float64, queue_size=10)
    pub_shouler_wrist_1 = rospy.Publisher('/optimus_rear_namespace/UR10_wrist_1_joint_controller/command', Float64, queue_size=10)
    pub_shouler_wrist_2 = rospy.Publisher('/optimus_rear_namespace/UR10_wrist_2_joint_controller/command', Float64, queue_size=10)
    pub_shouler_wrist_3 = rospy.Publisher('/optimus_rear_namespace/UR10_wrist_3_joint_controller/command', Float64, queue_size=10)
    
    x = 0
    th = 0
    status = 0
    count = 0
    acc = 0.1
    target_speed = 0
    target_turn = 0
    control_speed = 0
    control_turn = 0
    try:
        print msg
        print vels(speed,turn)
        while(1):
            key = getKey()
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                th = moveBindings[key][1]
                count = 0
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]
                count = 0

                print vels(speed,turn)
                if (status == 14):
                    print msg
                status = (status + 1) % 15
            elif key == ' ' or key == 'k' :
                x = 0
                th = 0
                control_speed = 0
                control_turn = 0
            else:
                count = count + 1
                if count > 4:
                    x = 0
                    th = 0
                if (key == '\x03'):
                    break

            target_speed = speed * x
            target_turn = turn * th

            if target_speed > control_speed:
                control_speed = min( target_speed, control_speed + 0.02 )
            elif target_speed < control_speed:
                control_speed = max( target_speed, control_speed - 0.02 )
            else:
                control_speed = target_speed

            if key == 'j' or key  == 'l':
                if target_turn > control_turn:
                    control_turn = min( target_turn, control_turn + 0.1 )
                elif target_turn < control_turn:
                    control_turn = max( target_turn, control_turn - 0.1 )
                else:
                    control_turn = target_turn

                speed_right = control_turn
                speed_left = -control_turn

                gain = 1

                if key == 'j':
                    pub_move_ROR.publish(speed_right)
                    pub_move_RIR.publish(speed_right)

                    pub_move_ROL.publish(gain*speed_left)
                    pub_move_RIL.publish(gain*speed_left)

                if key == 'l':
                    pub_move_ROL.publish(speed_left)
                    pub_move_RIL.publish(speed_left)

                    pub_move_ROR.publish(gain*speed_right)
                    pub_move_RIR.publish(gain*speed_right)
            else:
                speed_right = control_speed
                speed_left = control_speed
                pub_move_ROR.publish(speed_right)
                pub_move_RIR.publish(speed_right)

                pub_move_ROL.publish(speed_left)
                pub_move_RIL.publish(speed_left)

            # UR10 Control
            if key in UR10_bindings:
                if key == 'e':
                    SPP += 0.1
                if key == 'r':
                    SPP -= 0.1
                if key == 'd':
                    SLP += 0.1
                if key == 'f':
                    SLP -= 0.1
                if key == 'c':
                    EP += 0.1
                if key == 'v':
                    EP -= 0.1
                if key == 't':
                    W1P += 0.1
                if key == 'y':
                    W1P -= 0.1
                if key == 'g':
                    W2P += 0.1
                if key == 'h':
                    W2P -= 0.1
                if key == 'b':
                    W3P += 0.1
                if key == 'n':
                    W3P -= 0.1

                pub_shouler_pan.publish(SPP)
                pub_shouler_lift.publish(SLP)
                pub_elbow.publish(EP)
                pub_shouler_wrist_1.publish(W1P)
                pub_shouler_wrist_2.publish(W2P)
                pub_shouler_wrist_3.publish(W3P)

    except:
        pass
        # print e

    finally:
        pub_move_ROR.publish(speed_right)
        pub_move_RIR.publish(speed_right)

        pub_move_ROL.publish(speed_left)
        pub_move_RIL.publish(speed_left)
        # twist = Twist()
        # twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        # twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        # pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
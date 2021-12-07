#!/usr/bin/env python
import rospy

from std_msgs.msg import Float64

import sys, select, termios, tty

msg = """
Moving around:
        i    
   j    k    l
        ,    
q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
space key, k : force stop
anything else : stop smoothly

r/v: Front Outer Bogie
t/b: Rear Outer Bogie
y/n: Front Inner Bogie
u/m: Rear Inner Bogie

a: Toggle Attached Mode (Front/Rear Bogie Joint Control)

CTRL-C to quit
"""

moveBindings = {
        'i':(1,0),
        'j':(0,1),
        'l':(0,-1),
        ',':(-1,0),
           }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
          }

heightBindings = ['r', 'v', 't', 'b', 'y', 'n', 'u', 'm']

flags = ['a', 'd']

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

FOC = 0.0
ROC = 0.0
FIC = 0.0
RIC = 0.0

attached_flag = False

def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)
    
    rospy.init_node('optimus_control')

    # Front Outer Wheels
    pub_move_FOR = rospy.Publisher('/optimus_FR_outer_wheel_controller/command', Float64, queue_size=10) # Publisher for Front-Right wheel
    pub_move_FOL = rospy.Publisher('/optimus_FL_outer_wheel_controller/command', Float64, queue_size=10) # Publisher for Front-Left wheel
    # Rear Outer Wheels
    pub_move_ROR = rospy.Publisher('/optimus_RR_outer_wheel_controller/command', Float64, queue_size=10) # Publisher for Front-Right wheel
    pub_move_ROL = rospy.Publisher('/optimus_RL_outer_wheel_controller/command', Float64, queue_size=10) # Publisher for Fron/    pub_move_FIR = rospy.Publisher('/optimus_FR_inner_wheel_controller/command', Float64, queue_size=10) # Publisher for Rear-Right wheel

    # Outer Connectors
    pub_FORC = rospy.Publisher('/optimus_FR_outer_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Right connector
    pub_FOLC = rospy.Publisher('/optimus_FL_outer_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Left connector
    pub_RORC = rospy.Publisher('/optimus_RR_outer_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Right connector
    pub_ROLC = rospy.Publisher('/optimus_RL_outer_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Left connector

    # Inner Connectors
    pub_FIRC = rospy.Publisher('/optimus_FR_inner_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Right connector
    pub_FILC = rospy.Publisher('/optimus_FL_inner_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Left connector
    pub_RIRC = rospy.Publisher('/optimus_RR_inner_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Right connector
    pub_RILC = rospy.Publisher('/optimus_RL_inner_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Left connector

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

            # Velocity Control
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
                    pub_move_FOR.publish(speed_right)
                    pub_move_ROR.publish(speed_right)

                    pub_move_FOL.publish(gain*speed_left)
                    pub_move_ROL.publish(gain*speed_left)

                if key == 'l':
                    pub_move_FOL.publish(speed_left)
                    pub_move_ROL.publish(speed_left)

                    pub_move_FOR.publish(gain*speed_right)
                    pub_move_ROR.publish(gain*speed_right)
            else:
                speed_right = control_speed
                speed_left = control_speed
                pub_move_FOR.publish(speed_right)
                pub_move_ROR.publish(speed_right)

                pub_move_FOL.publish(speed_left)
                pub_move_ROL.publish(speed_left)

            # Flag Control
            if key in flags:
                if key == 'a':
                    attached_flag = not attached_flag
                    print("Attached Mode: %d"%attached_flag)

            # Connector Control
            if key in heightBindings:
                if key == 'r':
                    FOC += 0.001
                if key == 'v':
                    FOC -= 0.001
                if key == 't':
                    ROC += 0.001
                if key == 'b':
                    ROC -= 0.001
                if key == 'y':
                    FIC += 0.1
                if key == 'n':
                    FIC -= 0.1
                if key == 'u':
                    RIC += 0.1
                if key == 'm':
                    RIC -= 0.1

                if(attached_flag):
                    FOC = ROC
                    FIC = RIC

                    pub_FORC.publish(FOC)
                    pub_FOLC.publish(FOC)
                    pub_RORC.publish(ROC)
                    pub_ROLC.publish(ROC)

                    pub_FIRC.publish(FIC)
                    pub_FILC.publish(FIC)
                    pub_RIRC.publish(RIC)
                    pub_RILC.publish(RIC)
                else:
                    pub_FORC.publish(FOC)
                    pub_FOLC.publish(FOC)
                    pub_RORC.publish(ROC)
                    pub_ROLC.publish(ROC)

                    pub_FIRC.publish(FIC)
                    pub_FILC.publish(FIC)
                    pub_RIRC.publish(RIC)
                    pub_RILC.publish(RIC)

    except:
        pass
        # print e

    finally:
        pub_move_FOR.publish(speed_right)
        pub_move_ROR.publish(speed_right)

        pub_move_FOL.publish(speed_left)
        pub_move_ROL.publish(speed_left)
        # twist = Twist()
        # twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        # twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        # pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
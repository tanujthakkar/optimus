#!/usr/bin/env python
import rospy

from std_msgs.msg import Float64

import sys, select, termios, tty

msg = """
UR10 Front Control:

q/w : Shoulder Pan
a/s : Shoulder Lift
z/x : Elbow
e/r : Wrist 1
d/f : Wrist 2
c/v : Wrist 3

UR10 Rear Control:

t/y : Shoulder Pan
g/h : Shoulder Lift
b/n : Elbow
u/i : Wrist 1
j/k : Wrist 2
m/, : Wrist 3


CTRL-C to quit
"""

UR10_front_bindings = ['q', 'w', 'a', 's', 'z', 'x', 'e', 'r', 'd', 'f', 'c', 'v']

UR10_rear_bindings = ['t', 'y', 'g', 'h', 'b', 'n', 'u', 'i', 'j', 'k', 'm', ',']

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

front_SPP = 0.0
front_SLP = 0.0
front_EP = 0.0
front_W1P = 0.0
front_W2P = 0.0
front_W3P = 0.0

rear_SPP = 0.0
rear_SLP = 0.0
rear_EP = 0.0
rear_W1P = 0.0
rear_W2P = 0.0
rear_W3P = 0.0

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)
    
    rospy.init_node('UR10_control')

    # UR10 Front Control
    pub_front_shouler_pan = rospy.Publisher('UR10_front_shoulder_pan_joint_controller/command', Float64, queue_size=10)
    pub_front_shouler_lift = rospy.Publisher('UR10_front_shoulder_lift_joint_controller/command', Float64, queue_size=10)
    pub_front_elbow = rospy.Publisher('UR10_front_elbow_joint_controller/command', Float64, queue_size=10)
    pub_front_shouler_wrist_1 = rospy.Publisher('UR10_front_wrist_1_joint_controller/command', Float64, queue_size=10)
    pub_front_shouler_wrist_2 = rospy.Publisher('UR10_front_wrist_2_joint_controller/command', Float64, queue_size=10)
    pub_front_shouler_wrist_3 = rospy.Publisher('UR10_front_wrist_3_joint_controller/command', Float64, queue_size=10)
    
    # UR10 rear Control
    pub_rear_shouler_pan = rospy.Publisher('UR10_rear_shoulder_pan_joint_controller/command', Float64, queue_size=10)
    pub_rear_shouler_lift = rospy.Publisher('UR10_rear_shoulder_lift_joint_controller/command', Float64, queue_size=10)
    pub_rear_elbow = rospy.Publisher('UR10_rear_elbow_joint_controller/command', Float64, queue_size=10)
    pub_rear_shouler_wrist_1 = rospy.Publisher('UR10_rear_wrist_1_joint_controller/command', Float64, queue_size=10)
    pub_rear_shouler_wrist_2 = rospy.Publisher('UR10_rear_wrist_2_joint_controller/command', Float64, queue_size=10)
    pub_rear_shouler_wrist_3 = rospy.Publisher('UR10_rear_wrist_3_joint_controller/command', Float64, queue_size=10)
    
    try:
        print msg
        while(1):
            key = getKey()

            if (key == '\x03'):
                    break

            # UR10 Front Control
            if key in UR10_front_bindings:
                if key == 'q':
                    front_SPP += 0.1
                if key == 'w':
                    front_SPP -= 0.1
                if key == 'a':
                    front_SLP += 0.1
                if key == 's':
                    front_SLP -= 0.1
                if key == 'z':
                    front_EP += 0.1
                if key == 'x':
                    front_EP -= 0.1
                if key == 'e':
                    front_W1P += 0.1
                if key == 'r':
                    front_W1P -= 0.1
                if key == 'd':
                    front_W2P += 0.1
                if key == 'f':
                    front_W2P -= 0.1
                if key == 'c':
                    front_W3P += 0.1
                if key == 'v':
                    front_W3P -= 0.1

                pub_front_shouler_pan.publish(front_SPP)
                pub_front_shouler_lift.publish(front_SLP)
                pub_front_elbow.publish(front_EP)
                pub_front_shouler_wrist_1.publish(front_W1P)
                pub_front_shouler_wrist_2.publish(front_W2P)
                pub_front_shouler_wrist_3.publish(front_W3P)

            if key in UR10_rear_bindings:
                if key == 't':
                    rear_SPP += 0.1
                if key == 'y':
                    rear_SPP -= 0.1
                if key == 'g':
                    rear_SLP += 0.1
                if key == 'h':
                    rear_SLP -= 0.1
                if key == 'b':
                    rear_EP += 0.1
                if key == 'n':
                    rear_EP -= 0.1
                if key == 'u':
                    rear_W1P += 0.1
                if key == 'i':
                    rear_W1P -= 0.1
                if key == 'j':
                    rear_W2P += 0.1
                if key == 'k':
                    rear_W2P -= 0.1
                if key == 'm':
                    rear_W3P += 0.1
                if key == ',':
                    rear_W3P -= 0.1

                pub_rear_shouler_pan.publish(rear_SPP)
                pub_rear_shouler_lift.publish(rear_SLP)
                pub_rear_elbow.publish(rear_EP)
                pub_rear_shouler_wrist_1.publish(rear_W1P)
                pub_rear_shouler_wrist_2.publish(rear_W2P)
                pub_rear_shouler_wrist_3.publish(rear_W3P)

    except:
        pass
        # print e

    finally:
        pass
        # twist = Twist()
        # twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        # twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        # pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
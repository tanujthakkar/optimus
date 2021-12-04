#!/usr/bin/env python

import rospy

from std_msgs.msg import Float64
from optimus.msg import optimus_telemetry


# Defining a global custom message
optimus_telemetry_ = optimus_telemetry()


def callback_optimus_telemetry_sub(data):

	global optimus_telemetry_

	print("Subscriber - Left: %.2f Right:%.2f move_FL: %.2f move_FR: %.2f move_RL: %.2f move_RR: %.2f"
					%(optimus_telemetry_.left.data, optimus_telemetry_.right.data,
						optimus_telemetry_.move_FL.data, optimus_telemetry_.move_FR.data,
						optimus_telemetry_.move_RL.data, optimus_telemetry_.move_RR.data))


def main():

	global optimus_telemetry_

	rospy.init_node('optimus_control')

	pub_right = rospy.Publisher('/optimus_FR_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Right connector
	pub_left = rospy.Publisher('/optimus_FL_wheel_connector_controller/command', Float64, queue_size=10) # Publisher for Front-Left connector
	pub_move_FR = rospy.Publisher('/optimus_FR_wheel_controller/command', Float64, queue_size=10) # Publisher for Front-Right wheel
	pub_move_FL = rospy.Publisher('/optimus_FL_wheel_controller/command', Float64, queue_size=10) # Publisher for Front-Left wheel
	pub_move_RR = rospy.Publisher('/optimus_RR_wheel_controller/command', Float64, queue_size=10) # Publisher for Rear-Right wheel
	pub_move_RL = rospy.Publisher('/optimus_RL_wheel_controller/command', Float64, queue_size=10) # Publisher for Rear-Left wheel

	optimus_telemetry_pub = rospy.Publisher('/optimus_telemetry_info', optimus_telemetry, queue_size=10) # Publisher for optimus_telemetry data

	optimus_telemetry_sub = rospy.Subscriber('/optimus_telemetry_info', optimus_telemetry, callback_optimus_telemetry_sub) # Subscriber for optimus_telemetry data

	# Assigning control commands
	optimus_telemetry_.left.data = 0.4 # [rad] left steering position
	optimus_telemetry_.right.data = 0.4 # [rad] right steering position
	optimus_telemetry_.move_FL.data = 2.0 # [m/s] FL velocity control command
	optimus_telemetry_.move_FR.data = 2.0 # [m/s] FR velocity control command
	optimus_telemetry_.move_RL.data = 2.0 # [m/s] RL velocity control command
	optimus_telemetry_.move_RR.data = 2.0 # [m/s] RR velocity control command

	rate = rospy.Rate(10)

	while not rospy.is_shutdown():
		# Publishing control commands
		pub_right.publish(optimus_telemetry_.left)
		pub_left.publish(optimus_telemetry_.right)
		pub_move_FR.publish(optimus_telemetry_.move_FL)
		pub_move_FL.publish(optimus_telemetry_.move_FR)
		pub_move_RR.publish(optimus_telemetry_.move_RL)
		pub_move_RL.publish(optimus_telemetry_.move_RR)

		optimus_telemetry_pub.publish(optimus_telemetry_)

		rate.sleep()


if __name__ == '__main__':
	main()
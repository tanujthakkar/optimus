cmake_minimum_required(VERSION 2.8.3)

project(optimus)

find_package(catkin REQUIRED COMPONENTS
	rospy
	roscpp
	std_msgs
	message_generation)

add_message_files(
  FILES
  optimus_telemetry.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
	CATKIN_DEPENDS message_runtime)

find_package(roslaunch)

foreach(dir config launch meshes urdf)
	install(DIRECTORY ${dir}/
		DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)

catkin_install_python(PROGRAMS scripts/teleop.py scripts/publisher_subscriber.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
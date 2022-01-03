# Optimus - All Terrain Semi-Amphibious Ground Vehicle for Highly Hazardous Scenerios

The following repository is part of a project submitted as coursework for the ENPM662 - Introduction to Robot Modelling course at University of Maryland - College Park. The motivation behind the project was to design a all terrain ground robot inspired from the Axel Rover by NASA/JPL and the Clearpath Robotics Warthog. We developed a differential drive robot that can dynamically adjust its ride height and adapt to the local terrain. Additionally, the robot also features two UR10e arms for manipulation capabilities.


<h3>Setup & Usage<h3>

1. Copy the following ROS packages to your respective catkin_workspace/src
	optimus
	optimus_front_down
	optimus_rear_down
	universal_robot

2. Build the package by navigating back to the catkin_workspace folder in the terminal and run -
	```
	catkin_make
	```
3. Source the catkin_workspace after successful build - 
	```
	source /catkin_workspace/devel/setup.bash
	```
4. For full configuration of the robot, launch Gazebo using the following command -
	```
	roslaunch optimus optimus.launch
	```
   Run the teleop scripts using the following respective commands in different terminals - 
   	```
	rosrun optimus optimus_teleop.py

	rosrun optimus UR10_teleop.py
	```
5. For seperate halves configuration of the robot, launch Gazebo using the following command -
	```
	roslaunch optimus different_namespaces.launch
	```
	Run the teleop scripts using the following respective commands in different terminals - 

	```
	rosrun optimus_front_down optimus_front_down_teleop.py

	rosrun optimus_rear_down optimus_rear_down_teleop.py
	```

Please reach out to us if you face any issues building/running the package.
Tanuj Thakkar - tanuj@umd.edu
Divyansh Agrawal - dagrawa1@umd.edu
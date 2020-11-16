#Created By Sanil Singh on August 7 2020
#Robotics Lab Intern @ NRC Mississauga

#GETTING STARTED WITH PROGRAMMING THE NORTHC9 ROBOT

#This is what we need everytime when starting the code. We import the NorthC9 Class from the northc9 library and get all the attribute associated with this. From the Locator we import using the * which means it will import the contents into the Locator table available in the simulator

from northc9 import NorthC9
from Locator import * 

#We give the variable name "RobotArm" and copy all the contents from the NorthC9 Class (This is what Instiatiate means) to the assigned the variable. What this means is we can now use all the attributes from the class under the assigned variable Ex. RobotArm.Close_Gripper()

RobotArm = NorthC9('A')

#When using the NorthIDE, Its best to always to know your home position, you can use the Locator tool to define a point and reference or through this simple command. This command will default all 4 Axis to their home state

RobotArm.home_robot()

#How to Home a specific Axis
RobotArm.home_axis(RobotArm.Elbow)

#MOVING THE ROBOT ARM - When moving the Robot Arm it is good practice to understand what and where you are moving the robot. The C9 Robot has 4 axis (Elbow, Shoulder, Gripper and Z axis) which can be controlled through rotational COUNTS or RADIANS. 

#Enables Radians
#For Conversions from Counts to Radians please view the MATH Instructional Guide
from math import pi

#Commands for moving in COUNTS & RADIANS
#Moving in COUNTS(Counts range 0 - 24000)
RobotArm.move_axis(RobotArm.GRIPPER,24000)
#Moving in RADIANS
RobotArm.move_axis_rad(RobotArm.SHOULDER,pi/4)

#This Command will allow all 4 axes to be moved to specific location. This command is easier to move the rest of the robot if 1 or more axes need to be positioned at a specific count, Ex. Elbow & Shoulder @ 2000 while you experiment with the Gripper & Z Axis 
RobotArm.move_robot_cts(-3000,1500,2000,3000)

#Other Ways to move the robot arm

#With This Command, The 4 Axis can be fine tuned to a precision of 1mm. In this example we move the Robot Arm down so that is only 50mm above the deck.
RobotArm.move_axis_mm(RobotArm.Z_AXIS, 50)

#With these commands we can move the ELBOW + SHOULDER (xy) or move the ELBOW + SHOULDER + Z AXIS (xyz). THIS IS MOVING THROUGH COORDINATES
RobotArm.move_xy(200,-120)
RobotArm.move_xyz(-150,0,50)

#Assign a point to a variable & call it through the .goto() attribute. This command is very useful when locations are fixed and the RobotArm needs to go there often, Ex. Glass Slide Hotel

Slide_Hotel = [10000,15000 3000, 20000]

RobotArm.goto(Slide_Hotel)  


#HOW TO MAKE THE ROBOT ARM GO FASTER
#The Default Values for the velocity is at 5000 and the acceleration is set at 50000. Adjust values accordingly

RobotArm.default_vel = 40000
RobotArm.default_accel = 150000
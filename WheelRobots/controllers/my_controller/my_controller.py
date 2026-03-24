"""my_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
right_motor = robot.getDevice('RightMotor')
left_motor = robot.getDevice('LeftMotor')

# right_motor.setPosition(float('inf'))
# left_motor.setPosition(float('inf'))

# right_motor.maxVelocity(100)
# left_motor.maxVelocity(100)

# right_motor.setVelocity(0)
# left_motor.setVelocity(0)

IMU_center = robot.getDevice('InertialUnit')
IMU_center.enable(timestep)
count = 1

TWR_center = robot.getDevice('TWRGyro')
TWR_center.enable(timestep)
# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    RPY_value = IMU_center.getRollPitchYaw()
    RAD_value = TWR_center.getValues()
    print(RAD_value[1])

    # k = 0
    # if count < 10:
        # k = 0.2
    # else:
        # k = 0
 
    k=0
    ks = -0.8*(k-RPY_value[1])
    # ks = -0.4*(0-RPY_value[1])
    # ks = 0
    # ks = -0.2*(k-RPY_value[1])+0.0*RAD_value[1]
  
  
    right_motor.setTorque(ks)
    left_motor.setTorque(ks)
    
    count = count + 1
        
    
    
    
    
    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.

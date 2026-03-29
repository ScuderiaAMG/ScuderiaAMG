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

# Use torque control mode.
right_motor.setPosition(float('inf'))
left_motor.setPosition(float('inf'))
right_motor.setVelocity(0.0)
left_motor.setVelocity(0.0)

IMU_center = robot.getDevice('InertialUnit')
IMU_center.enable(timestep)

TWR_center = robot.getDevice('TWRGyro')
TWR_center.enable(timestep)

dt = timestep / 1000.0

# PI gains (start values, tune in Webots).
target_pitch = 0.0
KP = 1.0
KI = 0.8

# Anti-windup and output limits.
integral_error = 0.0
integral_limit = 0.4
torque_limit = 8.0

log_interval_steps = max(1, int(200 / timestep))
step_count = 0


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Pitch is the body tilt for balancing in this model.
    pitch = IMU_center.getRollPitchYaw()[1]
    pitch_rate = TWR_center.getValues()[1]

    # Keep the same control direction as your previous script.
    error = pitch - target_pitch
    integral_error = clamp(integral_error + error * dt, -integral_limit, integral_limit)

    torque_cmd = KP * error + KI * integral_error
    torque_cmd = clamp(torque_cmd, -torque_limit, torque_limit)

    right_motor.setTorque(torque_cmd)
    left_motor.setTorque(torque_cmd)

    if step_count % log_interval_steps == 0:
        print(
            f"pitch={pitch:.4f} rad, rate={pitch_rate:.4f} rad/s, "
            f"integral={integral_error:.4f}, torque={torque_cmd:.3f}"
        )

    step_count += 1

# Enter here exit cleanup code.

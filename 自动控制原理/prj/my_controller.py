"""my_controller controller."""

from controller import Robot
import math

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# 获取设备
right_motor = robot.getDevice('RightMotor')
left_motor = robot.getDevice('LeftMotor')

IMU_center = robot.getDevice('InertialUnit')
IMU_center.enable(timestep)

TWR_center = robot.getDevice('TWRGyro')
TWR_center.enable(timestep)

# --- 配置扰动参数 ---
# 假设 timestep 是 32ms (0.032s)，10 步大约是 0.32 秒
DISTURBANCE_STEPS = 1       
DISTURBANCE_TORQUE = 0.2     # 扰动扭矩大小 (单位：Nm)，根据机器人重量调整，太小没效果，太大会直接摔倒
# -----------------------

count = 1

# Main loop
# while robot.step(timestep) != -1:
#     # 1. 读取传感器
#     RPY_value = IMU_center.getRollPitchYaw()
#     RAD_value = TWR_center.getValues()
    
#     # 2. 控制逻辑分支
#     if count <= DISTURBANCE_STEPS:
#         # === 阶段一：施加扰动 ===
#         # 给两个电机相同的扭矩，利用加速度让车身产生俯仰 (Pitch) 倾斜
#         # 正扭矩通常会让车向前加速，车身因惯性向后仰 (Pitch 变负)
#         right_motor.setTorque(DISTURBANCE_TORQUE)
#         left_motor.setTorque(DISTURBANCE_TORQUE)
#         print(f"Step {count}: Applying Disturbance Torque")
        
#     else:
#         # === 阶段二：正常平衡控制 ===
#         # 你的原始比例控制逻辑
#         k = 0  # 目标角度 0 弧度
#         current_pitch = RPY_value[1]
        
#         # 比例控制 (P-Control)
#         # 注意：这里的 0.8 是增益，如果机器人震荡，尝试减小；如果反应慢，尝试增大
#         #ks = -0.8 * (k - current_pitch) 
        
#         # 可选：加入微分控制 (D-Control) 以增加稳定性
#         angular_velocity = RAD_value[1]
#         ks = -0.5 * (k - current_pitch) +  0.01 * angular_velocity
        
#         right_motor.setTorque(ks)
#         left_motor.setTorque(ks)
        
#         # 打印当前状态以便观察
#         print(f"Pitch: {math.degrees(current_pitch):.2f}°, Torque: {ks:.2f}")

#     count = count + 1




# PI 控制参数（现在 I 通过 a/(s+1) 实现）
Kp = -0.78
a = 0.1         # 可调参数（你提到的 a）
integrator_state = 0.0

target_pitch = 0.0
max_torque = 2.0
dt = timestep / 1000.0

while robot.step(timestep) != -1:
    
    
    if count <= DISTURBANCE_STEPS:
        # === 阶段一：施加扰动 ===
        # 给两个电机相同的扭矩，利用加速度让车身产生俯仰 (Pitch) 倾斜
        # 正扭矩通常会让车向前加速，车身因惯性向后仰 (Pitch 变负)
        right_motor.setTorque(DISTURBANCE_TORQUE)
        left_motor.setTorque(DISTURBANCE_TORQUE)
        print(f"Step {count}: Applying Disturbance Torque")
        
    else:
    
        RPY_value = IMU_center.getRollPitchYaw()
        current_pitch = RPY_value[1]
        error = target_pitch - current_pitch

        # I项：a/(s+1) 等价于一阶滤波器状态方程
        integrator_state += dt * (-integrator_state + a * error)
        u_I = integrator_state

        control_torque = Kp * error + u_I
        control_torque = max(min(control_torque, max_torque), -max_torque)

        right_motor.setTorque(control_torque)
        left_motor.setTorque(control_torque)

        print(f"Pitch: {math.degrees(current_pitch):.2f}°, Err: {math.degrees(error):.2f}°, Torque: {control_torque:.3f}")
        
        
    count = count + 1
    

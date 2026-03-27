import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot, Cpu, Gauge, Zap, Settings, Play, RotateCcw,
  ChevronDown, ChevronRight, BookOpen, Code2, GitBranch,
  Activity, Target, Layers, ArrowRight
} from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

// ==================== Data ====================

const sections = [
  {
    id: 'overview',
    icon: BookOpen,
    title: '总体概述',
    color: 'from-blue-500 to-cyan-500',
    content: {
      summary:
        '这段代码是一个 Webots 仿真平台上的 **两轮自平衡机器人控制器**（类似倒立摆/平衡车）。它通过读取 IMU（惯性测量单元）的姿态信息，使用 PI 控制算法计算控制扭矩，驱动左右电机使机器人保持直立平衡。',
      keyPoints: [
        '平台：Webots 机器人仿真环境',
        '语言：Python（使用 Webots 的 controller 库）',
        '控制目标：使机器人俯仰角（Pitch）保持在 0°',
        '控制算法：改进型 PI 控制（I 项使用一阶低通滤波）',
        '执行器：左右两个直流电机（扭矩控制模式）',
      ],
    },
  },
  {
    id: 'init',
    icon: Settings,
    title: '1. 初始化与设备获取',
    color: 'from-purple-500 to-pink-500',
    content: {
      code: `from controller import Robot
import math

# 创建 Robot 实例
robot = Robot()

# 获取仿真时间步长（毫秒）
timestep = int(robot.getBasicTimeStep())

# 获取电机设备
right_motor = robot.getDevice('RightMotor')
left_motor = robot.getDevice('LeftMotor')

# 获取 IMU（惯性测量单元）
IMU_center = robot.getDevice('InertialUnit')
IMU_center.enable(timestep)

# 获取陀螺仪
TWR_center = robot.getDevice('TWRGyro')
TWR_center.enable(timestep)`,
      explanations: [
        {
          label: 'Robot()',
          desc: '创建机器人实例，这是 Webots 控制器的入口点，所有设备都通过它获取。',
        },
        {
          label: 'getBasicTimeStep()',
          desc: '获取 Webots 世界文件中定义的基本仿真时间步长（通常为 32ms），控制循环每隔这个时间执行一次。',
        },
        {
          label: "getDevice('RightMotor/LeftMotor')",
          desc: '获取左右两个电机的句柄，后续用 setTorque() 直接控制扭矩输出。',
        },
        {
          label: 'InertialUnit (IMU)',
          desc: '惯性测量单元，通过 getRollPitchYaw() 返回三个欧拉角 [Roll, Pitch, Yaw]，其中 Pitch（俯仰角）是平衡控制的关键。',
        },
        {
          label: 'TWRGyro（陀螺仪）',
          desc: '测量角速度的传感器，通过 getValues() 返回三轴角速度 [ωx, ωy, ωz]，在注释掉的 PD 控制中被使用。',
        },
      ],
    },
  },
  {
    id: 'disturbance',
    icon: Zap,
    title: '2. 扰动参数配置',
    color: 'from-orange-500 to-red-500',
    content: {
      code: `# --- 配置扰动参数 ---
DISTURBANCE_STEPS = 1       
DISTURBANCE_TORQUE = 0.2  # 扰动扭矩 (Nm)
# -----------------------
count = 1`,
      explanations: [
        {
          label: 'DISTURBANCE_STEPS = 1',
          desc: '扰动持续的时间步数。仅在第 1 步施加扰动，按 32ms 步长计算大约持续 0.032 秒，非常短暂。',
        },
        {
          label: 'DISTURBANCE_TORQUE = 0.2',
          desc: '扰动扭矩大小，单位 Nm（牛·米）。这个力矩施加到电机上，使车轮加速，车身因惯性产生倾斜。相当于"推一下"机器人来测试其平衡恢复能力。',
        },
        {
          label: 'count 计数器',
          desc: '用于记录当前是第几步，决定是处于"扰动阶段"还是"平衡控制阶段"。',
        },
      ],
    },
  },
  {
    id: 'commented',
    icon: GitBranch,
    title: '3. 注释掉的 PD 控制（旧版本）',
    color: 'from-gray-500 to-gray-600',
    content: {
      code: `# 旧版 PD 控制逻辑（已注释）
k = 0  # 目标角度
current_pitch = RPY_value[1]
angular_velocity = RAD_value[1]

# P项 + D项
ks = -0.5 * (k - current_pitch) + 0.01 * angular_velocity

right_motor.setTorque(ks)
left_motor.setTorque(ks)`,
      explanations: [
        {
          label: 'P 项（比例控制）',
          desc: '-0.5 × (目标角度 - 当前角度)：角度偏差越大，输出扭矩越大，但单纯 P 控制会产生稳态误差且容易震荡。',
        },
        {
          label: 'D 项（微分控制）',
          desc: '0.01 × 角速度：利用陀螺仪测量角速度作为微分项，相当于"阻尼"，抑制震荡，增加系统稳定性。',
        },
        {
          label: '为什么被弃用？',
          desc: 'PD 控制无法消除稳态误差（机器人可能持续偏离垂直位置），因此升级为下方的 PI 控制方案。',
        },
      ],
    },
  },
  {
    id: 'pi-control',
    icon: Target,
    title: '4. 主控制循环 — 改进型 PI 控制',
    color: 'from-green-500 to-emerald-500',
    content: {
      code: `# PI 控制参数
Kp = -0.78          # 比例增益
a = 0.1             # I项滤波参数
integrator_state = 0.0  # 积分器状态变量
target_pitch = 0.0  # 目标俯仰角（0 = 竖直）
max_torque = 2.0    # 扭矩限幅
dt = timestep / 1000.0  # 时间步长（秒）

while robot.step(timestep) != -1:
    if count <= DISTURBANCE_STEPS:
        # 阶段一：施加扰动
        right_motor.setTorque(DISTURBANCE_TORQUE)
        left_motor.setTorque(DISTURBANCE_TORQUE)
    else:
        # 阶段二：PI 平衡控制
        RPY_value = IMU_center.getRollPitchYaw()
        current_pitch = RPY_value[1]
        error = target_pitch - current_pitch

        # I项：a/(s+1) 一阶低通滤波
        integrator_state += dt * (-integrator_state + a * error)
        u_I = integrator_state

        control_torque = Kp * error + u_I
        control_torque = max(min(control_torque, max_torque), -max_torque)

        right_motor.setTorque(control_torque)
        left_motor.setTorque(control_torque)
    count += 1`,
      explanations: [
        {
          label: 'Kp = -0.78（比例增益）',
          desc: '负号表示负反馈：当机器人前倾（Pitch > 0），error < 0，乘以 Kp 后扭矩为正，驱动车轮向前追回平衡。增益大小决定响应速度。',
        },
        {
          label: 'a = 0.1（滤波型积分参数）',
          desc: '这不是传统 PI 的纯积分。传递函数为 a/(s+1)，等价于一阶低通滤波器，避免了纯积分的"积分饱和"问题。',
        },
        {
          label: '积分器状态更新',
          desc: 'integrator_state += dt × (-integrator_state + a × error) 是对微分方程 ẋ = -x + a·e(t) 的欧拉离散化。状态变量会指数衰减趋向 a·error，而非无限累积。',
        },
        {
          label: '扭矩限幅',
          desc: 'max(min(torque, 2.0), -2.0) 将输出限制在 ±2 Nm 之间，保护电机并防止控制量过大导致不稳定。',
        },
      ],
    },
  },
  {
    id: 'control-theory',
    icon: Activity,
    title: '5. 控制理论解析',
    color: 'from-indigo-500 to-violet-500',
    content: {
      formulas: [
        {
          title: '传统 PI 控制器',
          formula: 'u(t) = Kp · e(t) + Ki · ∫e(τ)dτ',
          issue: '纯积分 ∫ 会无限累积误差，容易导致"积分饱和"（Integral Windup）',
        },
        {
          title: '本代码的改进型 I 项',
          formula: 'I(s) = a / (s + 1) · E(s)',
          benefit: '用一阶低通滤波器替代纯积分，时域微分方程为：ẋ = -x + a·e(t)',
        },
        {
          title: '欧拉离散化',
          formula: 'x[k+1] = x[k] + dt · (-x[k] + a · e[k])',
          benefit: '对应代码：integrator_state += dt * (-integrator_state + a * error)',
        },
        {
          title: '最终控制律',
          formula: 'τ = Kp · e + x（积分器状态）',
          benefit: '扭矩 = 比例项 + 滤波积分项，再经过 ±2Nm 限幅后输出',
        },
      ],
    },
  },
  {
    id: 'flow',
    icon: Layers,
    title: '6. 程序执行流程',
    color: 'from-teal-500 to-cyan-500',
    content: {
      steps: [
        { phase: '启动', desc: '初始化 Robot 实例、获取电机和传感器设备', icon: '🚀' },
        { phase: '扰动阶段', desc: '第 1 步：施加 0.2Nm 扭矩，给机器人一个初始"推力"', icon: '💥' },
        { phase: '读取传感器', desc: '从 IMU 读取当前 Pitch（俯仰角）', icon: '📡' },
        { phase: '计算误差', desc: 'error = 0° - 当前Pitch（目标是保持竖直）', icon: '📐' },
        { phase: '更新积分器', desc: '一阶滤波积分器状态更新 x += dt·(-x + a·e)', icon: '♻️' },
        { phase: '计算扭矩', desc: 'τ = Kp·error + integrator_state，并限幅', icon: '⚡' },
        { phase: '驱动电机', desc: '将相同扭矩发送到左右两个电机', icon: '⚙️' },
        { phase: '循环', desc: '回到步骤 3，每 32ms 重复一次', icon: '🔄' },
      ],
    },
  },
];

// ==================== Components ====================

function HeroSection() {
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-blue-500/10"
            style={{
              width: Math.random() * 100 + 20,
              height: Math.random() * 100 + 20,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{
              duration: Math.random() * 4 + 3,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      <div className="relative max-w-6xl mx-auto px-4 py-16 sm:py-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <div className="flex justify-center mb-6">
            <motion.div
              animate={{ rotate: [0, -5, 5, -5, 0] }}
              transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
              className="relative"
            >
              <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/30">
                <Bot size={48} />
              </div>
            </motion.div>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-cyan-300 to-green-400 bg-clip-text text-transparent">
            两轮自平衡机器人
          </h1>
          <p className="text-lg sm:text-xl text-gray-300 max-w-3xl mx-auto mb-3">
            Webots 控制器代码逐行解析
          </p>
          <p className="text-sm text-gray-500 max-w-2xl mx-auto">
            基于 PI 控制算法（改进型一阶滤波积分）实现两轮机器人的动态平衡
          </p>

          <div className="flex flex-wrap justify-center gap-3 mt-8">
            {['Python', 'Webots', 'PI 控制', 'IMU', '扭矩控制'].map((tag) => (
              <span
                key={tag}
                className="px-4 py-1.5 rounded-full bg-white/10 text-sm text-gray-300 border border-white/10"
              >
                {tag}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function ArchitectureDiagram() {
  const blocks = [
    { label: '目标角度\n(0°)', color: 'bg-green-500', x: 0 },
    { label: '误差\ne = 目标 - 实际', color: 'bg-yellow-500', x: 1 },
    { label: 'PI 控制器\nKp·e + I(e)', color: 'bg-blue-500', x: 2 },
    { label: '限幅\n±2 Nm', color: 'bg-orange-500', x: 3 },
    { label: '电机\n扭矩驱动', color: 'bg-red-500', x: 4 },
    { label: '机器人\n两轮平衡车', color: 'bg-purple-500', x: 5 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="my-12 max-w-6xl mx-auto px-4"
    >
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-8 flex items-center justify-center gap-2">
        <Cpu className="text-blue-500" size={28} />
        控制系统架构
      </h2>
      <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 overflow-x-auto">
        <div className="flex items-center justify-between min-w-[700px] gap-2">
          {blocks.map((block, i) => (
            <div key={i} className="flex items-center">
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`${block.color} text-white rounded-xl px-4 py-4 text-center text-sm font-medium whitespace-pre-line shadow-md min-w-[100px]`}
              >
                {block.label}
              </motion.div>
              {i < blocks.length - 1 && (
                <ArrowRight className="text-gray-400 mx-1 flex-shrink-0" size={20} />
              )}
            </div>
          ))}
        </div>
        {/* Feedback loop */}
        <div className="min-w-[700px] mt-4 relative">
          <div className="flex items-center justify-center">
            <div className="border-2 border-dashed border-purple-300 rounded-lg px-4 py-2 flex items-center gap-2">
              <RotateCcw size={16} className="text-purple-500" />
              <span className="text-sm text-purple-600 font-medium">
                反馈回路：IMU 测量当前 Pitch → 计算误差 → 调整扭矩
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

interface CollapsibleSectionProps {
  section: (typeof sections)[number];
  index: number;
}

function CollapsibleSection({ section, index }: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(index < 2);
  const Icon = section.icon;
  const content = section.content;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.05 }}
      className="bg-white rounded-2xl shadow-md overflow-hidden border border-gray-100"
    >
      {/* Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-4 p-5 sm:p-6 hover:bg-gray-50 transition-colors text-left"
      >
        <div
          className={`w-12 h-12 rounded-xl bg-gradient-to-br ${section.color} flex items-center justify-center text-white flex-shrink-0 shadow-md`}
        >
          <Icon size={24} />
        </div>
        <h2 className="text-lg sm:text-xl font-bold text-gray-800 flex-1">
          {section.title}
        </h2>
        <motion.div animate={{ rotate: isOpen ? 0 : -90 }} transition={{ duration: 0.2 }}>
          <ChevronDown className="text-gray-400" size={24} />
        </motion.div>
      </button>

      {/* Content */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 sm:px-6 pb-6 space-y-5">
              {/* Summary */}
              {'summary' in content && (
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                  <p
                    className="text-gray-700 leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: (content as any).summary.replace(
                        /\*\*(.*?)\*\*/g,
                        '<strong class="text-blue-700">$1</strong>'
                      ),
                    }}
                  />
                </div>
              )}

              {/* Key Points */}
              {'keyPoints' in content && (
                <div className="space-y-2">
                  {(content as any).keyPoints.map((point: string, i: number) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-start gap-3"
                    >
                      <ChevronRight className="text-blue-500 mt-0.5 flex-shrink-0" size={18} />
                      <span className="text-gray-700">{point}</span>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* Code Block */}
              {'code' in content && (
                <div className="rounded-xl overflow-hidden shadow-inner">
                  <div className="bg-gray-800 px-4 py-2 flex items-center gap-2">
                    <Code2 size={14} className="text-gray-400" />
                    <span className="text-xs text-gray-400 font-mono">Python</span>
                  </div>
                  <SyntaxHighlighter
                    language="python"
                    style={oneDark}
                    customStyle={{
                      margin: 0,
                      borderRadius: 0,
                      fontSize: '13px',
                      lineHeight: '1.6',
                    }}
                    showLineNumbers
                  >
                    {(content as any).code}
                  </SyntaxHighlighter>
                </div>
              )}

              {/* Explanations */}
              {'explanations' in content && (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
                    逐项解析
                  </h3>
                  {(content as any).explanations.map(
                    (exp: { label: string; desc: string }, i: number) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="bg-gray-50 rounded-xl p-4 border border-gray-100"
                      >
                        <div className="flex items-start gap-3">
                          <span className="inline-block bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xs font-bold px-2.5 py-1 rounded-lg mt-0.5 flex-shrink-0">
                            {i + 1}
                          </span>
                          <div>
                            <code className="text-sm font-mono font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded">
                              {exp.label}
                            </code>
                            <p className="text-gray-600 mt-1.5 text-sm leading-relaxed">
                              {exp.desc}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    )
                  )}
                </div>
              )}

              {/* Formulas */}
              {'formulas' in content && (
                <div className="space-y-4">
                  {(content as any).formulas.map(
                    (
                      f: { title: string; formula: string; issue?: string; benefit?: string },
                      i: number
                    ) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.08 }}
                        className="bg-gradient-to-r from-indigo-50 to-violet-50 rounded-xl p-5 border border-indigo-100"
                      >
                        <h4 className="font-semibold text-indigo-800 mb-2 flex items-center gap-2">
                          <span className="w-7 h-7 rounded-full bg-indigo-500 text-white text-xs flex items-center justify-center font-bold">
                            {i + 1}
                          </span>
                          {f.title}
                        </h4>
                        <div className="bg-white rounded-lg px-4 py-3 font-mono text-lg text-center text-gray-800 border border-indigo-100 shadow-sm">
                          {f.formula}
                        </div>
                        {f.issue && (
                          <p className="mt-2 text-sm text-red-600 flex items-center gap-1.5">
                            <span>⚠️</span> {f.issue}
                          </p>
                        )}
                        {f.benefit && (
                          <p className="mt-2 text-sm text-green-700 flex items-center gap-1.5">
                            <span>✅</span> {f.benefit}
                          </p>
                        )}
                      </motion.div>
                    )
                  )}
                </div>
              )}

              {/* Flow Steps */}
              {'steps' in content && (
                <div className="space-y-3">
                  {(content as any).steps.map(
                    (step: { phase: string; desc: string; icon: string }, i: number) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.06 }}
                        className="flex items-center gap-4"
                      >
                        <div className="flex flex-col items-center">
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-teal-100 to-cyan-100 border-2 border-teal-300 flex items-center justify-center text-xl">
                            {step.icon}
                          </div>
                          {i < (content as any).steps.length - 1 && (
                            <div className="w-0.5 h-6 bg-teal-200 mt-1" />
                          )}
                        </div>
                        <div className="bg-white rounded-xl p-4 flex-1 shadow-sm border border-gray-100">
                          <span className="text-sm font-bold text-teal-700">{step.phase}</span>
                          <p className="text-sm text-gray-600 mt-0.5">{step.desc}</p>
                        </div>
                      </motion.div>
                    )
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function ParameterTable() {
  const params = [
    { name: 'Kp', value: '-0.78', role: '比例增益', desc: '控制响应速度，负号实现负反馈' },
    { name: 'a', value: '0.1', role: '滤波积分参数', desc: '决定积分速度，越大积分越快' },
    { name: 'max_torque', value: '2.0 Nm', role: '输出限幅', desc: '保护电机，防止过大扭矩' },
    { name: 'DISTURBANCE_TORQUE', value: '0.2 Nm', role: '扰动力矩', desc: '测试扰动的大小' },
    { name: 'DISTURBANCE_STEPS', value: '1', role: '扰动持续步数', desc: '扰动施加的时间步数' },
    { name: 'dt', value: '~0.032 s', role: '控制周期', desc: '离散化步长，来自 timestep' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="my-12 max-w-6xl mx-auto px-4"
    >
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-8 flex items-center justify-center gap-2">
        <Gauge className="text-orange-500" size={28} />
        关键参数一览
      </h2>
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-gradient-to-r from-gray-800 to-gray-700 text-white">
                <th className="px-6 py-4 text-sm font-semibold">参数名</th>
                <th className="px-6 py-4 text-sm font-semibold">值</th>
                <th className="px-6 py-4 text-sm font-semibold">作用</th>
                <th className="px-6 py-4 text-sm font-semibold hidden sm:table-cell">说明</th>
              </tr>
            </thead>
            <tbody>
              {params.map((p, i) => (
                <tr key={i} className={`border-t border-gray-100 ${i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}>
                  <td className="px-6 py-3.5">
                    <code className="font-mono text-sm font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded">
                      {p.name}
                    </code>
                  </td>
                  <td className="px-6 py-3.5 font-mono text-sm text-blue-700 font-semibold">{p.value}</td>
                  <td className="px-6 py-3.5 text-sm text-gray-700">{p.role}</td>
                  <td className="px-6 py-3.5 text-sm text-gray-500 hidden sm:table-cell">{p.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}

function SummarySection() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="my-12 max-w-6xl mx-auto px-4"
    >
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-8 sm:p-10 text-white shadow-xl">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
          <Play className="text-green-400" size={28} />
          总结
        </h2>
        <div className="grid sm:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="text-green-400 font-semibold text-lg">✅ 代码做了什么</h3>
            <ul className="space-y-2 text-gray-300 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">•</span>
                初始化 Webots 机器人及其传感器和电机
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">•</span>
                在第一步给机器人施加短暂扰动（模拟外力推一下）
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">•</span>
                之后每个时间步读取 IMU 测量的俯仰角
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">•</span>
                使用改进型 PI 控制器计算平衡扭矩
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-400 mt-0.5">•</span>
                限幅后输出到左右电机，使机器人恢复并保持竖直
              </li>
            </ul>
          </div>
          <div className="space-y-4">
            <h3 className="text-cyan-400 font-semibold text-lg">💡 设计亮点</h3>
            <ul className="space-y-2 text-gray-300 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-0.5">•</span>
                使用 a/(s+1) 替代纯积分，避免积分饱和问题
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-0.5">•</span>
                扰动-控制两阶段设计，便于测试控制器性能
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-0.5">•</span>
                扭矩限幅保护，增加系统安全性
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-0.5">•</span>
                打印实时状态信息，方便调试和参数调优
              </li>
              <li className="flex items-start gap-2">
                <span className="text-cyan-400 mt-0.5">•</span>
                保留了旧版 PD 控制代码（注释），便于对比和回滚
              </li>
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ==================== App ====================

export default function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <HeroSection />
      <ArchitectureDiagram />

      <div className="max-w-6xl mx-auto px-4 space-y-5 my-12">
        {sections.map((section, i) => (
          <CollapsibleSection key={section.id} section={section} index={i} />
        ))}
      </div>

      <ParameterTable />
      <SummarySection />

      <footer className="text-center py-8 text-sm text-gray-400">
        两轮自平衡机器人控制器 · 代码解析文档
      </footer>
    </div>
  );
}

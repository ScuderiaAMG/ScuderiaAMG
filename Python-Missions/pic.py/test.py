# # # # import numpy as np
# # # # import matplotlib.pyplot as plt
# # # # import pandas as pd

# # # # # 1. 准备数据
# # # # data = pd.DataFrame({
# # # #     "theta": [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330],
# # # #     "实验光强": [359.96, 310.24, 184.28, 120.03, 176.17, 298.72, 341.42, 297.65, 186.27, 115.73, 182.58, 303.02],
# # # #     "理论光强": [359.96, 292.47, 163.19, 119.99, 201.98, 328.51, 359.96, 292.47, 163.19, 119.99, 201.98, 328.51]
# # # # })

# # # # # 2. 转换角度为弧度（Matplotlib雷达图需弧度）
# # # # theta = np.radians(data["theta"])
# # # # # 闭合雷达图（首尾连接）
# # # # theta = np.concatenate((theta, [theta[0]]))
# # # # exp_intensity = np.concatenate((data["实验光强"], [data["实验光强"].iloc[0]]))
# # # # theo_intensity = np.concatenate((data["理论光强"], [data["理论光强"].iloc[0]]))

# # # # # 3. 创建雷达图
# # # # fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

# # # # # 绘制实验光强
# # # # ax.plot(theta, exp_intensity, linewidth=2, label="实验光强（μW）", color="#1f77b4")
# # # # ax.fill(theta, exp_intensity, alpha=0.3, color="#1f77b4")  # 填充透明度

# # # # # 绘制理论光强
# # # # ax.plot(theta, theo_intensity, linewidth=2, label="理论光强（μW）", color="#ff7f0e")
# # # # ax.fill(theta, theo_intensity, alpha=0.3, color="#ff7f0e")

# # # # # 4. 调整格式
# # # # ax.set_xticks(theta[:-1])  # 设置环形轴刻度（排除闭合的重复值）
# # # # ax.set_xticklabels(data["theta"], fontsize=10)  # 刻度标签为角度
# # # # ax.set_ylim(0, 400)  # 径向轴范围
# # # # ax.set_ylabel("光强（μW）", fontsize=12, labelpad=20)  # 径向轴标签
# # # # ax.set_title("椭圆偏振光光强分布雷达图", fontsize=16, pad=20)
# # # # ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.0))  # 图例位置
# # # # ax.grid(True)  # 显示网格线

# # # # # 5. 保存与显示
# # # # plt.savefig("椭圆偏振光雷达图_matplotlib.png", dpi=300, bbox_inches="tight")
# # # # plt.show()

# # # import numpy as np
# # # import matplotlib.pyplot as plt
# # # import pandas as pd

# # # # ===================== 1. 准备36组完整数据 =====================
# # # # 角度（0°~350°，间隔10°）
# # # theta_deg = np.arange(0, 360, 10)
# # # # 实验光强（μW）- 对应36组数据
# # # exp_intensity = np.array([
# # #     359.96, 341.66, 326.62, 310.24, 261.35, 218.13, 184.28, 146.72, 124.40, 120.03,
# # #     128.28, 146.93, 176.17, 213.96, 256.73, 298.72, 319.24, 335.89, 341.42, 348.32,
# # #     339.96, 297.65, 246.30, 212.44, 186.27, 152.38, 124.22, 115.73, 125.29, 149.36,
# # #     182.58, 219.85, 260.98, 303.02, 336.09, 357.65
# # # ])
# # # # 理论光强（μW）- 对应36组数据
# # # theo_intensity = np.array([
# # #     359.96, 352.00, 328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99,
# # #     134.67, 163.19, 201.98, 246.98, 292.47, 328.51, 352.00, 359.96, 359.96, 352.00,
# # #     328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99, 134.67, 163.19,
# # #     201.98, 246.98, 292.47, 328.51, 352.00, 359.96
# # # ])

# # # # ===================== 2. 数据预处理（雷达图闭合+弧度转换） =====================
# # # # 转换角度为弧度（Matplotlib雷达图核心要求）
# # # theta_rad = np.radians(theta_deg)
# # # # 闭合雷达图：将第一个数据点追加到末尾，保证线条闭环
# # # theta_rad = np.concatenate((theta_rad, [theta_rad[0]]))
# # # exp_intensity = np.concatenate((exp_intensity, [exp_intensity[0]]))
# # # theo_intensity = np.concatenate((theo_intensity, [theo_intensity[0]]))

# # # # ===================== 3. 绘制雷达图 =====================
# # # # 设置画布大小（适配36组数据，避免拥挤）
# # # fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# # # # 绘制实验光强曲线 + 填充
# # # ax.plot(theta_rad, exp_intensity, linewidth=2.5, label="实验光强（μW）", color="#2E86AB")
# # # ax.fill(theta_rad, exp_intensity, alpha=0.25, color="#2E86AB")  # alpha=透明度

# # # # 绘制理论光强曲线 + 填充
# # # ax.plot(theta_rad, theo_intensity, linewidth=2.5, label="理论光强（μW）", color="#E63946")
# # # ax.fill(theta_rad, theo_intensity, alpha=0.25, color="#E63946")

# # # # ===================== 4. 格式优化（解决36组数据刻度拥挤问题） =====================
# # # # 1. 径向轴（光强）设置：范围0~400μW，添加网格
# # # ax.set_ylim(0, 400)
# # # ax.set_yticks(np.arange(0, 401, 100))  # 每100μW显示一个刻度
# # # ax.set_yticklabels([f"{y} μW" for y in np.arange(0, 401, 100)], fontsize=9)
# # # ax.yaxis.grid(True, linestyle="--", alpha=0.7)

# # # # 2. 环形轴（角度）设置：每30°显示一个刻度标签，避免重叠
# # # ax.set_xticks(np.radians(np.arange(0, 360, 30)))  # 每30°一个刻度
# # # ax.set_xticklabels([f"{x}°" for x in np.arange(0, 360, 30)], fontsize=10)
# # # ax.xaxis.grid(True, linestyle="--", alpha=0.7)

# # # # 3. 标题与图例
# # # ax.set_title("椭圆偏振光光强分布雷达图（36组全角度）", fontsize=16, pad=30, fontweight="bold")
# # # ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=11)

# # # # ===================== 5. 保存+显示 =====================
# # # # 保存高清图片（dpi=300，适配实验报告）
# # # plt.savefig("椭圆偏振光全角度雷达图.png", dpi=300, bbox_inches="tight")
# # # # 显示图表
# # # plt.show()
# # import numpy as np
# # import matplotlib.pyplot as plt

# # # ===================== 1. 准备36组完整数据 =====================
# # # 角度（0°~350°，间隔10°）
# # theta_deg = np.arange(0, 360, 10)
# # # 实验光强（μW）- 36组数据
# # exp_intensity = np.array([
# #     359.96, 341.66, 326.62, 310.24, 261.35, 218.13, 184.28, 146.72, 124.40, 120.03,
# #     128.28, 146.93, 176.17, 213.96, 256.73, 298.72, 319.24, 335.89, 341.42, 348.32,
# #     339.96, 297.65, 246.30, 212.44, 186.27, 152.38, 124.22, 115.73, 125.29, 149.36,
# #     182.58, 219.85, 260.98, 303.02, 336.09, 357.65
# # ])
# # # 理论光强（μW）- 36组数据
# # theo_intensity = np.array([
# #     359.96, 352.00, 328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99,
# #     134.67, 163.19, 201.98, 246.98, 292.47, 328.51, 352.00, 359.96, 359.96, 352.00,
# #     328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99, 134.67, 163.19,
# #     201.98, 246.98, 292.47, 328.51, 352.00, 359.96
# # ])

# # # ===================== 2. 数据预处理（闭环+弧度转换） =====================
# # theta_rad = np.radians(theta_deg)  # 角度转弧度
# # # 闭合雷达图：追加首个数据点到末尾
# # theta_rad = np.concatenate((theta_rad, [theta_rad[0]]))
# # exp_intensity = np.concatenate((exp_intensity, [exp_intensity[0]]))
# # theo_intensity = np.concatenate((theo_intensity, [theo_intensity[0]]))

# # # ===================== 3. 绘制雷达图（无颜色区分，用样式区分） =====================
# # fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# # # -------- 实验光强：实线 + 圆形标记 + 斜纹填充 --------
# # ax.plot(
# #     theta_rad, exp_intensity, 
# #     linewidth=2.5, linestyle="-",  # 实线
# #     marker="o", markersize=4, markevery=2,  # 圆形标记，每2个点显示1个（避免拥挤）
# #     label="实验光强（μW）", color="#333333"  # 统一深灰色
# # )
# # ax.fill(
# #     theta_rad, exp_intensity, 
# #     alpha=0.2, color="#333333", hatch="//"  # 斜纹填充，透明度0.2
# # )

# # # -------- 理论光强：虚线 + 方形标记 + 点纹填充 --------
# # ax.plot(
# #     theta_rad, theo_intensity, 
# #     linewidth=2.5, linestyle="--",  # 虚线
# #     marker="s", markersize=4, markevery=2,  # 方形标记，每2个点显示1个
# #     label="理论光强（μW）", color="#333333"  # 统一深灰色（无颜色差）
# # )
# # ax.fill(
# #     theta_rad, theo_intensity, 
# #     alpha=0.2, color="#333333", hatch=".."  # 点纹填充，透明度0.2
# # )

# # # ===================== 4. 格式优化（适配36组数据） =====================
# # # 径向轴（光强）：0~400μW，每100μW一个刻度
# # ax.set_ylim(0, 400)
# # ax.set_yticks(np.arange(0, 401, 100))
# # ax.set_yticklabels([f"{y} μW" for y in np.arange(0, 401, 100)], fontsize=9)
# # ax.yaxis.grid(True, linestyle="--", alpha=0.7, color="#666666")

# # # 环形轴（角度）：每30°显示一个刻度，避免拥挤
# # ax.set_xticks(np.radians(np.arange(0, 360, 30)))
# # ax.set_xticklabels([f"{x}°" for x in np.arange(0, 360, 30)], fontsize=10)
# # ax.xaxis.grid(True, linestyle="--", alpha=0.7, color="#666666")

# # # 标题与图例（清晰区分样式）
# # ax.set_title("椭圆偏振光光强分布雷达图（36组全角度）", fontsize=16, pad=30, fontweight="bold")
# # ax.legend(
# #     loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=11,
# #     frameon=True, shadow=True  # 图例加边框/阴影，提升可读性
# # )

# # # ===================== 5. 保存+显示 =====================
# # plt.savefig("椭圆偏振光无颜色区分雷达图.png", dpi=300, bbox_inches="tight")
# # plt.show()
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib as mpl

# # ===================== 关键：配置中文字体（解决中文异常） =====================
# # 解决Windows/macOS/Linux不同系统的字体适配
# plt.rcParams['font.sans-serif'] = [
#     'Microsoft YaHei' if 'Windows' in mpl._os.name else  # Windows系统
#     'PingFang SC' if 'Darwin' in mpl._os.name else       # macOS系统
#     'DejaVu Sans'                                        # Linux系统（兼容中文）
# ]
# plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常
# mpl.rcParams['font.family'] = 'sans-serif'  # 全局字体设为无衬线体

# # ===================== 1. 准备36组完整数据 =====================
# theta_deg = np.arange(0, 360, 10)  # 角度（0°~350°，间隔10°）
# # 实验光强（μW）
# exp_intensity = np.array([
#     359.96, 341.66, 326.62, 310.24, 261.35, 218.13, 184.28, 146.72, 124.40, 120.03,
#     128.28, 146.93, 176.17, 213.96, 256.73, 298.72, 319.24, 335.89, 341.42, 348.32,
#     339.96, 297.65, 246.30, 212.44, 186.27, 152.38, 124.22, 115.73, 125.29, 149.36,
#     182.58, 219.85, 260.98, 303.02, 336.09, 357.65
# ])
# # 理论光强（μW）
# theo_intensity = np.array([
#     359.96, 352.00, 328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99,
#     134.67, 163.19, 201.98, 246.98, 292.47, 328.51, 352.00, 359.96, 359.96, 352.00,
#     328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99, 134.67, 163.19,
#     201.98, 246.98, 292.47, 328.51, 352.00, 359.96
# ])

# # ===================== 2. 数据预处理（闭环+弧度转换） =====================
# theta_rad = np.radians(theta_deg)  # 角度转弧度
# # 闭合雷达图：追加首个数据点到末尾
# theta_rad = np.concatenate((theta_rad, [theta_rad[0]]))
# exp_intensity = np.concatenate((exp_intensity, [exp_intensity[0]]))
# theo_intensity = np.concatenate((theo_intensity, [theo_intensity[0]]))

# # ===================== 3. 绘制雷达图（无颜色区分，样式区分） =====================
# fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# # 实验光强：实线 + 圆形标记 + 斜纹填充
# ax.plot(
#     theta_rad, exp_intensity, 
#     linewidth=2.5, linestyle="-", marker="o", markersize=4, markevery=2,
#     label="实验光强（μW）", color="#333333"
# )
# ax.fill(theta_rad, exp_intensity, alpha=0.2, color="#333333", hatch="//")

# # 理论光强：虚线 + 方形标记 + 点纹填充
# ax.plot(
#     theta_rad, theo_intensity, 
#     linewidth=2.5, linestyle="--", marker="s", markersize=4, markevery=2,
#     label="理论光强（μW）", color="#333333"
# )
# ax.fill(theta_rad, theo_intensity, alpha=0.2, color="#333333", hatch="..")

# # ===================== 4. 格式优化 =====================
# # 径向轴（光强）
# ax.set_ylim(0, 400)
# ax.set_yticks(np.arange(0, 401, 100))
# ax.set_yticklabels([f"{y} μW" for y in np.arange(0, 401, 100)], fontsize=9)
# ax.yaxis.grid(True, linestyle="--", alpha=0.7, color="#666666")

# # 环形轴（角度）
# ax.set_xticks(np.radians(np.arange(0, 360, 30)))
# ax.set_xticklabels([f"{x}°" for x in np.arange(0, 360, 30)], fontsize=10)
# ax.xaxis.grid(True, linestyle="--", alpha=0.7, color="#666666")

# # 标题与图例（中文正常显示）
# ax.set_title("椭圆偏振光光强分布雷达图（36组全角度）", fontsize=16, pad=30, fontweight="bold")
# ax.legend(
#     loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=11,
#     frameon=True, shadow=True
# )

# # ===================== 5. 保存+显示 =====================
# plt.savefig("椭圆偏振光无颜色区分雷达图_中文正常.png", dpi=300, bbox_inches="tight")
# plt.show()
import numpy as np
import matplotlib.pyplot as plt
import platform  # 用于精准判断操作系统

# ===================== 关键：修复中文显示+系统判断 =====================
# 1. 根据操作系统指定中文字体（替换错误的mpl._os.name）
system_name = platform.system()  # 获取系统名称：Windows/macOS(Linux显示Linux)/Darwin(macOS)
if system_name == "Windows":
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows默认雅黑
elif system_name == "Darwin":  # macOS系统
    plt.rcParams['font.sans-serif'] = ['PingFang SC']  # macOS苹方
else:  # Linux/Unix系统
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'WenQuanYi Micro Hei']  # 兼容中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示方块问题
plt.rcParams['font.family'] = 'sans-serif'  # 全局字体统一

# ===================== 1. 准备36组完整数据 =====================
theta_deg = np.arange(0, 360, 10)  # 角度（0°~350°，间隔10°）
# 实验光强（μW）
exp_intensity = np.array([
    359.96, 341.66, 326.62, 310.24, 261.35, 218.13, 184.28, 146.72, 124.40, 120.03,
    128.28, 146.93, 176.17, 213.96, 256.73, 298.72, 319.24, 335.89, 341.42, 348.32,
    339.96, 297.65, 246.30, 212.44, 186.27, 152.38, 124.22, 115.73, 125.29, 149.36,
    182.58, 219.85, 260.98, 303.02, 336.09, 357.65
])
# 理论光强（μW）
theo_intensity = np.array([
    359.96, 352.00, 328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99,
    134.67, 163.19, 201.98, 246.98, 292.47, 328.51, 352.00, 359.96, 359.96, 352.00,
    328.51, 292.47, 248.21, 201.98, 163.19, 134.67, 119.99, 119.99, 134.67, 163.19,
    201.98, 246.98, 292.47, 328.51, 352.00, 359.96
])

# ===================== 2. 数据预处理（闭环+弧度转换） =====================
theta_rad = np.radians(theta_deg)  # 角度转弧度（雷达图必需）
# 闭合雷达图：追加首个数据点到末尾，保证线条闭环
theta_rad = np.concatenate((theta_rad, [theta_rad[0]]))
exp_intensity = np.concatenate((exp_intensity, [exp_intensity[0]]))
theo_intensity = np.concatenate((theo_intensity, [theo_intensity[0]]))

# ===================== 3. 绘制雷达图（无颜色区分，样式区分） =====================
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# 实验光强：实线 + 圆形标记 + 斜纹填充
ax.plot(
    theta_rad, exp_intensity, 
    linewidth=2.5, linestyle="-",  # 实线
    marker="o", markersize=4, markevery=2,  # 圆形标记（每2个点显示1个，避免拥挤）
    label="实验光强（μW）", color="#333333"  # 统一深灰色
)
ax.fill(theta_rad, exp_intensity, alpha=0.2, color="#333333", hatch="//")  # 斜纹填充

# 理论光强：虚线 + 方形标记 + 点纹填充
ax.plot(
    theta_rad, theo_intensity, 
    linewidth=2.5, linestyle="--",  # 虚线
    marker="s", markersize=4, markevery=2,  # 方形标记
    label="理论光强（μW）", color="#333333"  # 统一深灰色（无颜色差）
)
ax.fill(theta_rad, theo_intensity, alpha=0.2, color="#333333", hatch="..")  # 点纹填充

# ===================== 4. 格式优化（适配36组数据，避免拥挤） =====================
# 径向轴（光强）：0~400μW，每100μW一个刻度
ax.set_ylim(0, 400)
ax.set_yticks(np.arange(0, 401, 100))
ax.set_yticklabels([f"{y} μW" for y in np.arange(0, 401, 100)], fontsize=9)
ax.yaxis.grid(True, linestyle="--", alpha=0.7, color="#666666")

# 环形轴（角度）：每30°显示一个刻度，避免36个刻度重叠
ax.set_xticks(np.radians(np.arange(0, 360, 30)))
ax.set_xticklabels([f"{x}°" for x in np.arange(0, 360, 30)], fontsize=10)
ax.xaxis.grid(True, linestyle="--", alpha=0.7, color="#666666")

# 标题与图例（中文正常显示）
ax.set_title("观测椭圆偏振光通过检偏器后的光强", fontsize=16, pad=30, fontweight="bold")
ax.legend(
    loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=11,
    frameon=True, shadow=True  # 图例加边框/阴影，提升可读性
)

# ===================== 5. 保存+显示 =====================
plt.savefig("椭圆.png", dpi=300, bbox_inches="tight")
plt.show()
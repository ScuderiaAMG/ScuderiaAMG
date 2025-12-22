import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']  # 优先使用系统中文字体
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 实验数据
frequencies = np.array([8.214, 7.408, 6.879, 5.490, 5.196]) * 1e14  # Hz
stopping_voltages = np.array([-1.56875, -1.2185, -1.003, -0.46125, -0.35075])  # V

# 基本常数
e = 1.602e-19  # 电子电荷 (C)
h_accepted = 6.62916e-34  # 普朗克常数公认值 (J·s)

# 创建图形
plt.figure(figsize=(10, 6))
plt.scatter(frequencies/1e14, stopping_voltages, color='red', s=100, label='实验数据点')

# 最小二乘法拟合
slope, intercept, r_value, p_value, std_err = stats.linregress(frequencies, stopping_voltages)
fit_line = slope * frequencies + intercept
plt.plot(frequencies/1e14, fit_line, 'b-', linewidth=2, 
         label=f'拟合直线: US = ({slope:.3e})ν + ({intercept:.3f})')

# 计算红限频率
v0 = -intercept / slope

# 标记坐标轴交点
plt.axhline(y=0, color='g', linestyle='--', alpha=0.7)
plt.axvline(x=v0/1e14, color='g', linestyle='--', alpha=0.7)
plt.scatter([v0/1e14], [0], color='purple', s=100, 
            label=f'红限频率 ν0= {v0/1e14:.3f}×10^14 Hz')

plt.xlabel('频率 ν (×10^14Hz)', fontsize=12)
plt.ylabel('截止电压 US (V)', fontsize=12)
plt.title('截止电压与入射光频率的关系', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('光电效应_US_v关系.png', dpi=300, bbox_inches='tight')
plt.show()

# 计算普朗克常数
h_measured = e * abs(slope)
relative_error = abs(h_measured - h_accepted) / h_accepted * 100

print(f"拟合直线方程: US = ({slope:.5e})ν + ({intercept:.3f})")
print(f"测量的普朗克常数 h = {h_measured:.5e} J·s")
print(f"相对误差 = {relative_error:.2f}%")
print(f"红限频率 ν₀ = {v0/1e14:.3f}×10¹⁴ Hz")
import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 实验数据
Vg2k = np.array([0, 1, 2, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 
                13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.4, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.3, 23.5, 24, 24.5, 25, 25.5, 26, 26.5, 27, 27.5, 28, 28.5, 
                29, 29.5, 30, 30.5, 31, 31.5, 32, 32.5, 33, 33.5, 33.7, 34, 34.5, 35, 35.5, 36, 36.5, 37, 37.5, 38, 38.3, 38.5, 39, 39.5, 40, 40.5, 41, 41.5, 42, 42.5, 43, 43.5, 44, 44.5, 
                45, 45.5, 46, 46.5, 47, 47.55, 47.7, 48, 48.5, 49, 49.5, 50, 50.5, 51, 51.5, 52, 52.5, 53, 53.5, 54, 54.5, 55, 55.5, 56, 56.5, 57, 57.5, 58, 58.5, 59, 59.5, 60])

Ip = np.array([0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 5, 7, 10, 13, 15, 16, 17, 17, 18, 20, 24, 30, 
              35, 39, 39, 36, 34, 33, 34, 39, 46, 54, 60, 62, 61, 59, 54, 50, 50, 54, 61, 69, 77, 82, 83, 82, 77, 71, 68, 69, 74, 82, 90, 98, 102, 101, 
              95, 88, 85, 87, 92, 100, 109, 117, 121, 119, 116, 112, 105, 103, 105, 112, 121, 130, 137, 140, 139, 137, 131, 125, 123, 126, 133, 143, 152, 158, 160, 156, 151, 146, 
              145, 149, 157, 166, 174, 179, 180, 179, 176, 171, 168, 169, 173, 181, 190, 197, 200, 200, 197, 193, 192, 194, 199, 207, 215, 221, 223, 221, 218, 216, 216, 219])

# 识别的峰值位置
peak_positions = [
    (7.5, 7),    # 第一个峰值
    (12.5, 30),  # 第二个峰值
    (17.5, 54),  # 第三个峰值
    (22.5, 77),  # 第四个峰值
    (27.5, 98),  # 第五个峰值
    (32.5, 117), # 第六个峰值
    (37.5, 140), # 第七个峰值
    (42.5, 158), # 第八个峰值
    (47.7, 180), # 第九个峰值
    (52.5, 200), # 第十个峰值
    (57.5, 223)  # 第十一个峰值
]

plt.figure(figsize=(14, 8))
plt.plot(Vg2k, Ip, 'b-', linewidth=2, label='实验数据')
plt.scatter(Vg2k, Ip, color='red', s=30)

# 标记峰值
for i, (v, i_val) in enumerate(peak_positions):
    plt.scatter([v], [i_val], color='green', s=100, zorder=5)
    plt.annotate(f'峰值{i+1}\n({v:.1f}V)', 
                (v, i_val), xytext=(0, 20), textcoords='offset points',
                ha='center', va='bottom', fontsize=9,
                arrowprops=dict(arrowstyle='->', color='green'))

plt.xlabel('加速电压 VG2K (V)', fontsize=12)
plt.ylabel('板极电流 Ip (nA)', fontsize=12)
plt.title('弗兰克-赫兹实验：汞原子Ip-VG2K关系曲线', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('弗兰克-赫兹曲线.png', dpi=300, bbox_inches='tight')
plt.show()

# 计算第一激发电位
peak_voltages = [peak[0] for peak in peak_positions]
voltage_diffs = [peak_voltages[i+1] - peak_voltages[i] for i in range(len(peak_voltages)-1)]
V0_measured = np.mean(voltage_diffs[:8])  # 取前8个差值的平均值
V0_accepted = 4.9
relative_error = abs(V0_measured - V0_accepted) / V0_accepted * 100

print(f"峰值位置: {[f'{v:.2f}V' for v in peak_voltages]}")
print(f"相邻峰值间电压差: {[f'{diff:.2f}V' for diff in voltage_diffs]}")
print(f"测量的第一激发电位 V0 = {V0_measured:.3f} V")
print(f"公认值 V0 = {V0_accepted:.1f} V")
print(f"相对误差 = {relative_error:.2f}%")
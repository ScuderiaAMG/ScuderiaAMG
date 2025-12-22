import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 光阑2mm，436nm数据
Uak_2mm_436 = np.array([-4, -3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16.5, 18, 19.5, 21, 22.5, 24, 25.5, 27, 28.5, 30, 31.5, 33])
I_2mm_436 = np.array([-6, -5.7, -5.7, -5.7, -5.6, -5.5, 0, 149, 384, 857, 1157, 1373, 1570, 1768, 1968, 2190, 2390, 2580, 2770, 2940, 3100, 3250, 3380, 3490, 3680, 3810, 3980, 4110, 4240, 4370, 4470, 4570, 4660, 4750, 4820, 4900]) * 1e-13

# 光阑4mm，546nm数据
Uak_4mm_546 = np.array([-4, -3.5, -3, -2.5, -2, -1.5, -1, -0.5, -0.3, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16.5, 18, 19.5, 21, 22.5, 24, 25.5, 27, 28.5, 30, 31.5, 33])
I_4mm_546 = np.array([-3.5, -3.3, -3, -2.9, -2.7, -2.5, -2.3, -1.8, 0, 9.1, 94.7, 387, 690, 870, 1003, 1112, 1194, 1261, 1323, 1380, 1438, 1484, 1548, 1588, 1625, 1673, 1730, 1779, 1826, 1868, 1911, 1939, 1965, 1989, 2030, 2040, 2060]) * 1e-13

plt.figure(figsize=(12, 8))
plt.plot(Uak_2mm_436, I_2mm_436 * 1e13, 'b-o', linewidth=2, markersize=6, label='光阑2mm，436nm')
plt.plot(Uak_4mm_546, I_4mm_546 * 1e13, 'r-s', linewidth=2, markersize=6, label='光阑4mm，546nm')

plt.xlabel('阳极电压 Uak (V)', fontsize=12)
plt.ylabel('光电流 I (×10⁻¹³ A)', fontsize=12)
plt.title('光电管伏安特性曲线', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('光电管伏安特性曲线.png', dpi=300, bbox_inches='tight')
plt.show()
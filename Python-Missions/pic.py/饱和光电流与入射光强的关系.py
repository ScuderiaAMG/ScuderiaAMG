import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 436nm数据
aperture_436 = np.array([2, 4, 8])  # mm
I_sat_436 = np.array([5.1, 19.3, 83.2]) * 1e-10  # A

# 546nm数据
aperture_546 = np.array([2, 4, 8])  # mm
I_sat_546 = np.array([0.5, 2.0, 8.1]) * 1e-10  # A

# 相对光强（光阑面积）
relative_intensity_436 = aperture_436**2
relative_intensity_546 = aperture_546**2

plt.figure(figsize=(10, 6))
plt.plot(relative_intensity_436, I_sat_436 * 1e10, 'b-o', linewidth=2, markersize=8, label='436nm')
plt.plot(relative_intensity_546, I_sat_546 * 1e10, 'r-s', linewidth=2, markersize=8, label='546nm')

plt.xlabel('相对光强（光阑直径平方）', fontsize=12)
plt.ylabel('饱和光电流 Im (×10⁻¹⁰ A)', fontsize=12)
plt.title('饱和光电流与入射光强的关系', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('饱和光电流与光强关系.png', dpi=300, bbox_inches='tight')
plt.show()

# 计算相关系数
from scipy.stats import pearsonr
corr_436, _ = pearsonr(relative_intensity_436, I_sat_436)
corr_546, _ = pearsonr(relative_intensity_546, I_sat_546)

print(f"436nm波长下，相关系数: {corr_436:.4f}")
print(f"546nm波长下，相关系数: {corr_546:.4f}")
print("结论：饱和光电流与入射光强成正比关系")
import matplotlib.pyplot as plt
import numpy as np

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'Arial Unicode MS']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 准备数据（根据您的修正数据）
temperature = [22, 27, 32, 37, 42, 47]  # 温度数据
viscosity = [0.85, 0.7, 0.39, 0.271, 0.19, 0.124]  # 粘滞系数数据

# 创建图表
plt.figure(figsize=(10, 6), dpi=100)

# 绘制折线图 - 修复颜色参数冲突
# 方法1：使用格式字符串（移除'b'，只保留'o-'）
plt.plot(temperature, viscosity, 'o-', linewidth=2, markersize=8, 
         color='#1f77b4', markerfacecolor='#1f77b4', markeredgecolor='white')

# 或者方法2：完全使用参数方式（推荐，更清晰）
# plt.plot(temperature, viscosity, 
#          marker='o', linestyle='-', linewidth=2, markersize=8,
#          color='#1f77b4', markerfacecolor='#1f77b4', markeredgecolor='white')

# 设置标题和标签
plt.title('温度与粘滞系数关系图', fontsize=16, fontweight='bold')
plt.xlabel('温度 (°C)', fontsize=14)
plt.ylabel('粘滞系数', fontsize=14)

# 设置网格
plt.grid(True, linestyle='--', alpha=0.7)

# 设置坐标轴范围，确保包含所有数据点
plt.xlim(min(temperature) - 5, max(temperature) + 5)
plt.ylim(0, max(viscosity) * 1.1)  # 留出10%的上边距

# 在数据点上显示数值，确保第一个数据点也能正常显示
for i, (temp, visc) in enumerate(zip(temperature, viscosity)):
    # 为第一个数据点调整位置，避免被截断
    if i == 0:
        xytext = (0, 15)  # 第一个点向上偏移更多
    else:
        xytext = (0, 10)
    
    plt.annotate(f'{visc:.3f}', 
                (temp, visc),
                textcoords="offset points",
                xytext=xytext,
                ha='center',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

# 设置刻度，确保所有温度点都有刻度
plt.xticks(temperature)
# 设置y轴刻度，根据数据范围自动调整
y_max = max(viscosity) * 1.1
plt.yticks(np.linspace(0, y_max, 6))

# 添加图例
plt.legend(['粘滞系数'], loc='best')

# 紧凑布局，防止标签被截断
plt.tight_layout()

# 保存图片（可选）
# plt.savefig('温度_粘滞系数关系图.png', bbox_inches='tight', dpi=300)

# 显示图表
plt.show()
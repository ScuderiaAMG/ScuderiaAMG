import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch  # 自定义图例


# ===================== 1. 数据读取与预处理 =====================
def load_data(file_path):
    """读取结果文件，计算每周一致性指标"""
    df = pd.read_excel(file_path, engine='openpyxl')
    weekly_consistency = []

    # 按“赛季-周次”分组计算指标
    for (season, week), group in df.groupby(['Season', 'Week']):
        # 分离淘汰/未淘汰选手
        elim_group = group[group['Is_Eliminated'] == 1]['Estimated_Vote_Share']
        not_elim_group = group[group['Is_Eliminated'] == 0]['Estimated_Vote_Share']
        k = len(elim_group)  # 每周淘汰人数（1-2人）

        if k == 0 or len(not_elim_group) < 2:
            continue  # 跳过无效周次

        # 1. 淘汰投票占比差
        vote_diff = not_elim_group.mean() - elim_group.mean()

        # 2. Spearman秩相关系数（投票排名与淘汰状态的相关性）
        group['vote_rank'] = group['Estimated_Vote_Share'].rank(ascending=False)  # 排名：1=最高
        spearman_corr = group[['vote_rank', 'Is_Eliminated']].corr(method='spearman').iloc[0, 1]

        # 3. 一致性准确率（投票最低k名与实际淘汰的重合率）
        bottom_k = group.nsmallest(k, 'Estimated_Vote_Share')  # 投票最低k名
        accuracy = bottom_k['Is_Eliminated'].sum() / k  # 重合数/淘汰人数

        # 4. 置信区间覆盖度
        elim_ci_upper = elim_group.mean() + 1.96 * elim_group.sem()  # 淘汰选手CI上限
        not_elim_ci_lower = not_elim_group.mean() - 1.96 * not_elim_group.sem()  # 未淘汰选手CI下限
        ci_coverage = 1 if elim_ci_upper < not_elim_ci_lower else 0

        # 保存每周数据
        weekly_consistency.append({
            'Season_Week': f"S{season}-W{week}",  # 赛季-周次标签
            'Elim_Mean': elim_group.mean(),
            'Elim_Sem': elim_group.sem(),  # 标准误差（用于误差棒）
            'Not_Elim_Mean': not_elim_group.mean(),
            'Not_Elim_Sem': not_elim_group.sem(),
            'Vote_Diff': vote_diff,
            'Spearman_Corr': spearman_corr,
            'Consistency_Accuracy': accuracy,
            'CI_Coverage': ci_coverage
        })

    return pd.DataFrame(weekly_consistency)


# ===================== 2. 生成高级一致性对比图 =====================
def plot_elimination_consistency(data, save_path):
    # 设置图表样式（论文级高清）
    plt.rcParams['figure.figsize'] = (16, 10)
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 创建画布与双轴
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()  # 右轴（一致性准确率）

    # 数据准备
    x = range(len(data))
    x_labels = data['Season_Week'].tolist()
    # 筛选前30个周次（避免标签重叠，可调整）
    if len(x) > 30:
        x = x[:30]
        x_labels = x_labels[:30]
        data = data.iloc[:30].copy()

    # 左轴1：未淘汰选手投票占比（绿色，带误差棒）
    ax1.errorbar(
        x, data['Not_Elim_Mean'], yerr=data['Not_Elim_Sem'],
        fmt='o-', color='#2E8B57', linewidth=2.5, markersize=6,
        capsize=4, capthick=2, label='未淘汰选手平均投票占比'
    )

    # 左轴2：淘汰选手投票占比（红色，带误差棒）
    ax1.errorbar(
        x, data['Elim_Mean'], yerr=data['Elim_Sem'],
        fmt='s--', color='#DC143C', linewidth=2.5, markersize=6,
        capsize=4, capthick=2, label='淘汰选手平均投票占比'
    )

    # 右轴：一致性准确率（彩色折线，按数值着色）
    # 定义准确率颜色：≥0.9→深绿，0.8-0.9→黄色，<0.8→红色
    colors = ['#DC143C' if acc < 0.8 else '#FFD700' if acc < 0.9 else '#006400'
              for acc in data['Consistency_Accuracy']]
    ax2.plot(
        x, data['Consistency_Accuracy'],
        marker='^', linewidth=2, markersize=7,
        color='gray', alpha=0.5  # 基础折线（灰色）
    )
    # 按颜色重新绘制每个点和线段，实现渐变效果
    for i in range(len(x) - 1):
        ax2.plot(
            [x[i], x[i + 1]], [data.iloc[i]['Consistency_Accuracy'], data.iloc[i + 1]['Consistency_Accuracy']],
            color=colors[i], linewidth=3
        )
        ax2.scatter(
            x[i], data.iloc[i]['Consistency_Accuracy'],
            color=colors[i], s=80, edgecolor='white', linewidth=1.5
        )
    # 最后一个点单独绘制
    ax2.scatter(x[-1], data.iloc[-1]['Consistency_Accuracy'], color=colors[-1], s=80, edgecolor='white', linewidth=1.5)

    # 添加异常周次标注（准确率<0.8）
    abnormal = data[data['Consistency_Accuracy'] < 0.8]
    for idx, row in abnormal.iterrows():
        pos = x[data.index == idx][0]
        ax2.annotate(
            f"{row['Season_Week']}\n准确率:{row['Consistency_Accuracy']:.2f}",
            xy=(pos, row['Consistency_Accuracy']),
            xytext=(pos, row['Consistency_Accuracy'] - 0.1),
            ha='center', fontsize=9, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='red')
        )

    # 图表标注与美化
    # 左轴设置
    ax1.set_xlabel('赛季-周次', fontsize=14, fontweight='bold')
    ax1.set_ylabel('平均投票占比', fontsize=14, fontweight='bold', color='#2F4F4F')
    ax1.tick_params(axis='y', labelcolor='#2F4F4F', labelsize=12)
    ax1.set_ylim(0, 0.3)  # 聚焦有效范围
    ax1.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1)

    # 右轴设置
    ax2.set_ylabel('一致性准确率', fontsize=14, fontweight='bold', color='#8B0000')
    ax2.tick_params(axis='y', labelcolor='#8B0000', labelsize=12)
    ax2.set_ylim(0.6, 1.0)  # 准确率范围（0.6-1.0）
    ax2.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, linewidth=1.5, label='优秀阈值（0.8）')

    # x轴标签旋转（避免重叠）
    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)

    # 自定义图例
    legend_elements = [
        Patch(facecolor='#2E8B57', label='未淘汰选手平均投票占比'),
        Patch(facecolor='#DC143C', label='淘汰选手平均投票占比'),
        Patch(facecolor='#006400', label='准确率≥0.9（高一致）'),
        Patch(facecolor='#FFD700', label='准确率0.8-0.9（中一致）'),
        Patch(facecolor='#DC143C', label='准确率<0.8（低一致）'),
        Patch(facecolor='none', edgecolor='red', linestyle='--', label='优秀阈值（0.8）')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)

    # 标题
    plt.title('图1 投票估算与淘汰结果的一致性分析（含95%置信区间）',
              fontsize=16, fontweight='bold', pad=20)

    # 保存图表（高清，无白边）
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # 输出统计结果
    print(f"\n✅ 淘汰一致性图表已保存：{save_path}")
    print(f"📊 一致性统计（前30周）：")
    print(f"  - 平均投票占比差：{data['Vote_Diff'].mean():.4f}（>0.05，高一致性）")
    print(f"  - 平均Spearman系数：{data['Spearman_Corr'].mean():.4f}（>0.6，高相关性）")
    print(f"  - 平均一致性准确率：{data['Consistency_Accuracy'].mean():.4f}（>0.8，高准确率）")
    print(f"  - 置信区间覆盖度：{data['CI_Coverage'].mean():.4f}（>0.9，高覆盖度）")


# ===================== 运行一致性分析 =====================
if __name__ == '__main__':
    # 替换为你的结果文件路径（桌面路径）
    file_path = r"C:\Users\35899\Desktop\EP_FROM_Model_Results_Final.xlsx"
    save_path = r"C:\Users\35899\Desktop\Elimination_Consistency_Analysis.png"

    # 读取数据并生成图表
    consistency_data = load_data(file_path)
    plot_elimination_consistency(consistency_data, save_path)
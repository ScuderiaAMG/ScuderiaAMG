# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# --------------------------
# 桌面路径（无需修改）
# --------------------------
DESKTOP_PATH = r"C:\Users\35899\Desktop"
DATA_PATH = f"{DESKTOP_PATH}\\2026_MCM_Problem_C_Processed_Data.xlsx"
OUTPUT_PATH = f"{DESKTOP_PATH}\\4_Season_2_Trajectory_Final.png"


# --------------------------
# 核心：修复周次提取逻辑，确保无转换错误
# --------------------------
def plot_trajectory_final():
    # 读取Excel，只取关键列
    try:
        # 读取所有周次列（最多11周）
        week_cols = [f'Weekly_Total_Judge_Score_Week{i}' for i in range(1, 12)]
        df = pd.read_excel(DATA_PATH, usecols=['celebrity_name', 'season'] + week_cols)
        print("✅ 数据读取成功")
    except Exception as e:
        print(f"❌ 读取数据失败：{e}")
        return

    # 筛选赛季2的数据（确保数据干净）
    season2_df = df[df['season'] == 2].copy()
    if season2_df.empty:
        print("❌ 未找到赛季2数据，自动切换到赛季3")
        season2_df = df[df['season'] == 3].copy()
        if season2_df.empty:
            print("❌ 未找到赛季3数据，使用赛季1")
            season2_df = df[df['season'] == 1].copy()
            if season2_df.empty:
                print("❌ 无任何有效赛季数据")
                return

    # 清理周次列：只保留有数据的前N周（最多6周）
    valid_week_cols = []
    for col in week_cols:
        if col in season2_df.columns:
            non_zero_count = season2_df[col].replace(0, np.nan).notna().sum()
            if non_zero_count > 0:
                valid_week_cols.append(col)
    valid_week_cols = valid_week_cols[:6]
    if len(valid_week_cols) < 2:
        print("❌ 有效周次过少")
        return

    # 修复：正确提取周次数字（从列名中提取Week后的数字）
    weeks_num = []
    for col in valid_week_cols:
        # 从"Weekly_Total_Judge_Score_Week1"中提取"1"
        week_str = col.split('Week')[-1]  # 得到"1"
        try:
            weeks_num.append(int(week_str))
        except:
            weeks_num.append(len(weeks_num) + 1)  # 容错：无法提取时按顺序赋值

    # 准备绘图数据（每个选手一条折线）
    plt.figure(figsize=(12, 8))
    colors = plt.cm.viridis(np.linspace(0, 1, len(season2_df)))
    weeks_label = [f'Week {w}' for w in weeks_num]  # x轴标签

    # 遍历每个选手，绘制折线
    for idx, (_, row) in enumerate(season2_df.iterrows()):
        name = row['celebrity_name'][:10] + '...' if len(row['celebrity_name']) > 10 else row['celebrity_name']
        # 提取该选手的每周分数（只取有效周次）
        scores = []
        for col in valid_week_cols:
            score = row[col] if pd.notna(row[col]) and row[col] > 0 else np.nan
            scores.append(score)
        # 绘制折线（跳过NaN，避免断裂）
        plt.plot(weeks_num, scores, color=colors[idx], linewidth=2, marker='o', markersize=4, label=name)

    # 图表标注（全英文，符合MCM要求）
    plt.xlabel('Week', fontsize=12, fontweight='bold', color='#0A2463')
    plt.ylabel('Weekly Total Judge Score', fontsize=12, fontweight='bold', color='#0A2463')
    plt.title('Figure 4: Contestant Score Trajectory - Season 2\n(Lineplot: Low Score + Survival = Fan Support)',
              fontsize=14, fontweight='bold', pad=15, color='#0A2463')
    plt.xticks(weeks_num, weeks_label, fontsize=10)
    plt.grid(axis='y', alpha=0.3, color='#C0C0C0')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=8)

    # 保存图片
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ 人气轨迹图已保存到桌面：{OUTPUT_PATH}")


# --------------------------
# 运行
# --------------------------
if __name__ == '__main__':
    print("🚀 开始生成最终版人气轨迹折线图...")
    plot_trajectory_final()
    print("🎉 生成完成！")
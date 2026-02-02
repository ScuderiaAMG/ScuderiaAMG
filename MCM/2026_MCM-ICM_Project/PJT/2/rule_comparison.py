# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from pathlib import Path
# import warnings
# warnings.filterwarnings('ignore')

# Path("output/figures").mkdir(parents=True, exist_ok=True)
# Path("output/results").mkdir(parents=True, exist_ok=True)

# # 读取预测数据（长格式）
# df = pd.read_csv("predicted_vote_shares.csv")

# # 清洗数据：仅保留有效周次（week>=1）和有效分数
# df = df[df['week'] >= 1].copy()
# df = df.dropna(subset=['judge_score_total', 'vote_share_hat', 'season', 'week', 'celebrity_name']).copy()

# # 确保数值类型
# df['judge_score_total'] = pd.to_numeric(df['judge_score_total'], errors='coerce')
# df['vote_share_hat'] = pd.to_numeric(df['vote_share_hat'], errors='coerce')
# df['season'] = pd.to_numeric(df['season'], errors='coerce')
# df['week'] = pd.to_numeric(df['week'], errors='coerce')
# df = df.dropna(subset=['judge_score_total', 'vote_share_hat', 'season', 'week']).copy()

# print(f"✓ 数据加载成功: {len(df)} 条有效记录")
# print(f"  赛季范围: S{int(df['season'].min())} - S{int(df['season'].max())}")
# print(f"  周次范围: Week {int(df['week'].min())} - Week {int(df['week'].max())}")

# def calculate_rank_method(df_week):
#     """排名法：评委排名 + 粉丝排名"""
#     df_week = df_week.copy()
#     df_week['judge_rank'] = df_week['judge_score_total'].rank(ascending=False, method='min')
#     df_week['fan_rank'] = df_week['vote_share_hat'].rank(ascending=False, method='min')
#     df_week['combined_rank'] = df_week['judge_rank'] + df_week['fan_rank']
#     return df_week

# def calculate_percent_method(df_week):
#     """百分比法：评委分数百分比 + 粉丝投票百分比"""
#     df_week = df_week.copy()
#     total_judge = df_week['judge_score_total'].sum()
#     total_fan = df_week['vote_share_hat'].sum()
    
#     if total_judge == 0 or total_fan == 0:
#         df_week['judge_pct'] = 0
#         df_week['fan_pct'] = 0
#         df_week['combined_pct'] = 0
#     else:
#         df_week['judge_pct'] = df_week['judge_score_total'] / total_judge * 100
#         df_week['fan_pct'] = df_week['vote_share_hat'] / total_fan * 100
#         df_week['combined_pct'] = df_week['judge_pct'] + df_week['fan_pct']
#     return df_week

# # 模拟淘汰过程：仅处理实际发生淘汰的周次
# simulation_results = []
# elimination_weeks_total = 0
# non_elimination_weeks = 0

# for season in sorted(df['season'].unique()):
#     season_data = df[df['season'] == season].copy()
#     max_week = season_data['week'].max()
    
#     for week in range(1, int(max_week) + 1):
#         week_data = season_data[season_data['week'] == week].copy()
#         if len(week_data) < 3:  # 少于3人不淘汰（决赛周）
#             non_elimination_weeks += 1
#             continue
            
#         # 检查当周是否有实际淘汰
#         actual_elim_candidates = week_data[week_data['is_eliminated'] == 1]['celebrity_name'].values
#         if len(actual_elim_candidates) == 0:
#             non_elimination_weeks += 1
#             continue  # 无淘汰发生，跳过该周（如决赛周）
            
#         actual_elim = actual_elim_candidates[0]
#         elimination_weeks_total += 1
        
#         # 应用两种规则
#         week_rank = calculate_rank_method(week_data)
#         week_pct = calculate_percent_method(week_data)
        
#         # 找出预测淘汰者（排名最后/得分最低）
#         elim_rank = week_rank.loc[week_rank['combined_rank'].idxmax(), 'celebrity_name']
#         elim_pct = week_pct.loc[week_pct['combined_pct'].idxmin(), 'celebrity_name']
        
#         simulation_results.append({
#             'season': int(season),
#             'week': int(week),
#             'actual_eliminated': actual_elim,
#             'rank_method_eliminated': elim_rank,
#             'percent_method_eliminated': elim_pct,
#             'rank_match': elim_rank == actual_elim,
#             'percent_match': elim_pct == actual_elim,
#             'methods_agree': elim_rank == elim_pct
#         })

# # 保存结果
# results_df = pd.DataFrame(simulation_results)
# results_df.to_csv("output/results/rule_simulation_results.csv", index=False)

# # 计算准确率（仅基于实际淘汰周次）
# total_elim_weeks = len(results_df)
# rank_accuracy = results_df['rank_match'].sum() / total_elim_weeks * 100
# pct_accuracy = results_df['percent_match'].sum() / total_elim_weeks * 100
# agreement_rate = results_df['methods_agree'].sum() / total_elim_weeks * 100

# print(f"\n✓ 淘汰周次统计:")
# print(f"  • 实际发生淘汰的周次: {total_elim_weeks}")
# print(f"  • 无淘汰周次（决赛/退赛等）: {non_elimination_weeks}")
# print(f"  • 总周次: {total_elim_weeks + non_elimination_weeks}")

# # 可视化1：两种规则淘汰结果一致性（按赛季）
# plt.figure(figsize=(14, 6))
# agreement_by_season = results_df.groupby('season')['methods_agree'].mean() * 100
# colors = ['#87CEEB' if x >= agreement_rate else '#D3D3D3' for x in agreement_by_season.values]
# plt.bar(agreement_by_season.index, agreement_by_season.values, color=colors, edgecolor='black', linewidth=0.8)
# plt.axhline(y=agreement_rate, color='#4682B4', linestyle='--', linewidth=2, 
#             label=f'平均一致性: {agreement_rate:.1f}%')
# plt.title('Elimination Consistency Between Rank and Percent Methods (Elimination Weeks Only)', 
#           fontsize=14, fontweight='bold', pad=15)
# plt.ylabel('Consistency (%)', fontsize=12)
# plt.xlabel('Season', fontsize=12)
# plt.legend(fontsize=10)
# plt.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
# plt.tight_layout()
# plt.savefig("output/figures/elimination_comparison.png", dpi=300, bbox_inches='tight', facecolor='white')
# plt.close()

# # 可视化2：规则准确率对比
# bias_analysis = []
# for season in results_df['season'].unique():
#     season_results = results_df[results_df['season'] == season]
#     rank_acc = (season_results['rank_match'].sum() / len(season_results)) * 100
#     pct_acc = (season_results['percent_match'].sum() / len(season_results)) * 100
#     bias_analysis.append({
#         'season': int(season),
#         'rank_accuracy': rank_acc,
#         'percent_accuracy': pct_acc,
#         'era': 'Rank Era' if season in [1,2] or season >= 28 else 'Percent Era'
#     })

# bias_df = pd.DataFrame(bias_analysis)
# plt.figure(figsize=(15, 7))
# bias_melt = bias_df.melt(id_vars=['season', 'era'], value_vars=['rank_accuracy', 'percent_accuracy'],
#                         var_name='Method', value_name='Accuracy')
# bias_melt['Method'] = bias_melt['Method'].map({'rank_accuracy': 'Rank Method', 'percent_accuracy': 'Percent Method'})

# sns.scatterplot(data=bias_melt, x='season', y='Accuracy', hue='Method', style='era', 
#                 s=120, linewidth=1.2, palette=['#4682B4', '#90EE90'])
# plt.axvline(x=2.5, color='gray', linestyle=':', alpha=0.6, linewidth=1.5)
# plt.axvline(x=27.5, color='gray', linestyle=':', alpha=0.6, linewidth=1.5)
# plt.text(1.5, 95, 'Rank Era\n(S1-2)', ha='center', fontsize=9, color='gray')
# plt.text(15, 95, 'Percent Era\n(S3-27)', ha='center', fontsize=9, color='gray')
# plt.text(31, 95, 'Rank Era\n(S28-34)', ha='center', fontsize=9, color='gray')
# plt.title('Accuracy of Voting Methods vs Actual Eliminations (Elimination Weeks Only)', 
#           fontsize=14, fontweight='bold', pad=15)
# plt.ylabel('Accuracy (%)', fontsize=12)
# plt.xlabel('Season', fontsize=12)
# plt.legend(title='Method / Era', fontsize=10, title_fontsize=11)
# plt.grid(alpha=0.3, linestyle='--', linewidth=0.5)
# plt.tight_layout()
# plt.savefig("output/figures/rule_bias_analysis.png", dpi=300, bbox_inches='tight', facecolor='white')
# plt.close()

# print("\n✅ 规则PK赛分析完成!")
# print(f"  • 实际淘汰周次: {total_elim_weeks} (仅这些周次计入准确率)")
# print(f"  • 两种规则结果一致率: {agreement_rate:.1f}%")
# print(f"  • 排名法准确率: {rank_accuracy:.1f}%")
# print(f"  • 百分比法准确率: {pct_accuracy:.1f}%")
# print(f"  • 无淘汰周次已排除: {non_elimination_weeks} 周（决赛/退赛等）")
# print(f"  • 图表已保存至: output/figures/elimination_comparison.png")
# print(f"  • 详细结果已保存至: output/results/rule_simulation_results.csv")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# 创建输出目录
Path("output/figures").mkdir(parents=True, exist_ok=True)
Path("output/results").mkdir(parents=True, exist_ok=True)

def load_and_clean_data(filepath):
    """加载并清洗数据"""
    df = pd.read_csv(filepath)
    
    # 基础清洗
    df = df[df['week'] >= 1].copy()
    
    # 确保数值列正确
    cols_to_numeric = ['judge_score_total', 'vote_share_hat', 'season', 'week']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna(subset=cols_to_numeric + ['celebrity_name']).copy()
    return df

def calculate_rank_score(group):
    """
    模拟 Rank Method (排名法):
    1. 计算评委分排名 (分数越高排名越靠前, 1是最高分还是最低分取决于赛制，
       通常DWTS中Rank points是: 第一名给最高分。
       这里假设: Rank 1 = 最低分 (Worst), Rank N = 最高分 (Best) 以便和Percent逻辑统一，
       或者遵循题目：Rank 1 = Best。
       
       *修正*：题目中 Rank Method 通常是 Rank 1 = Best。
       最终淘汰 Combined Score 最低 (数值最小) 或者 Rank 数值最大?
       
       根据DWTS惯例：
       Judges Rank points + Fan Rank points = Total Points. 
       最低 Total Points 被淘汰。
       (例: 3对选手，第一名得3分，最后一名得1分。总分低者淘汰)
    """
    # 评委排名分 (从小到大排序，rank(1)是最低分，得分1点)
    # method='min' 表示平分时取最小排名，还是平均? 通常赛制是同分得同点。
    # 这里使用 rank(pct=False), 假设分数越高 rank分越高
    group['judge_rank_pts'] = group['judge_score_total'].rank(method='min', ascending=True)
    
    # 粉丝排名分
    group['fan_rank_pts'] = group['vote_share_hat'].rank(method='min', ascending=True)
    
    # 总排名分
    group['total_rank_pts'] = group['judge_rank_pts'] + group['fan_rank_pts']
    
    # 预测淘汰: 总分最低者 (如果有平局，通常有Tie-breaker，这里简单取第一个)
    # idxmin 返回最小值的索引
    loser_idx = group['total_rank_pts'].idxmin()
    return group.loc[loser_idx, 'celebrity_name']

def calculate_percent_score(group):
    """
    模拟 Percent Method (百分比法):
    Judge % + Fan % = Total %
    最低 Total % 被淘汰
    """
    judge_sum = group['judge_score_total'].sum()
    fan_sum = group['vote_share_hat'].sum() # 应该是1.0，但防止归一化误差重新算
    
    if judge_sum == 0: judge_sum = 1 # 避免除零
    if fan_sum == 0: fan_sum = 1
    
    group['judge_pct'] = group['judge_score_total'] / judge_sum
    group['fan_pct'] = group['vote_share_hat'] / fan_sum # 这里使用模型预测的share
    
    group['total_pct'] = group['judge_pct'] + group['fan_pct']
    
    loser_idx = group['total_pct'].idxmin()
    return group.loc[loser_idx, 'celebrity_name']

def main():
    # 1. 加载数据
    df = load_and_clean_data("predicted_vote_shares.csv")
    print(f"数据加载完成: {len(df)} 行")

    simulation_results = []

    # 2. 按赛季/周次遍历
    # 这一步只负责“计算”，不负责“判断对错”
    for (season, week), current_week_data in df.groupby(['season', 'week']):
        if len(current_week_data) < 2:
            continue # 只有一个人没法淘汰
            
        # --- 核心修复逻辑开始 ---
        # 1. 获取真实淘汰者 (Ground Truth)
        # 检查这一周是否有 is_eliminated == 1
        eliminated_rows = current_week_data[current_week_data['is_eliminated'] == 1]
        
        has_elimination = False
        actual_eliminated_name = None
        
        if not eliminated_rows.empty:
            has_elimination = True
            actual_eliminated_name = eliminated_rows['celebrity_name'].iloc[0]
        
        # 2. 模型推演 (无论是否有人淘汰，模型都会算出一个最低分)
        # 深拷贝以避免SettingWithCopyWarning
        sim_data = current_week_data.copy()
        
        # 计算两种规则下的“拟淘汰者”
        pred_rank_loser = calculate_rank_score(sim_data)
        pred_pct_loser = calculate_percent_score(sim_data)
        
        # 3. 记录结果 (包含 has_elimination 标记)
        simulation_results.append({
            'season': season,
            'week': week,
            'actual_eliminated': actual_eliminated_name,
            'pred_rank_loser': pred_rank_loser,
            'pred_pct_loser': pred_pct_loser,
            'has_elimination': has_elimination # <--- 关键字段
        })
        # --- 核心修复逻辑结束 ---

    # 3. 转换为 DataFrame
    res_df = pd.DataFrame(simulation_results)
    
    # 保存原始推演数据 (包含非淘汰周，供查阅)
    res_df.to_csv("output/results/full_simulation_raw.csv", index=False)

    # ==========================================
    # 4. 评估阶段 (Evaluation Phase) - 严谨过滤
    # ==========================================
    
    # 过滤：只保留真正发生淘汰的周次！
    # 解决了用户提出的 "没有淘汰的周被算作错误" 的问题
    eval_df = res_df[res_df['has_elimination'] == True].copy()
    
    print(f"原始周次总数: {len(res_df)}")
    print(f"有效淘汰周次(用于计算准确率): {len(eval_df)}")

    # 计算准确性
    eval_df['rank_correct'] = (eval_df['pred_rank_loser'] == eval_df['actual_eliminated']).astype(int)
    eval_df['pct_correct'] = (eval_df['pred_pct_loser'] == eval_df['actual_eliminated']).astype(int)
    
    # 计算方法一致性 (仅在有效淘汰周比较，或者根据需求在全量数据比较)
    # 这里我们听从建议，避免被非淘汰周稀释，仅在有效周计算一致性
    eval_df['methods_agree'] = (eval_df['pred_rank_loser'] == eval_df['pred_pct_loser']).astype(int)

    # 保存评估结果
    eval_df.to_csv("output/results/evaluation_metrics.csv", index=False)

    # 5. 统计与可视化
    # 全局准确率
    print("\n=== 总体准确率 (仅淘汰周) ===")
    print(f"Rank Method Accuracy: {eval_df['rank_correct'].mean():.2%}")
    print(f"Percent Method Accuracy: {eval_df['pct_correct'].mean():.2%}")
    print(f"Methods Agreement Rate: {eval_df['methods_agree'].mean():.2%}")

    # 按赛季统计准确率
    season_stats = eval_df.groupby('season')[['rank_correct', 'pct_correct', 'methods_agree']].mean().reset_index()
    
    # 区分时代 (Eras) 用于绘图
    # 题目背景: S1-S2 (Rank), S3-S27 (Percent), S28+ (Rank)
    def get_era(s):
        if s <= 2: return 'Rank Era (Early)'
        elif s <= 27: return 'Percent Era'
        else: return 'Rank Era (Late)'
        
    season_stats['era'] = season_stats['season'].apply(get_era)

    # 绘图: 准确率对比
    plt.figure(figsize=(12, 6))
    
    # 融化数据以便 Seaborn 绘图
    melted = season_stats.melt(id_vars=['season', 'era'], 
                               value_vars=['rank_correct', 'pct_correct'], 
                               var_name='Method', value_name='Accuracy')
    
    melted['Method'] = melted['Method'].map({'rank_correct': 'Rank Method', 'pct_correct': 'Percent Method'})

    sns.scatterplot(data=melted, x='season', y='Accuracy', hue='Method', style='era', s=100)
    sns.lineplot(data=melted, x='season', y='Accuracy', hue='Method', alpha=0.3, legend=False)
    
    # 添加时代分割线
    plt.axvline(x=2.5, color='gray', linestyle='--')
    plt.axvline(x=27.5, color='gray', linestyle='--')
    
    plt.title('Prediction Accuracy by Method (Calculated on Elimination Weeks Only)')
    plt.ylabel('Accuracy (0-1)')
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.3)
    
    plt.savefig("output/figures/corrected_accuracy_plot.png")
    print("\n图表已保存至 output/figures/corrected_accuracy_plot.png")

if __name__ == "__main__":
    main()
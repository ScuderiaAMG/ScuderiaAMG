import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings('ignore')

def validate_model_predictions():
    """
    验证粉丝投票预测模型的两个核心指标：
    1. 一致性：预测投票是否能正确推导出每周淘汰结果
    2. 确定性：预测结果的可靠性及不确定性分布
    """
    
    # 1. 读取数据
    print("=" * 70)
    print("DWTS Vote Share Prediction Validation System")
    print("=" * 70)
    
    try:
        # 读取预测结果
        pred_df = pd.read_csv('predicted_vote_shares.csv')
        print(f"✓ Loaded predicted_vote_shares.csv ({len(pred_df)} records)")
        
        # 读取原始比赛数据（用于获取实际淘汰信息）
        raw_df = pd.read_excel('2026_MCM_Problem_C_Processed_Data.xlsx', sheet_name='Sheet1')
        print(f"✓ Loaded 2026_MCM_Problem_C_Processed_Data.xlsx")
        
        # 读取EP-FROM基准数据
        ep_from_df = pd.read_excel('EP_FROM_Model_Final_Results.xlsx')
        print(f"✓ Loaded EP_FROM_Model_Final_Results.xlsx")
        
    except FileNotFoundError as e:
        print(f"✗ Error: Required file not found - {e}")
        return
    
    # 2. 数据预处理与对齐
    print("\n[Step 1] Data preprocessing and alignment...")
    
    # 从原始数据中提取实际淘汰信息
    elimination_info = []
    for idx, row in raw_df.iterrows():
        celebrity = row['celebrity_name']
        season = row['season']
        eliminated_week = row['Eliminated_Week']
        
        # 清洗淘汰周次
        if pd.isna(eliminated_week) or eliminated_week in ['N/A', '', 'nan', 'None']:
            eliminated_week_clean = 97
        elif str(eliminated_week).lower() in ['决赛', 'winner', 'champion', 'finalist']:
            eliminated_week_clean = 99
        elif str(eliminated_week).lower() in ['退赛', 'withdrew', 'quit']:
            eliminated_week_clean = 98
        else:
            try:
                eliminated_week_clean = int(eliminated_week)
            except:
                eliminated_week_clean = 97
        
        elimination_info.append({
            'celebrity_name': celebrity,
            'season': season,
            'actual_eliminated_week': eliminated_week_clean
        })
    
    elimination_df = pd.DataFrame(elimination_info)
    
    # 合并预测数据与实际淘汰信息
    merged_df = pd.merge(
        pred_df, 
        elimination_df, 
        on=['celebrity_name', 'season'], 
        how='left'
    )
    
    # 标记"该周是否被淘汰"
    merged_df['is_actually_eliminated'] = (
        (merged_df['week'] == merged_df['actual_eliminated_week']) & 
        (merged_df['actual_eliminated_week'] < 97)
    ).astype(int)
    
    print(f"✓ Merged prediction and elimination data ({len(merged_df)} records)")
    
    # 3. 一致性验证：预测投票是否能正确推导淘汰结果
    print("\n[Step 2] Consistency Validation: Elimination Accuracy Analysis")
    
    weekly_elimination_results = []
    
    for (season, week), group in merged_df.groupby(['season', 'week']):
        # 排除决赛周（无淘汰或淘汰规则不同）
        if week >= 10 and group['actual_eliminated_week'].max() >= 97:
            continue
            
        # 找出预测得票最低的选手（最可能被淘汰）
        pred_lowest_idx = group['vote_share_hat'].idxmin()
        pred_eliminated = group.loc[pred_lowest_idx, 'celebrity_name']
        pred_vote_share = group.loc[pred_lowest_idx, 'vote_share_hat']
        
        # 找出实际被淘汰的选手
        actual_eliminated = group[group['is_actually_eliminated'] == 1]['celebrity_name'].tolist()
        
        # 判断预测是否正确
        is_correct = pred_eliminated in actual_eliminated if actual_eliminated else False
        
        weekly_elimination_results.append({
            'season': season,
            'week': week,
            'predicted_eliminated': pred_eliminated,
            'actual_eliminated': ', '.join(actual_eliminated) if actual_eliminated else 'None',
            'is_correct': is_correct,
            'num_contestants': len(group),
            'min_vote_share_hat': pred_vote_share,
            'vote_gap_to_second': (
                group['vote_share_hat'].nsmallest(2).iloc[1] - pred_vote_share 
                if len(group) >= 2 else np.nan
            )
        })
    
    elimination_accuracy_df = pd.DataFrame(weekly_elimination_results)
    overall_accuracy = elimination_accuracy_df['is_correct'].mean()
    
    print(f"  • Weekly elimination prediction accuracy: {overall_accuracy:.2%} "
          f"({elimination_accuracy_df['is_correct'].sum()}/{len(elimination_accuracy_df)} weeks)")
    
    # 3.1 淘汰边缘分析：当预测最低得票与第二低得票差距小时，预测不确定性高
    close_calls = elimination_accuracy_df[elimination_accuracy_df['vote_gap_to_second'] < 0.02]
    print(f"  • Close elimination calls (<2% vote gap): {len(close_calls)} weeks")
    if len(close_calls) > 0:
        close_call_accuracy = close_calls['is_correct'].mean()
        print(f"    - Accuracy on close calls: {close_call_accuracy:.2%}")
    
    # 4. 预测得票与评委评分的相关性（补充一致性指标）
    print("\n[Step 3] Consistency Validation: Vote Share vs Judge Score Correlation")
    
    correlations = []
    for (season, week), group in merged_df.groupby(['season', 'week']):
        if len(group) < 3:  # 至少3人才能计算有意义的相关性
            continue
            
        # 计算Spearman相关系数（非参数，适合非线性关系）
        spearman_corr, _ = spearmanr(group['vote_share_hat'], group['judge_score_total'])
        correlations.append({
            'season': season,
            'week': week,
            'spearman_corr': spearman_corr,
            'num_contestants': len(group)
        })
    
    corr_df = pd.DataFrame(correlations)
    avg_spearman = corr_df['spearman_corr'].mean()
    positive_corr_ratio = (corr_df['spearman_corr'] > 0).mean()
    
    print(f"  • Average Spearman correlation (vote share vs judge score): {avg_spearman:.4f}")
    print(f"  • Weeks with positive correlation: {positive_corr_ratio:.2%}")
    
    # 5. 确定性验证：预测不确定性分析
    print("\n[Step 4] Certainty/Uncertainty Analysis")
    
    # 5.1 基础不确定性统计
    avg_uncertainty = merged_df['uncertainty'].mean()
    uncertainty_std = merged_df['uncertainty'].std()
    uncertainty_range = (merged_df['uncertainty'].min(), merged_df['uncertainty'].max())
    
    print(f"  • Average prediction uncertainty: {avg_uncertainty:.4f} ± {uncertainty_std:.4f}")
    print(f"  • Uncertainty range: [{uncertainty_range[0]:.4f}, {uncertainty_range[1]:.4f}]")
    
    # 5.2 不确定性分层分析：淘汰边缘 vs 安全选手
    elimination_edge = merged_df[merged_df['is_eliminated'] == 1]
    safe_contestants = merged_df[merged_df['is_eliminated'] == 0]
    
    if len(elimination_edge) > 0 and len(safe_contestants) > 0:
        edge_uncertainty = elimination_edge['uncertainty'].mean()
        safe_uncertainty = safe_contestants['uncertainty'].mean()
        uncertainty_ratio = edge_uncertainty / safe_uncertainty
        
        print(f"  • Uncertainty on elimination edge: {edge_uncertainty:.4f}")
        print(f"  • Uncertainty for safe contestants: {safe_uncertainty:.4f}")
        print(f"  • Uncertainty ratio (edge/safe): {uncertainty_ratio:.2f}x")
    
    # 5.3 比赛阶段不确定性分析
    merged_df['competition_stage'] = pd.cut(
        merged_df['week'], 
        bins=[0, 3, 7, 12], 
        labels=['Early Stage (Weeks 1-3)', 'Mid Stage (Weeks 4-7)', 'Late Stage (Weeks 8+)']
    )
    
    stage_uncertainty = merged_df.groupby('competition_stage')['uncertainty'].agg(['mean', 'std', 'count']).round(4)
    print("\n  Uncertainty by competition stage:")
    print(stage_uncertainty)
    
    # 5.4 与EP-FROM基准对比（如果数据重叠）
    ep_from_comparison = pd.merge(
        merged_df[['season', 'week', 'celebrity_name', 'vote_share_hat', 'uncertainty']],
        ep_from_df[['Season', 'Week', 'Celebrity_Name', 'Chebyshev_Radius']],
        left_on=['season', 'week', 'celebrity_name'],
        right_on=['Season', 'Week', 'Celebrity_Name'],
        how='inner'
    )
    
    if len(ep_from_comparison) > 0:
        avg_ep_from_radius = ep_from_comparison['Chebyshev_Radius'].mean()
        print(f"\n  • Average EP-FROM Chebyshev radius (benchmark): {avg_ep_from_radius:.4f}")
        print(f"  • Our average uncertainty: {avg_uncertainty:.4f}")
        if avg_uncertainty < avg_ep_from_radius:
            print("    → Our model shows HIGHER certainty than EP-FROM baseline")
        else:
            print("    → Our model shows LOWER certainty than EP-FROM baseline")
    
    # 6. 生成验证报告
    print("\n" + "=" * 70)
    print("VALIDATION REPORT SUMMARY")
    print("=" * 70)
    
    report = {
        'Consistency Metrics': {
            'Weekly Elimination Accuracy': f"{overall_accuracy:.2%} ({elimination_accuracy_df['is_correct'].sum()}/{len(elimination_accuracy_df)})",
            'Spearman Correlation (Vote vs Judge)': f"{avg_spearman:.4f}",
            'Positive Correlation Weeks': f"{positive_corr_ratio:.2%}"
        },
        'Certainty Metrics': {
            'Average Uncertainty': f"{avg_uncertainty:.4f}",
            'Uncertainty Range': f"[{uncertainty_range[0]:.4f}, {uncertainty_range[1]:.4f}]",
            'Elimination Edge Uncertainty': f"{elimination_edge['uncertainty'].mean() if len(elimination_edge)>0 else 'N/A':.4f}",
            'Safe Contestant Uncertainty': f"{safe_contestants['uncertainty'].mean() if len(safe_contestants)>0 else 'N/A':.4f}"
        },
        'Key Findings': []
    }
    
    # 生成关键发现
    if overall_accuracy > 0.80:
        report['Key Findings'].append(f"✓ HIGH consistency: {overall_accuracy:.0%} of weekly eliminations correctly predicted")
    elif overall_accuracy > 0.70:
        report['Key Findings'].append(f"✓ MODERATE consistency: {overall_accuracy:.0%} elimination accuracy")
    else:
        report['Key Findings'].append(f"⚠ LOW consistency: Only {overall_accuracy:.0%} elimination accuracy")
    
    if avg_spearman > 0.4:
        report['Key Findings'].append("✓ Strong positive correlation between predicted votes and judge scores")
    elif avg_spearman > 0.2:
        report['Key Findings'].append("✓ Moderate positive correlation between predicted votes and judge scores")
    else:
        report['Key Findings'].append("⚠ Weak correlation between predicted votes and judge scores")
    
    if len(elimination_edge) > 0 and len(safe_contestants) > 0:
        edge_unc = elimination_edge['uncertainty'].mean()
        safe_unc = safe_contestants['uncertainty'].mean()
        if edge_unc > safe_unc * 1.2:
            report['Key Findings'].append("✓ Model appropriately assigns higher uncertainty to elimination-edge contestants")
        else:
            report['Key Findings'].append("⚠ Limited differentiation of uncertainty between elimination-edge and safe contestants")
    
    # 打印报告
    for category, metrics in report.items():
        print(f"\n{category}:")
        if isinstance(metrics, dict):
            for metric, value in metrics.items():
                print(f"  • {metric}: {value}")
        elif isinstance(metrics, list):
            for finding in metrics:
                print(f"  {finding}")
    
    # 7. 保存详细结果
    elimination_accuracy_df.to_csv('validation_elimination_accuracy.csv', index=False)
    corr_df.to_csv('validation_correlations.csv', index=False)
    merged_df.to_csv('validation_full_results.csv', index=False)
    
    print("\n" + "=" * 70)
    print("Validation results saved to:")
    print("  • validation_elimination_accuracy.csv")
    print("  • validation_correlations.csv")
    print("  • validation_full_results.csv")
    print("=" * 70)
    
    # 8. 生成文本报告
    with open('validation_report.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("DWTS VOTE SHARE PREDICTION VALIDATION REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"EXECUTION TIME: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("1. CONSISTENCY VALIDATION\n")
        f.write("-" * 70 + "\n")
        f.write(f"   Weekly Elimination Accuracy: {overall_accuracy:.2%}\n")
        f.write(f"   Total Weeks Analyzed: {len(elimination_accuracy_df)}\n")
        f.write(f"   Correctly Predicted Eliminations: {elimination_accuracy_df['is_correct'].sum()}\n")
        f.write(f"   Average Spearman Correlation (Vote vs Judge): {avg_spearman:.4f}\n\n")
        
        f.write("2. CERTAINTY VALIDATION\n")
        f.write("-" * 70 + "\n")
        f.write(f"   Average Prediction Uncertainty: {avg_uncertainty:.4f}\n")
        f.write(f"   Uncertainty Range: [{uncertainty_range[0]:.4f}, {uncertainty_range[1]:.4f}]\n")
        if len(elimination_edge) > 0:
            f.write(f"   Elimination Edge Uncertainty: {elimination_edge['uncertainty'].mean():.4f}\n")
        if len(safe_contestants) > 0:
            f.write(f"   Safe Contestant Uncertainty: {safe_contestants['uncertainty'].mean():.4f}\n\n")
        
        f.write("3. KEY FINDINGS\n")
        f.write("-" * 70 + "\n")
        for finding in report['Key Findings']:
            f.write(f"   {finding}\n")
    
    print("\n✓ Full validation report saved to 'validation_report.txt'")
    return report

if __name__ == "__main__":
    report = validate_model_predictions()
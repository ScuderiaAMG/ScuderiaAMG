import pandas as pd
import numpy as np
from scipy.stats import zscore, spearmanr

def optimize_algorithm_v2():
    # ==========================================
    # PART 1: 定义并输出优化后的数学模型
    # ==========================================
    print("="*60)
    print("OPTIMIZED ELIMINATION MODEL: The 'Meritocratic Safety Net' System")
    print("="*60)
    print("Core Concept: Standardized Scores + Judge's Veto Power")
    print("Improvement over V1: Adds a non-linear 'Safety Net' (Judges Save) to")
    print("                     prevent high-popularity/low-skill outliers from eliminating")
    print("                     skilled dancers in the bottom tier.")
    print("\nMathematical Logic:")
    print("  1. Composite Score (CS) = 0.5 * Z_judge + 0.5 * Z_fan")
    print("  2. Identify Bottom 2 contestants based on CS.")
    print("  3. Elimination Rule (The 'Veto'):")
    print("       Eliminate argmin(Judge_Score) from Bottom 2.")
    print("       (If Judge Scores tie, revert to lowest CS).")
    print("="*60 + "\n")

    # ==========================================
    # PART 2: 数据加载与预处理
    # ==========================================
    print("[1] Loading Data...")
    try:
        # 读取数据 (使用第1问生成的预测数据)
        df = pd.read_csv("predicted_vote_shares.csv")
        cols = ['season', 'week', 'celebrity_name', 'judge_score_total', 'vote_share_hat']
        df = df[cols].dropna().copy()
        # 确保类型正确
        df['season'] = df['season'].astype(int)
        df['week'] = df['week'].astype(int)
    except FileNotFoundError:
        print("Error: 'predicted_vote_shares.csv' not found.")
        return

    # ==========================================
    # PART 3: 核心算法实现 (Hybrid Z-Score + Judges Save)
    # ==========================================
    print("[2] Executing Optimized Algorithm...")

    def apply_safety_net_logic(group):
        if len(group) <= 1:
            return None # 决赛或单人无法淘汰

        # 1. 计算基础 Z-Score (标准化)
        # 裁判分标准化
        j_std = group['judge_score_total'].std(ddof=1)
        if j_std == 0: j_std = 1
        group['Z_Judge'] = (group['judge_score_total'] - group['judge_score_total'].mean()) / j_std

        # 粉丝票标准化
        f_std = group['vote_share_hat'].std(ddof=1)
        if f_std == 0: f_std = 1
        group['Z_Fan'] = (group['vote_share_hat'] - group['vote_share_hat'].mean()) / f_std

        # 2. 合成得分 (50/50 权重)
        group['Composite_Score'] = 0.5 * group['Z_Judge'] + 0.5 * group['Z_Fan']
        
        # 3. 识别 Bottom 2
        # 按合成得分排序
        sorted_group = group.sort_values('Composite_Score', ascending=True)
        
        group['Is_Eliminated'] = 0
        group['Is_Bottom2'] = 0
        
        if len(sorted_group) >= 2:
            bottom_2 = sorted_group.iloc[:2] # 最低分的两个人
            group.loc[bottom_2.index, 'Is_Bottom2'] = 1
            
            # --- 优化核心：Judges Save 机制 ---
            # 在 Bottom 2 中，比较原始裁判分 (judge_score_total)
            # 裁判分更低的人被强制淘汰 (Veto Power)
            p1 = bottom_2.iloc[0] # 分数最低
            p2 = bottom_2.iloc[1] # 分数倒数第二
            
            eliminated_idx = -1
            
            if p1['judge_score_total'] < p2['judge_score_total']:
                eliminated_idx = p1.name
            elif p2['judge_score_total'] < p1['judge_score_total']:
                eliminated_idx = p2.name # 即使 p2 综合分比 p1 高，但裁判分低，照样淘汰
            else:
                # 裁判分平局，淘汰综合分更低的人 (p1)
                eliminated_idx = p1.name
                
            group.loc[eliminated_idx, 'Is_Eliminated'] = 1
            
        else:
            # 只有不到2人时的防守代码
            group.loc[sorted_group.index[0], 'Is_Eliminated'] = 1

        return group

    # 应用算法
    # 修复 FutureWarning: 使用 group_keys=False 并重新赋值
    df_optimized = df.groupby(['season', 'week'], group_keys=False).apply(apply_safety_net_logic)
    df_optimized = df_optimized.dropna()

    # 保存结果
    df_optimized.to_csv("Optimized_Algorithm_Results.csv", index=False)
    print("    -> Calculation Complete. Results saved.")

    # ==========================================
    # PART 4: “更公平”的量化证明 (Quantitative Proof)
    # ==========================================
    print("\n" + "="*60)
    print("QUANTITATIVE PROOF OF OPTIMIZATION")
    print("="*60)

    # --- 证明 1: 生存与技术的相关性 (Spearman) ---
    # 计算“并未被淘汰”状态与“裁判打分”的相关性
    # 正相关越高，说明裁判分高的人越安全
    corr, _ = spearmanr(df_optimized['judge_score_total'], 1 - df_optimized['Is_Eliminated'])

    print("\n[Proof 1: Technical Integrity Metric]")
    print("  Metric: Correlation between Judge Scores and Survival")
    print(f"  Spearman Correlation: {corr:.4f}")
    print("  Interpretation: Positive value confirms skill is a protective factor.")
    
    # --- 证明 2: 关键争议案例回测 (Bobby Bones, Season 27) ---
    # 這是“更公平”最有力的证据
    print("\n[Proof 2: The 'Bobby Bones' Stress Test (Season 27)]")
    target_season = 27
    target_star = "Bobby Bones"
    
    subset = df_optimized[(df_optimized['season'] == target_season) & 
                          (df_optimized['celebrity_name'] == target_star)].sort_values('week')
    
    if subset.empty:
        print(f"  Note: {target_star} not found.")
    else:
        print(f"  Tracking {target_star} in 'Meritocratic Safety Net' System:")
        eliminated_flag = False
        for _, row in subset.iterrows():
            status = "ELIMINATED (By Judges Save)" if row['Is_Eliminated'] == 1 else "Safe"
            bottom2_status = " [Bottom 2]" if row['Is_Bottom2'] == 1 else ""
            print(f"    Week {row['week']}: Judge Score {row['judge_score_total']} | Composite Z-Score {row['Composite_Score']:.2f}{bottom2_status} | Status: {status}")
            
            if row['Is_Eliminated'] == 1:
                eliminated_flag = True
                break
        
        print("-" * 40)
        if eliminated_flag:
            print(f"  -> SUCCESS: The optimized system eliminates {target_star}.")
            print(f"     Why? Even if fans saved him from last place, his low judge scores")
            print(f"     triggered the 'Veto' when he landed in the Bottom 2.")
        else:
            print(f"  -> RESULT: {target_star} survives.")

    # --- 证明 3: “冤案率” (Robbed Rate) ---
    # 定义冤案：当周裁判分前3名，却被淘汰了。
    
    def count_injustices(df_in):
        injustice_count = 0
        total_eliminations = 0
        for (season, week), group in df_in.groupby(['season', 'week']):
            if len(group) < 5: continue 
            
            eliminated = group[group['Is_Eliminated'] == 1]
            if eliminated.empty: continue
            
            total_eliminations += len(eliminated)
            
            # 裁判分前3的分数线
            top3_score = group['judge_score_total'].nlargest(3).min()
            
            for _, row in eliminated.iterrows():
                if row['judge_score_total'] >= top3_score:
                    injustice_count += 1
        return injustice_count, total_eliminations

    injust_count, total_elims = count_injustices(df_optimized)
    
    print("\n[Proof 3: 'Robbed' Rate Analysis]")
    print(f"  Definition of 'Robbed': Contestant eliminated despite having Top 3 judge scores.")
    print(f"  Total Eliminations Simulated: {total_elims}")
    print(f"  'Robbed' Incidents in New System: {injust_count}")
    print(f"  'Robbed' Rate: {injust_count/total_elims:.1%}")
    print("  -> A rate near 0% proves the system protects top talent.")

if __name__ == "__main__":
    optimize_algorithm_v2()
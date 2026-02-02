import pandas as pd
import numpy as np
import re

# ==========================================
# 2026 MCM Problem C: Comprehensive Solution
# Tasks 1, 2, & 3
# ==========================================

def solve_mcm_problem_c(file_path):
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)

    # ---------------------------------------------------------
    # 1. 数据预处理 (Data Preprocessing)
    # ---------------------------------------------------------
    
    # 辅助函数：解析 'results' 列以提取淘汰周次
    def get_elimination_week(result_str):
        if pd.isna(result_str): return 100 # 假设未提及则为决赛/幸存
        result_str = str(result_str).lower()
        if 'eliminated week' in result_str:
            try:
                match = re.search(r'week\s*(\d+)', result_str)
                if match: return int(match.group(1))
            except: return 100
        elif 'withdrew' in result_str: return 100 # 视为非正常淘汰
        elif 'winner' in result_str or 'place' in result_str: return 100
        return 100

    df['Elimination_Week'] = df['results'].apply(get_elimination_week)

    # 构建结构化数据字典：Season -> Week -> Data
    # 这有助于快速访问每周的比赛状态
    seasons_data = {}
    all_seasons = sorted(df['season'].unique())

    for season in all_seasons:
        seasons_data[season] = {}
        season_df = df[df['season'] == season]
        
        # 遍历常规赛周次 (1-11周)
        for week in range(1, 12):
            # 动态构建列名 (e.g., week1_judge1_score)
            judge_cols = [f'week{week}_judge{i}_score' for i in range(1, 5)]
            valid_judge_cols = [c for c in judge_cols if c in df.columns]
            
            if not valid_judge_cols: continue
            
            # 筛选当周活跃选手：有分数记录且当周（或之后）才被淘汰
            active_mask = (season_df[valid_judge_cols[0]] > 0) & (season_df[valid_judge_cols[0]].notna())
            active_contestants = season_df[active_mask].copy()
            
            if active_contestants.empty: continue
            
            # 计算该周裁判总分
            active_contestants['Week_Total'] = active_contestants[valid_judge_cols].sum(axis=1)
            
            # 识别本周被淘汰者 (Ground Truth)
            eliminated_names = active_contestants[active_contestants['Elimination_Week'] == week]['celebrity_name'].tolist()
            
            seasons_data[season][week] = {
                'contestants': active_contestants['celebrity_name'].tolist(),
                'judge_scores': active_contestants['Week_Total'].tolist(),
                'eliminated': eliminated_names
            }

    # ---------------------------------------------------------
    # 2. 核心算法库 (Core Algorithms for Task 1 & 2)
    # ---------------------------------------------------------
    
    def calculate_ranks(scores, ascending=False):
        """
        计算排名。
        ascending=False: 分数越高(大)，名次越靠前(1)。
        注意：在'Rank Method'中，名次是数值，1是最小值。
        """
        # 使用 method='min' 处理并列 (e.g. 1, 2, 2, 4)
        return pd.Series(scores).rank(ascending=(not ascending), method='min').values

    def estimate_fan_votes(contestants, judge_scores, eliminated_list, method='Percentage', n_sim=3000):
        """
        Task 1: 蒙特卡洛模拟，逆向推导未知的观众投票。
        """
        n = len(judge_scores)
        valid_estimates = []
        
        # 计算评委指标
        if method == 'Percentage':
            total_j = sum(judge_scores)
            if total_j == 0: return None
            judge_metrics = np.array(judge_scores) / total_j * 100
        else: # Rank
            judge_metrics = calculate_ranks(judge_scores, ascending=False) # 高分 -> Rank 1
            
        elim_indices = [contestants.index(e) for e in eliminated_list if e in contestants]
        if not elim_indices: return None
        
        # 开始模拟
        for _ in range(n_sim):
            if method == 'Percentage':
                # Dirichlet 分布生成随机百分比 (和为100)
                fan_metrics = np.random.dirichlet(np.ones(n)) * 100
                combined = judge_metrics + fan_metrics
                worst_idx = np.argmin(combined) # 最小值被淘汰
            else: # Rank
                # 全排列生成随机排名 (1 to N)
                fan_metrics = np.random.permutation(n) + 1
                combined = judge_metrics + fan_metrics
                worst_idx = np.argmax(combined) # 最大值(排名靠后)被淘汰
                
            # 约束检查：模拟结果必须与历史淘汰吻合
            if worst_idx == elim_indices[0]:
                valid_estimates.append(fan_metrics)
        
        if not valid_estimates: return None
        return np.mean(valid_estimates, axis=0) # 返回所有可行解的平均值

    # ---------------------------------------------------------
    # 3. 任务分析与执行 (Execution Logic)
    # ---------------------------------------------------------
    print("Running Task 2 & 3 Simulations...")
    
    analysis_log = []
    
    # 定义我们要重点分析的争议选手 (Task 3 Targets)
    targets = [
        {'Name': 'Jerry Rice', 'Season': 2, 'Actual_Method': 'Rank'},
        {'Name': 'Bobby Bones', 'Season': 27, 'Actual_Method': 'Percentage'},
        {'Name': 'Billy Ray Cyrus', 'Season': 4, 'Actual_Method': 'Percentage'},
        {'Name': 'Bristol Palin', 'Season': 11, 'Actual_Method': 'Percentage'}
    ]
    
    for target in targets:
        s = target['Season']
        name = target['Name']
        actual_method = target['Actual_Method']
        
        if s not in seasons_data: continue
        
        # 按周次遍历
        for week in sorted(seasons_data[s].keys()):
            data = seasons_data[s][week]
            
            # 如果目标选手不在本周名单中（已淘汰或缺席），跳过
            if name not in data['contestants']: continue
            # 如果本周没有淘汰发生，无法作为基准，跳过
            if not data['eliminated']: continue
            
            # === Task 1: 估算实际观众票数 ===
            est_fan = estimate_fan_votes(
                data['contestants'], 
                data['judge_scores'], 
                data['eliminated'], 
                method=actual_method
            )
            
            if est_fan is None: continue 
            
            # === Task 2: 赛制反事实模拟 (Counterfactual) ===
            # 我们将估算出的观众票数，代入"另一种赛制"的公式
            
            res = {
                'Contestant': name, 'Season': s, 'Week': week,
                'Judge_Score': data['judge_scores'][data['contestants'].index(name)],
                'Actual_Eliminated': data['eliminated'][0]
            }
            
            n = len(data['contestants'])
            
            if actual_method == 'Rank':
                # 实际是 Rank -> 模拟 Percentage
                # 将 Rank 转化为权重 (Rank 1 权重 N, Rank N 权重 1)
                weights = n - est_fan + 1
                fan_pct_sim = weights / np.sum(weights) * 100
                
                total_j = sum(data['judge_scores'])
                judge_pct = np.array(data['judge_scores']) / total_j * 100
                
                combined_alt = judge_pct + fan_pct_sim
                worst_idx_alt = np.argmin(combined_alt) # Pct制下最低分淘汰
                
                res['Alt_Method_Name'] = 'Percentage'
                res['Alt_Eliminated'] = data['contestants'][worst_idx_alt]
                
                # 为 Task 3 准备数据：找出新赛制下的 Bottom 2
                sorted_idx = np.argsort(combined_alt) # Ascending
                bottom_two = [data['contestants'][i] for i in sorted_idx[:2]]
                
            else:
                # 实际是 Percentage -> 模拟 Rank
                # 将 Percent 转化为 Rank (Pct最高 -> Rank 1)
                fan_ranks_sim = pd.Series(est_fan).rank(ascending=False, method='min').values
                judge_ranks = calculate_ranks(data['judge_scores'], ascending=False)
                
                combined_alt = judge_ranks + fan_ranks_sim
                worst_idx_alt = np.argmax(combined_alt) # Rank制下最大值淘汰
                
                res['Alt_Method_Name'] = 'Rank'
                res['Alt_Eliminated'] = data['contestants'][worst_idx_alt]
                
                # 为 Task 3 准备数据：找出新赛制下的 Bottom 2
                sorted_idx = np.argsort(combined_alt)[::-1] # Descending (Max is worst)
                bottom_two = [data['contestants'][i] for i in sorted_idx[:2]]
            
            # === Task 3: 评委拯救机制模拟 (Judges Save) ===
            # 规则：评委从 Bottom 2 中选择 Judge Score 较高者晋级
            c1, c2 = bottom_two[0], bottom_two[1]
            s1 = data['judge_scores'][data['contestants'].index(c1)]
            s2 = data['judge_scores'][data['contestants'].index(c2)]
            
            if s1 < s2: judge_elim = c1   # c1 分低，淘汰 c1
            elif s2 < s1: judge_elim = c2 # c2 分低，淘汰 c2
            else: judge_elim = c1         # 平局，默认淘汰排名更低者
            
            res['Judge_Save_Eliminated'] = judge_elim
            
            # 标记是否改变了命运
            res['Target_Elim_By_Alt'] = (res['Alt_Eliminated'] == name)
            res['Target_Elim_By_Save'] = (judge_elim == name)
            
            analysis_log.append(res)

    return pd.DataFrame(analysis_log)

# ==========================================
# Main Execution Block
# ==========================================
if __name__ == "__main__":
    # 请确保 CSV 文件在当前目录下
    file_name = r'D:\Repositories\ScuderiaAMG\MCM\2026_MCM-ICM_Problems\PRJ\2026_MCM_Problem_C_Data.csv'
    
    try:
        results_df = solve_mcm_problem_c(file_name)
        
        print("\n" + "="*50)
        print("FINAL REPORT: IMPACT ANALYSIS")
        print("="*50)
        
        # 筛选显示该选手“原本安全，但在新规则下被淘汰”的高风险周次
        risk_mask = (results_df['Target_Elim_By_Alt'] == True) | (results_df['Target_Elim_By_Save'] == True)
        risk_report = results_df[risk_mask][
            ['Season', 'Contestant', 'Week', 'Actual_Eliminated', 
             'Alt_Method_Name', 'Alt_Eliminated', 'Judge_Save_Eliminated']
        ]
        
        if not risk_report.empty:
            print("The following contestants would have been eliminated under new rules:")
            print(risk_report.to_string(index=False))
        else:
            print("No changes in elimination results found for the simulated targets.")
            
    except FileNotFoundError:
        print(f"Error: File {file_name} not found. Please upload the data file.")
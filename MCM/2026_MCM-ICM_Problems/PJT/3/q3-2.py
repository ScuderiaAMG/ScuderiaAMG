import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
import warnings

# ================= 配置区域 =================
# 自动文件匹配，无需手动修改
# ===========================================

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

def auto_find_files():
    """智能查找所需文件"""
    print(f"📂 当前工作目录: {os.getcwd()}")
    all_files = glob.glob("*.csv") + glob.glob("*.xlsx")
    
    # 1. 寻找预测结果文件
    res_file = None
    for f in all_files:
        f_lower = f.lower()
        if 'predicted_vote' in f_lower and 'sorted' not in f_lower:
            res_file = f
            break
    if not res_file:
        cands = [f for f in all_files if 'vote' in f.lower() and 'hat' in f.lower()]
        if cands: res_file = cands[0]

    print(f"✅ 锁定核心预测数据: {res_file}")
    return res_file

def load_data():
    """加载并清洗数据 (修复列名冲突版)"""
    print(f"\n[{pd.Timestamp.now()}] 正在加载数据...")
    res_path = auto_find_files()
    
    if not res_path:
        raise FileNotFoundError("❌ 找不到包含 'predicted_vote' 的预测结果文件！")

    def read_f(p): return pd.read_excel(p) if p.endswith('.xlsx') else pd.read_csv(p)
    
    df = read_f(res_path)
    
    # 1. 规范化原始列名 (去空格，转小写)
    df.columns = [c.strip().lower() for c in df.columns]
    print(f"原始列名: {df.columns.tolist()}")

    # 2. 精确重命名逻辑 (避免重复映射)
    rename_dict = {}
    
    # --- 映射粉丝票数列 (优先级: vote_share_hat > vote_share) ---
    if 'vote_share_hat' in df.columns:
        rename_dict['vote_share_hat'] = 'Fan_Share'
    elif 'vote_share' in df.columns:
        rename_dict['vote_share'] = 'Fan_Share'
    else:
        # 最后的保底模糊搜索
        for c in df.columns:
            if 'vote' in c and 'share' in c:
                rename_dict[c] = 'Fan_Share'
                break
                
    # --- 映射评委分数列 ---
    if 'judge_score_total' in df.columns:
        rename_dict['judge_score_total'] = 'Judge_Score'
    else:
        for c in df.columns:
            if 'judge' in c and 'score' in c:
                rename_dict[c] = 'Judge_Score'
                break

    # --- 映射其他基础列 ---
    if 'season' in df.columns: rename_dict['season'] = 'Season'
    if 'week' in df.columns: rename_dict['week'] = 'Week'
    if 'celebrity_name' in df.columns: rename_dict['celebrity_name'] = 'Name'
    if 'is_eliminated' in df.columns: rename_dict['is_eliminated'] = 'Is_Eliminated'

    print(f"应用列名映射: {rename_dict}")
    df.rename(columns=rename_dict, inplace=True)
    
    # 3. 检查并清理多余列
    # 如果此时还有列叫 vote_share (因为上面可能只重命名了 vote_share_hat)，需要防止混淆
    # 但由于我们已经指定了 'Fan_Share'，后续只用这个名字，所以安全。
    
    # 确保必要列存在
    req_cols = ['Season', 'Week', 'Name', 'Judge_Score', 'Fan_Share', 'Is_Eliminated']
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise ValueError(f"❌ 数据缺失关键列: {missing}。请检查 CSV 文件头。")

    # 4. 类型转换
    print("正在转换数据类型...")
    # 确保 Fan_Share 是唯一的 Series
    if isinstance(df['Fan_Share'], pd.DataFrame):
        print("⚠️ 警告: Fan_Share 依然对应多列，正在强制选取第一列...")
        df['Fan_Share'] = df['Fan_Share'].iloc[:, 0]

    df['Judge_Score'] = pd.to_numeric(df['Judge_Score'], errors='coerce').fillna(0)
    df['Fan_Share'] = pd.to_numeric(df['Fan_Share'], errors='coerce').fillna(0)
    
    print(f"✅ 数据加载完成，共 {len(df)} 行。")
    return df

def simulate_methods(df):
    """全量模拟两种投票规则"""
    print(f"\n[{pd.Timestamp.now()}] 正在全量模拟两种投票规则...")
    
    results = []
    groups = df.groupby(['Season', 'Week'])
    
    for (season, week), group in groups:
        g = group.copy()
        n_contestants = len(g)
        
        # 跳过决赛圈或无人区
        if n_contestants < 2: continue

        # --- 方法 1: 排名制 (Rank Method) ---
        # 评委排名 (分数高=排名数值小)
        g['Rank_Judge'] = g['Judge_Score'].rank(ascending=False, method='min')
        # 粉丝排名 (票数高=排名数值小)
        g['Rank_Fan'] = g['Fan_Share'].rank(ascending=False, method='min')
        # 总排名 (越小越好)
        g['Rank_Sum'] = g['Rank_Judge'] + g['Rank_Fan']
        # 模拟排名 (Rank_Sum 升序)
        g['Final_Place_RankMethod'] = g['Rank_Sum'].rank(ascending=True, method='min')
        # 标记淘汰 (Rank_Sum 最大者)
        max_rank = g['Rank_Sum'].max()
        g['Eliminated_By_Rank'] = (g['Rank_Sum'] == max_rank).astype(int)

        # --- 方法 2: 百分比制 (Percentage Method) ---
        # 评委百分比
        total_judge = g['Judge_Score'].sum()
        if total_judge == 0: total_judge = 1
        g['Pct_Judge'] = (g['Judge_Score'] / total_judge) * 100
        
        # 粉丝百分比 (重新归一化)
        total_fan = g['Fan_Share'].sum()
        if total_fan == 0: total_fan = 1
        g['Pct_Fan'] = (g['Fan_Share'] / total_fan) * 100
        
        # 总百分比 (50/50)
        g['Pct_Total'] = g['Pct_Judge'] + g['Pct_Fan']
        # 模拟排名 (Pct_Total 降序)
        g['Final_Place_PctMethod'] = g['Pct_Total'].rank(ascending=False, method='min')
        # 标记淘汰 (Pct_Total 最小者)
        min_pct = g['Pct_Total'].min()
        g['Eliminated_By_Pct'] = (g['Pct_Total'] == min_pct).astype(int)

        results.append(g)
        
    df_sim = pd.concat(results)
    print("✅ 模拟完成。")
    return df_sim

def analyze_differences(df_sim):
    """对比分析：翻转率与偏差"""
    print(f"\n[{pd.Timestamp.now()}] 正在分析差异...")
    
    disagreements = []
    stats = {'Total_Weeks': 0, 'Rank_Saved_FanFav': 0, 'Pct_Saved_FanFav': 0}
    
    groups = df_sim.groupby(['Season', 'Week'])
    
    for (season, week), g in groups:
        # 找出被各方法“宣判淘汰”的人
        elim_rank = set(g[g['Eliminated_By_Rank'] == 1]['Name'])
        elim_pct = set(g[g['Eliminated_By_Pct'] == 1]['Name'])
        
        # 如果判罚结果不一致
        if elim_rank != elim_pct:
            stats['Total_Weeks'] += 1
            
            # 谁被 Rank 方法救了？(在 Pct 中死，在 Rank 中活)
            saved_by_rank = elim_pct - elim_rank
            # 谁被 Pct 方法救了？
            saved_by_pct = elim_rank - elim_pct
            
            row = {
                'Season': season, 'Week': week,
                'Eliminated_RankMode': list(elim_rank),
                'Eliminated_PctMode': list(elim_pct),
                'Saved_By_Rank': list(saved_by_rank),
                'Saved_By_Pct': list(saved_by_pct)
            }
            disagreements.append(row)
            
            # 简单统计：被救的人是不是高人气选手？(假设被救者中任意一人粉丝分较高即算)
            # 这里简化逻辑，只统计次数
            if saved_by_rank: stats['Rank_Saved_FanFav'] += 1
            if saved_by_pct: stats['Pct_Saved_FanFav'] += 1

    df_diff = pd.DataFrame(disagreements)
    
    # 计算相关性
    # RankMethod: 值越小越好 (1st)。 FanRank: 值越小越好 (1st)。 -> 正相关
    corr_rank = df_sim['Final_Place_RankMethod'].corr(df_sim['Rank_Fan'])
    # PctMethod: 值越小越好 (1st)。 FanRank: 值越小越好。 -> 正相关
    corr_pct = df_sim['Final_Place_PctMethod'].corr(df_sim['Rank_Fan'])
    
    print(f"全局相关性 (与纯粉丝排名的吻合度):")
    print(f"  Rank Method: {corr_rank:.4f}")
    print(f"  Pct Method:  {corr_pct:.4f}")
    
    return df_sim, df_diff, stats, (corr_rank, corr_pct)

def export_results(df_sim, df_diff, stats, corrs):
    """导出结果"""
    print(f"\n[{pd.Timestamp.now()}] 正在导出结果...")
    
    # 1. 详细表
    df_sim.to_csv('Voting_Method_Simulation_Full.csv', index=False)
    
    # 2. 差异表
    if not df_diff.empty:
        df_diff.to_csv('Voting_Method_Differences.csv', index=False)
        print("✅ 已保存: Voting_Method_Differences.csv (包含争议判罚详情)")
    
    # 3. 摘要报告
    with open('Method_Comparison_Summary.txt', 'w') as f:
        f.write("=== Voting Method Comparison Report ===\n")
        f.write(f"Total Weeks Analyzed: {len(df_sim['Season'].unique())} seasons\n")
        f.write(f"Weeks with Different Elimination Outcomes: {stats['Total_Weeks']}\n\n")
        f.write("=== Bias Analysis ===\n")
        f.write(f"Correlation with Fan Rank (Rank Method): {corrs[0]:.4f}\n")
        f.write(f"Correlation with Fan Rank (Pct Method):  {corrs[1]:.4f}\n")
        if corrs[0] > corrs[1]:
            f.write("-> Rank Method is closer to pure fan popularity.\n")
        else:
            f.write("-> Percentage Method is closer to pure fan popularity.\n")
    print("✅ 已保存: Method_Comparison_Summary.txt")

    # 4. 可视化
    if not df_diff.empty:
        plt.figure(figsize=(10, 6))
        # 选取差异最大的赛季展示
        top_s = df_diff['Season'].value_counts().idxmax()
        plot_data = df_sim[df_sim['Season'] == top_s]
        
        sns.scatterplot(data=plot_data, x='Final_Place_RankMethod', y='Final_Place_PctMethod', 
                        hue='Is_Eliminated', size='Fan_Share', sizes=(20, 200), alpha=0.7)
        plt.plot([0, 15], [0, 15], 'r--', alpha=0.5)
        plt.title(f'Rank vs Pct Method Placement (Season {top_s})')
        plt.xlabel('Place (Rank Method)')
        plt.ylabel('Place (Pct Method)')
        plt.tight_layout()
        plt.savefig('Method_Comparison_Scatter.png', dpi=300)
        print("✅ 已保存: Method_Comparison_Scatter.png")

def main():
    try:
        df = load_data()
        df_sim = simulate_methods(df)
        df_sim, df_diff, stats, corrs = analyze_differences(df_sim)
        export_results(df_sim, df_diff, stats, corrs)
        print("\n=== 全部完成 ===")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
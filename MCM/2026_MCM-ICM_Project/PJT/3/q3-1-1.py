import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
import os
import glob
import warnings

# ================= 配置区域 =================
# 自动文件匹配逻辑，无需手动修改
# ===========================================

# 设置绘图风格
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

def auto_find_files():
    """
    智能查找文件：
    1. 背景数据 (Processed Data): 提供 Age, Partner, Country
    2. 预测结果 (Predicted Votes): 提供 Vote_Share_Hat, Judge_Score
    """
    print(f"📂 当前工作目录: {os.getcwd()}")
    all_files = glob.glob("*.csv") + glob.glob("*.xlsx")
    
    bg_file = None
    res_file = None
    
    # 优先级匹配
    for f in all_files:
        if f.startswith('~$'): continue
        f_lower = f.lower()
        
        # 匹配结果文件 (优先匹配 predicted_vote_shares)
        if 'predicted_vote' in f_lower and 'sorted' not in f_lower:
            res_file = f
        
        # 匹配背景文件 (Processed Data)
        if 'processed' in f_lower and 'data' in f_lower and 'predicted' not in f_lower:
            bg_file = f
            
    # 如果没找到，尝试宽泛匹配
    if not res_file:
        cands = [f for f in all_files if 'vote_share' in f.lower() or 'ep_' in f.lower()]
        if cands: res_file = cands[0]
        
    if not bg_file:
        cands = [f for f in all_files if 'data' in f.lower() and 'processed' in f.lower()]
        if cands: bg_file = cands[0]

    print(f"✅ 锁定背景文件 (Source of Age/Partner): {bg_file}")
    print(f"✅ 锁定结果文件 (Source of Votes): {res_file}")
    
    return bg_file, res_file

def load_and_merge_data():
    """加载并合并数据"""
    print(f"\n[{pd.Timestamp.now()}] 正在加载并合并数据...")
    bg_path, res_path = auto_find_files()
    
    if not bg_path or not res_path:
        print("❌ 错误: 缺少必要文件。请确保目录下包含 Processed Data 和 Predicted Votes 文件。")
        return None

    # 读取文件工具函数
    def read_f(p): 
        if p.endswith('.xlsx'): return pd.read_excel(p)
        return pd.read_csv(p)

    try:
        df_bg = read_f(bg_path) # 背景
        df_res = read_f(res_path) # 结果
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return None

    # --- 1. 规范化列名 ---
    df_bg.columns = [c.strip().lower() for c in df_bg.columns]
    df_res.columns = [c.strip().lower() for c in df_res.columns]

    # --- 2. 准备合并键 (Season + Name) ---
    # 寻找背景文件中的列
    bg_name = [c for c in df_bg.columns if 'name' in c][0]
    bg_season = [c for c in df_bg.columns if 'season' in c][0]
    
    # 寻找结果文件中的列
    res_name = [c for c in df_res.columns if 'name' in c][0]
    res_season = [c for c in df_res.columns if 'season' in c][0]
    
    # 创建统一的 join_name
    df_bg['join_name'] = df_bg[bg_name].astype(str).str.strip().str.lower()
    df_res['join_name'] = df_res[res_name].astype(str).str.strip().str.lower()
    
    # 确保 Season 类型一致
    df_bg['join_season'] = df_bg[bg_season].astype(int)
    df_res['join_season'] = df_res[res_season].astype(int)

    # --- 3. 提取背景特征 (从 Processed Data) ---
    # 我们只需要: Age, Partner, Country (Industry 结果文件里可能有，优先用结果文件的)
    def find_col(df, key):
        c = [x for x in df.columns if key in x]
        return c[0] if c else None

    col_age = find_col(df_bg, 'age')
    col_partner = find_col(df_bg, 'partner')
    col_country = find_col(df_bg, 'country') or find_col(df_bg, 'homestate')
    
    print(f"映射背景列: Age->{col_age}, Partner->{col_partner}, Country->{col_country}")
    
    # 选取静态列，去重 (因为一个选手在一个赛季有多行，背景信息是一样的)
    static_cols = ['join_name', 'join_season', col_age, col_partner, col_country]
    df_static = df_bg[static_cols].drop_duplicates(subset=['join_name', 'join_season']).copy()
    
    # 重命名
    df_static.columns = ['join_name', 'join_season', 'Age', 'Partner', 'Country']

    # --- 4. 合并 ---
    # 左连接: 保留预测结果中的每一行 (每周数据)
    df_full = pd.merge(df_res, df_static, on=['join_season', 'join_name'], how='left')
    
    # --- 5. 最终清洗 ---
    # 目标变量映射
    # 你的新文件列名可能是: judge_score_total, vote_share_hat
    target_judge = 'judge_score_total'
    target_fan = 'vote_share_hat'
    
    # 检查列是否存在
    if target_judge not in df_full.columns or target_fan not in df_full.columns:
        print(f"⚠️ 警告: 目标列名不匹配。当前列: {df_full.columns.tolist()}")
        # 尝试自动修正
        target_judge = [c for c in df_full.columns if 'judge' in c and 'score' in c][0]
        target_fan = [c for c in df_full.columns if 'vote' in c and ('hat' in c or 'est' in c)][0]
        print(f"自动修正为: Judge->{target_judge}, Fan->{target_fan}")

    # 重命名为标准字段
    df_full.rename(columns={target_judge: 'Judge_Score', target_fan: 'Fan_Vote'}, inplace=True)
    
    # 确保 Industry 存在 (如果结果文件没 Industry，去背景文件找)
    if 'industry' not in df_full.columns:
        # 尝试从背景找
        col_ind = find_col(df_bg, 'industry')
        if col_ind:
            df_ind = df_bg[['join_name', 'join_season', col_ind]].drop_duplicates()
            df_full = pd.merge(df_full, df_ind, on=['join_name', 'join_season'], how='left')
            df_full.rename(columns={col_ind: 'Industry'}, inplace=True)
    else:
        df_full.rename(columns={'industry': 'Industry'}, inplace=True)

    # 删除缺失关键信息的行
    before = len(df_full)
    df_full.dropna(subset=['Age', 'Partner', 'Industry', 'Judge_Score', 'Fan_Vote'], inplace=True)
    print(f"✅ 合并完成: {before} -> {len(df_full)} 行有效数据")
    
    return df_full

def perform_quantification(df):
    """核心量化分析"""
    print(f"\n[{pd.Timestamp.now()}] 开始多因子回归分析...")

    # 1. 标准化 (Z-Score) 以便比较系数
    df['Judge_Z'] = (df['Judge_Score'] - df['Judge_Score'].mean()) / df['Judge_Score'].std()
    df['Fan_Z'] = (df['Fan_Vote'] - df['Fan_Vote'].mean()) / df['Fan_Vote'].std()
    
    # 2. 特征工程
    # Is_US
    df['Is_US'] = df['Country'].astype(str).apply(lambda x: 1 if 'United States' in x or 'USA' in x else 0)
    # 赛季作为分类变量 (控制时间通胀)
    # Industry, Partner 作为分类变量
    
    # 3. OLS 回归
    # 公式: Score ~ Age + Industry + Partner + Season
    formula = "Age + C(Industry) + C(Partner) + C(join_season)"
    
    print("正在拟合评委评分模型 (OLS)...")
    try:
        model_judge = smf.ols(f"Judge_Z ~ {formula}", data=df).fit()
        print("正在拟合粉丝投票模型 (OLS)...")
        model_fan = smf.ols(f"Fan_Z ~ {formula}", data=df).fit()
    except Exception as e:
        print(f"❌ OLS 建模失败: {e}")
        return None, None, None, None, None

    # 4. LightGBM (特征重要性)
    print("正在计算特征重要性 (LightGBM)...")
    features = ['Age', 'Industry', 'Partner', 'join_season', 'Is_US']
    X = df[features].copy()
    
    # Label Encoding
    for col in ['Industry', 'Partner']:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        
    params = {'objective': 'regression', 'metric': 'rmse', 'verbosity': -1, 'seed': 42}
    
    bst_judge = lgb.train(params, lgb.Dataset(X, label=df['Judge_Score']), num_boost_round=100)
    bst_fan = lgb.train(params, lgb.Dataset(X, label=df['Fan_Vote']), num_boost_round=100)
    
    return model_judge, model_fan, bst_judge, bst_fan, features

def save_and_plot_results(model_j, model_f, bst_j, bst_f, feat_names):
    """导出结果与绘图"""
    print(f"\n[{pd.Timestamp.now()}] 正在导出结果...")
    
    if not model_j: return

    # --- 1. 导出系数表 (Full CSV) ---
    def extract_coefs(model, prefix):
        return pd.DataFrame({
            'Factor': model.params.index,
            f'{prefix}_Coef': model.params.values,
            f'{prefix}_Pval': model.pvalues.values
        })
    
    df_coef = pd.merge(extract_coefs(model_j, 'Judge'), extract_coefs(model_f, 'Fan'), on='Factor', how='outer')
    # 过滤掉 Intercept 和 Season (太多且不关注)
    df_coef = df_coef[~df_coef['Factor'].str.contains('Intercept|join_season')]
    df_coef.to_csv('Factor_Quantification_Full.csv', index=False)
    print("✅ 已保存系数表: Factor_Quantification_Full.csv")

    # --- 2. 导出重要性排序 (Ranking CSV) ---
    imp_df = pd.DataFrame({
        'Feature': feat_names,
        'Judge_Importance': bst_j.feature_importance(importance_type='gain'),
        'Fan_Importance': bst_f.feature_importance(importance_type='gain')
    })
    # 归一化
    imp_df['Judge_Importance'] /= imp_df['Judge_Importance'].sum()
    imp_df['Fan_Importance'] /= imp_df['Fan_Importance'].sum()
    imp_df.to_csv('Feature_Importance_Ranking.csv', index=False)
    print("✅ 已保存重要性表: Feature_Importance_Ranking.csv")

    # --- 3. 绘制蝴蝶图 (Butterfly Chart) ---
    # 选取差异最大或影响最大的 Top 20 因子
    df_plot = df_coef.copy()
    df_plot['Total_Impact'] = df_plot['Judge_Coef'].abs() + df_plot['Fan_Coef'].abs()
    df_plot = df_plot.sort_values('Total_Impact', ascending=False).head(20)
    
    # 简化名字用于绘图
    df_plot['Clean_Name'] = df_plot['Factor'].apply(
        lambda x: x.replace('C(Industry)[T.', '').replace('C(Partner)[T.', '').replace(']', '')
    )

    plt.figure(figsize=(14, 10))
    y = np.arange(len(df_plot))
    height = 0.35
    
    # 评委向左，粉丝向右
    plt.barh(y, df_plot['Judge_Coef'], height, label='Judge Sensitivity', color='#1f77b4', align='center')
    plt.barh(y, df_plot['Fan_Coef'], height, label='Fan Sensitivity', color='#ff7f0e', align='edge') 
    # 为了更好看，改为上下并排
    plt.clf()
    plt.figure(figsize=(12, 12))
    
    plt.barh(y - height/2, df_plot['Judge_Coef'], height, label='Judge Influence', color='#4c72b0')
    plt.barh(y + height/2, df_plot['Fan_Coef'], height, label='Fan Influence', color='#dd8452')
    
    plt.yticks(y, df_plot['Clean_Name'], fontsize=10)
    plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
    plt.xlabel('Standardized Effect Size (Beta Coefficient)')
    plt.title('Impact of Contestant Factors: Judges vs. Fans\n(Who cares more about what?)')
    plt.legend()
    plt.tight_layout()
    
    plt.savefig('Factor_Analysis_Butterfly_Chart.png', dpi=300)
    print("✅ 已保存可视化图: Factor_Analysis_Butterfly_Chart.png")

def main():
    df = load_and_merge_data()
    if df is not None:
        m_j, m_f, b_j, b_f, feats = perform_quantification(df)
        save_and_plot_results(m_j, m_f, b_j, b_f, feats)
        print("\n=== 分析全部完成 ===")

if __name__ == "__main__":
    main()
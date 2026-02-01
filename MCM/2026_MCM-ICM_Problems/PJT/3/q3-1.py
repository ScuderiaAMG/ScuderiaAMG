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
# 自动扫描模式，无需修改
# ===========================================

# 设置绘图风格
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

def auto_find_files():
    """智能查找文件"""
    print(f"📂 当前工作目录: {os.getcwd()}")
    all_files = glob.glob("*.csv") + glob.glob("*.xlsx")
    
    bg_file = None
    res_file = None
    
    for f in all_files:
        if f.startswith('~$'): continue
        f_lower = f.lower()
        if 'data' in f_lower and ('processed' in f_lower or 'mcm' in f_lower) and 'result' not in f_lower:
            bg_file = f
        elif 'result' in f_lower or 'ep_' in f_lower or 'final' in f_lower:
            res_file = f
            
    if not bg_file:
        cands = [f for f in all_files if 'data' in f.lower()]
        if cands: bg_file = cands[0]
    if not res_file:
        cands = [f for f in all_files if 'ep' in f.lower()]
        if cands: res_file = cands[0]

    print(f"✅ 锁定背景文件: {bg_file}")
    print(f"✅ 锁定结果文件: {res_file}")
    return bg_file, res_file

def load_and_merge_data():
    """加载并清洗数据 (含冲突解决)"""
    print(f"\n[{pd.Timestamp.now()}] 正在加载数据...")
    bg_path, res_path = auto_find_files()
    
    if not bg_path or not res_path:
        print("❌ 错误: 未能找到对应文件。")
        return None

    # 读取
    def read_f(p): return pd.read_excel(p) if p.endswith('.xlsx') else pd.read_csv(p)
    df_bg = read_f(bg_path)
    df_res = read_f(res_path)

    # 1. 规范化背景数据列名
    df_bg.columns = [c.strip().lower() for c in df_bg.columns]
    
    # 2. 寻找背景特征列
    def find_col(df, keyword):
        matches = [c for c in df.columns if keyword in c]
        return matches[0] if matches else None

    col_season = find_col(df_bg, 'season')
    col_age = find_col(df_bg, 'age')
    col_industry = find_col(df_bg, 'industry')
    col_partner = find_col(df_bg, 'partner')
    col_country = find_col(df_bg, 'country') or find_col(df_bg, 'homestate')

    print(f"映射关系: Age->{col_age}, Industry->{col_industry}, Partner->{col_partner}")

    # 提取纯净的背景数据
    cols_to_keep = ['join_name', 'Season', 'Age', 'Industry', 'Partner', 'Country']
    
    # 构造 Join Name
    df_bg['join_name'] = df_bg['celebrity_name'].astype(str).str.strip().str.lower()
    
    df_static = pd.DataFrame()
    df_static['join_name'] = df_bg['join_name']
    df_static['Season'] = df_bg[col_season]
    df_static['Age'] = df_bg[col_age]
    df_static['Industry'] = df_bg[col_industry]
    df_static['Partner'] = df_bg[col_partner]
    df_static['Country'] = df_bg[col_country]

    # 3. 处理结果数据 (Results)
    # 寻找名字列
    res_name_col = 'celebrity_name'
    for col in df_res.columns:
        if 'name' in col.lower() and 'celebrity' in col.lower():
            res_name_col = col
            break
    df_res['join_name'] = df_res[res_name_col].astype(str).str.strip().str.lower()

    # --- 关键修复: 防止列名冲突 ---
    # 在合并前，删除 df_res 中可能存在的与 df_static 重名的列 (Season 和 join_name 除外)
    cols_to_drop = [c for c in ['Age', 'Industry', 'Partner', 'Country'] if c in df_res.columns]
    if cols_to_drop:
        print(f"⚠️ 检测到结果文件中包含冗余列，正在移除以避免冲突: {cols_to_drop}")
        df_res.drop(columns=cols_to_drop, inplace=True)
    # ---------------------------

    # 4. 合并
    if 'Season' in df_res.columns:
        df_res['Season'] = df_res['Season'].astype(int)
        df_static['Season'] = df_static['Season'].astype(int)
        df_full = pd.merge(df_res, df_static, on=['Season', 'join_name'], how='left')
    else:
        df_full = pd.merge(df_res, df_static, on=['join_name'], how='left')

    # 5. 最终清洗
    print(f"合并后列名: {df_full.columns.tolist()}") # Debug info
    df_full.dropna(subset=['Age', 'Industry', 'Partner'], inplace=True)
    print(f"✅ 数据合并完成，有效样本数: {len(df_full)}")

    return df_full

def perform_quantification(df):
    """核心量化分析"""
    print(f"\n[{pd.Timestamp.now()}] 开始量化因素分析...")

    # 确保数值型
    df['Judge_Score'] = pd.to_numeric(df['Judge_Score'], errors='coerce')
    df['Estimated_Vote_Share'] = pd.to_numeric(df['Estimated_Vote_Share'], errors='coerce')
    df.dropna(subset=['Judge_Score', 'Estimated_Vote_Share'], inplace=True)

    # 标准化
    df['Judge_Z'] = (df['Judge_Score'] - df['Judge_Score'].mean()) / df['Judge_Score'].std()
    df['Fan_Z'] = (df['Estimated_Vote_Share'] - df['Estimated_Vote_Share'].mean()) / df['Estimated_Vote_Share'].std()
    
    # 特征处理
    df['Is_US'] = df['Country'].astype(str).apply(lambda x: 1 if 'United States' in x or 'USA' in x else 0)

    # OLS
    # 使用 Q("Column Name") 处理可能包含空格或特殊字符的列名，或者重命名
    # 这里我们已经重命名为简单的 English，可以直接用
    formula = "Age + C(Industry) + C(Partner) + C(Season)"
    
    print("拟合评委模型 (OLS)...")
    try:
        model_judge = smf.ols(f"Judge_Z ~ {formula}", data=df).fit()
        print("拟合粉丝模型 (OLS)...")
        model_fan = smf.ols(f"Fan_Z ~ {formula}", data=df).fit()
    except Exception as e:
        print(f"⚠️ OLS 拟合失败 (可能是类别过多或奇异矩阵): {e}")
        model_judge, model_fan = None, None

    # LightGBM
    print("训练 LightGBM...")
    features = ['Age', 'Industry', 'Partner', 'Season', 'Is_US']
    X = df[features].copy()
    
    for col in ['Industry', 'Partner']:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        
    params = {'objective': 'regression', 'metric': 'rmse', 'verbosity': -1, 'seed': 42}
    bst_judge = lgb.train(params, lgb.Dataset(X, label=df['Judge_Score']), num_boost_round=100)
    bst_fan = lgb.train(params, lgb.Dataset(X, label=df['Estimated_Vote_Share']), num_boost_round=100)

    return model_judge, model_fan, bst_judge, bst_fan, features

def save_and_plot_results(model_j, model_f, bst_j, bst_f, feat_names):
    """导出结果"""
    print(f"\n[{pd.Timestamp.now()}] 正在导出结果...")

    # 1. 导出系数表 (CSV)
    if model_j and model_f:
        def get_coefs(model, prefix):
            return pd.DataFrame({
                'Factor': model.params.index,
                f'{prefix}_Coef': model.params.values,
                f'{prefix}_Pval': model.pvalues.values
            })

        df_coef = pd.merge(get_coefs(model_j, 'Judge'), get_coefs(model_f, 'Fan'), on='Factor', how='outer')
        # 过滤掉非核心因子
        df_coef = df_coef[~df_coef['Factor'].str.contains('Intercept|Season')]
        df_coef.to_csv('Factor_Quantification_Full.csv', index=False)
        print("✅ 已保存: Factor_Quantification_Full.csv")

        # 蝴蝶图
        df_plot = df_coef.copy()
        df_plot['Total_Impact'] = df_plot['Judge_Coef'].abs() + df_plot['Fan_Coef'].abs()
        df_plot = df_plot.sort_values('Total_Impact', ascending=False).head(20)
        df_plot['Clean_Name'] = df_plot['Factor'].apply(lambda x: x.replace('C(Industry)[T.', '').replace('C(Partner)[T.', '').replace(']', ''))
        
        plt.figure(figsize=(12, 10))
        y = np.arange(len(df_plot))
        plt.barh(y - 0.17, df_plot['Judge_Coef'], 0.35, label='Judge', color='#4c72b0')
        plt.barh(y + 0.17, df_plot['Fan_Coef'], 0.35, label='Fan', color='#dd8452')
        plt.yticks(y, df_plot['Clean_Name'])
        plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
        plt.title('Top 20 Factors: Judges vs Fans')
        plt.legend()
        plt.tight_layout()
        plt.savefig('Factor_Analysis_Butterfly_Chart.png', dpi=300)
        print("✅ 已保存: Factor_Analysis_Butterfly_Chart.png")

    # 2. 导出重要性 (CSV)
    imp_df = pd.DataFrame({
        'Feature': feat_names,
        'Judge_Importance': bst_j.feature_importance(importance_type='gain'),
        'Fan_Importance': bst_f.feature_importance(importance_type='gain')
    })
    imp_df['Judge_Importance'] /= imp_df['Judge_Importance'].sum()
    imp_df['Fan_Importance'] /= imp_df['Fan_Importance'].sum()
    imp_df.to_csv('Feature_Importance_Ranking.csv', index=False)
    print("✅ 已保存: Feature_Importance_Ranking.csv")

def main():
    df = load_and_merge_data()
    if df is not None:
        m_j, m_f, b_j, b_f, feats = perform_quantification(df)
        save_and_plot_results(m_j, m_f, b_j, b_f, feats)
        print("\n=== 全部完成 ===")

if __name__ == "__main__":
    main()
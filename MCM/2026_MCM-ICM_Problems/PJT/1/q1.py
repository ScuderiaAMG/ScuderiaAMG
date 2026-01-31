import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess():
    # 读取原始比赛数据
    df = pd.read_excel('2026_MCM_Problem_C_Processed_Data.xlsx', sheet_name='Sheet1')
    
    # 读取已估算的投票份额数据
    vote_data = pd.read_excel('EP_FROM_Model_Final_Results.xlsx')
    
    # 清洗 Eliminated_Week 列
    df['Eliminated_Week_Clean'] = df['Eliminated_Week'].astype(str).str.strip().str.lower()
    df['Eliminated_Week_Clean'] = df['Eliminated_Week_Clean'].replace({
        '决赛': '99', '决赛选手': '99', 'winner': '99', 'champion': '99',
        '退赛': '98', 'withdrew': '98', 'quit': '98',
        'na': '97', 'n/a': '97', '': '97', 'nan': '97', 'none': '97'
    })
    df['Eliminated_Week_Clean'] = pd.to_numeric(df['Eliminated_Week_Clean'], errors='coerce').fillna(97).astype(int)
    
    # 创建长格式数据
    records = []
    for idx, row in df.iterrows():
        celebrity = row['celebrity_name']
        season = row['season']
        industry = row['celebrity_industry'] if pd.notna(row['celebrity_industry']) else 'Unknown'
        age = row['celebrity_age_during_season'] if pd.notna(row['celebrity_age_during_season']) else 30
        eliminated_week = row['Eliminated_Week_Clean']
        
        for week in range(1, 12):
            judge_cols = [f'week{week}_judge{i}_score' for i in range(1, 5)]
            scores = []
            for col in judge_cols:
                if col in df.columns:
                    val = row[col]
                    if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
                        scores.append(val)
            
            if scores:
                judge_total = sum(scores)
                is_eliminated = 1 if (week == eliminated_week and eliminated_week < 97) else 0
                
                # 获取估算的投票份额
                vote_record = vote_data[
                    (vote_data['Season'] == season) & 
                    (vote_data['Week'] == week) & 
                    (vote_data['Celebrity_Name'] == celebrity)
                ]
                vote_share = vote_record['Estimated_Vote_Share'].values[0] if len(vote_record) > 0 else np.nan
                
                records.append({
                    'season': season,
                    'week': week,
                    'celebrity_name': celebrity,
                    'industry': industry,
                    'age': age,
                    'judge_score_total': judge_total,
                    'is_eliminated': is_eliminated,
                    'vote_share': vote_share,
                    'eliminated_week': eliminated_week
                })
    
    long_df = pd.DataFrame(records)
    
    # 特征工程：行业独热编码
    industry_dummies = pd.get_dummies(long_df['industry'], prefix='industry')
    long_df = pd.concat([long_df, industry_dummies], axis=1)
    
    # 添加趋势特征
    long_df = long_df.sort_values(['celebrity_name', 'week']).reset_index(drop=True)
    long_df['prev_week_score'] = long_df.groupby('celebrity_name')['judge_score_total'].shift(1)
    long_df['score_change'] = long_df['judge_score_total'] - long_df['prev_week_score']
    long_df['rolling_avg_2w'] = long_df.groupby('celebrity_name')['judge_score_total'].transform(
        lambda x: x.rolling(window=2, min_periods=1).mean()
    )
    
    # 填充缺失值
    long_df['prev_week_score'] = long_df['prev_week_score'].fillna(long_df['judge_score_total'])
    long_df['score_change'] = long_df['score_change'].fillna(0)
    long_df['rolling_avg_2w'] = long_df['rolling_avg_2w'].fillna(long_df['judge_score_total'])
    
    # 准备训练数据
    train_df = long_df[long_df['vote_share'].notna() & (long_df['vote_share'] > 0)].copy()
    
    base_features = [
        'season', 'week', 'age', 'judge_score_total', 
        'prev_week_score', 'score_change', 'rolling_avg_2w', 'is_eliminated'
    ]
    feature_cols = base_features + list(industry_dummies.columns)
    
    # 确保所有特征列存在
    for col in feature_cols:
        if col not in train_df.columns:
            train_df[col] = 0
    
    X = train_df[feature_cols]
    y = train_df['vote_share']
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, long_df, feature_cols

def train_and_predict(X_train, X_test, y_train, y_test, long_df, feature_cols):
    # XGBoost 模型（移除 verbose 参数确保兼容性）
    print("Training XGBoost model...")
    xgb_model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    try:
        xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    except TypeError:
        xgb_model.fit(X_train, y_train)  # 回退到基础训练
    
    # LightGBM 模型（移除 verbose 参数）
    print("Training LightGBM model...")
    lgb_model = LGBMRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    try:
        lgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=-1)
    except TypeError:
        try:
            lgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
        except TypeError:
            lgb_model.fit(X_train, y_train)  # 最终回退
    
    # 评估模型
    xgb_pred = xgb_model.predict(X_test)
    lgb_pred = lgb_model.predict(X_test)
    
    xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_pred))
    lgb_rmse = np.sqrt(mean_squared_error(y_test, lgb_pred))
    xgb_r2 = r2_score(y_test, xgb_pred)
    lgb_r2 = r2_score(y_test, lgb_pred)
    
    print(f"XGBoost - RMSE: {xgb_rmse:.4f}, R²: {xgb_r2:.4f}")
    print(f"LightGBM - RMSE: {lgb_rmse:.4f}, R²: {lgb_r2:.4f}")
    
    # 选择最佳模型
    if xgb_rmse < lgb_rmse:
        best_model = xgb_model
        model_name = "XGBoost"
        best_rmse = xgb_rmse
    else:
        best_model = lgb_model
        model_name = "LightGBM"
        best_rmse = lgb_rmse
    print(f"\n✓ Selected {model_name} as best model (RMSE: {best_rmse:.4f})")
    
    # 预测所有参赛者
    pred_df = long_df.copy()
    pred_df['prev_week_score'] = pred_df['prev_week_score'].fillna(pred_df['judge_score_total'])
    pred_df['score_change'] = pred_df['score_change'].fillna(0)
    pred_df['rolling_avg_2w'] = pred_df['rolling_avg_2w'].fillna(pred_df['judge_score_total'])
    
    # 确保所有特征列存在
    for col in feature_cols:
        if col not in pred_df.columns:
            pred_df[col] = 0
    
    # 预测
    X_full = pred_df[feature_cols]
    pred_df['vote_hat'] = best_model.predict(X_full)
    
    # 按赛季和周归一化
    def normalize_group(group):
        total = group['vote_hat'].sum()
        if total > 1e-8:
            group['vote_share_hat'] = group['vote_hat'] / total
        else:
            group['vote_share_hat'] = 1.0 / len(group) if len(group) > 0 else 0
        return group
    
    pred_df = pred_df.groupby(['season', 'week'], group_keys=False).apply(normalize_group).reset_index(drop=True)
    
    # 添加不确定性估计
    pred_df['uncertainty'] = 0.05
    pred_df.loc[pred_df['is_eliminated'] == 1, 'uncertainty'] = 0.08
    
    # 生成最终结果
    result_df = pred_df[[
        'season', 'week', 'celebrity_name', 'industry', 'judge_score_total',
        'vote_share', 'vote_share_hat', 'uncertainty', 'is_eliminated', 'eliminated_week'
    ]].copy()
    
    # 保存结果
    result_df.to_csv('predicted_vote_shares.csv', index=False)
    print(f"\n✓ Prediction complete! Results saved to 'predicted_vote_shares.csv'")
    print(f"✓ Total predictions: {len(result_df)} samples")
    
    return result_df, best_model, model_name

if __name__ == "__main__":
    print("=" * 70)
    print(" DWTS Vote Share Prediction System (Machine Learning Regression) ")
    print("=" * 70)
    
    try:
        # 数据预处理
        X_train, X_test, y_train, y_test, long_df, feature_cols = load_and_preprocess()
        print(f"✓ Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        print(f"✓ Features used: {len(feature_cols)}")
        
        # 模型训练与预测
        result_df, model, model_name = train_and_predict(
            X_train, X_test, y_train, y_test, long_df, feature_cols
        )
        
        # 显示示例结果
        print("\n✓ Top 10 predictions by vote share:")
        sample = result_df.sort_values('vote_share_hat', ascending=False).head(10)
        print(sample[['season', 'week', 'celebrity_name', 'judge_score_total', 'vote_share_hat']].to_string(index=False))
        
        # 保存排序结果
        result_df_sorted = result_df.sort_values(['season', 'week', 'vote_share_hat'], ascending=[True, True, False])
        result_df_sorted.to_csv('predicted_vote_shares_sorted.csv', index=False)
        print("\n✓ Sorted results saved to 'predicted_vote_shares_sorted.csv'")
        
        # 保存模型摘要
        with open('model_summary.txt', 'w', encoding='utf-8') as f:
            f.write(f"Best Model: {model_name}\n")
            f.write(f"Features Used: {len(feature_cols)}\n")
            f.write(f"Training Samples: {len(X_train)}\n")
            f.write(f"Test RMSE: {min(np.sqrt(mean_squared_error(y_test, model.predict(X_test))), 999):.4f}\n")
        
        print("\n" + "=" * 70)
        print(" Execution completed successfully! ")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
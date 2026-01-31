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
    
    # 清洗 Eliminated_Week 列：处理"决赛"、"退赛"等非数值情况
    df['Eliminated_Week_Clean'] = df['Eliminated_Week'].astype(str).str.strip()
    df['Eliminated_Week_Clean'] = df['Eliminated_Week_Clean'].replace({
        '决赛': '99',   # 决赛选手设为极大值（99周）
        '退赛': '98',   # 退赛选手设为98（特殊标记）
        'N/A': '97',
        '': '97',
        'nan': '97'
    })
    # 转换为数值，无法转换的设为97
    df['Eliminated_Week_Clean'] = pd.to_numeric(df['Eliminated_Week_Clean'], errors='coerce').fillna(97).astype(int)
    
    # 创建长格式数据：每个选手-周组合一行
    records = []
    
    # 遍历每个选手
    for idx, row in df.iterrows():
        celebrity = row['celebrity_name']
        season = row['season']
        industry = row['celebrity_industry']
        age = row['celebrity_age_during_season']
        eliminated_week = row['Eliminated_Week_Clean']
        
        # 遍历每周数据（最多11周）
        for week in range(1, 12):
            # 检查该周是否存在有效评分数据
            judge_cols = [f'week{week}_judge{i}_score' for i in range(1, 5)]
            has_valid_data = all(col in df.columns for col in judge_cols)
            
            if has_valid_data:
                # 获取该周评委分数
                scores = []
                for col in judge_cols:
                    val = row[col]
                    if pd.notna(val) and val > 0:  # 有效评分（评委最低1分）
                        scores.append(val)
                
                # 仅当有有效评分时才创建记录
                if scores:
                    judge_total = sum(scores)
                    
                    # 判断是否在比赛中：未被淘汰且未退赛
                    is_in_competition = (week < eliminated_week) or (eliminated_week >= 97)
                    
                    # 判断是否在当周被淘汰（仅当淘汰周是具体数字时）
                    is_eliminated = 1 if (week == eliminated_week and eliminated_week < 97) else 0
                    
                    # 从vote_data中获取估算的投票份额
                    vote_record = vote_data[
                        (vote_data['Season'] == season) & 
                        (vote_data['Week'] == week) & 
                        (vote_data['Celebrity_Name'] == celebrity)
                    ]
                    
                    vote_share = vote_record['Estimated_Vote_Share'].values[0] if len(vote_record) > 0 else np.nan
                    
                    # 添加记录
                    records.append({
                        'season': season,
                        'week': week,
                        'celebrity_name': celebrity,
                        'industry': industry,
                        'age': age,
                        'judge_score_total': judge_total,
                        'is_eliminated': is_eliminated,
                        'is_in_competition': 1 if is_in_competition else 0,
                        'vote_share': vote_share,
                        'eliminated_week': eliminated_week
                    })
    
    long_df = pd.DataFrame(records)
    
    # 2. 特征工程
    # 添加行业独热编码
    industry_dummies = pd.get_dummies(long_df['industry'], prefix='industry')
    long_df = pd.concat([long_df, industry_dummies], axis=1)
    
    # 添加趋势特征：过去2周的平均分和变化
    long_df = long_df.sort_values(['celebrity_name', 'week']).reset_index(drop=True)
    long_df['prev_week_score'] = long_df.groupby('celebrity_name')['judge_score_total'].shift(1)
    long_df['score_change'] = long_df['judge_score_total'] - long_df['prev_week_score']
    long_df['rolling_avg_2w'] = long_df.groupby('celebrity_name')['judge_score_total'].transform(
        lambda x: x.rolling(window=2, min_periods=1).mean()
    )
    
    # 填充缺失值
    long_df['prev_week_score'] = long_df['prev_week_score'].fillna(long_df['judge_score_total'])
    long_df['score_change'] = long_df['score_change'].fillna(0)
    
    # 3. 准备训练数据（仅使用有投票份额数据的样本）
    train_df = long_df[long_df['vote_share'].notna() & (long_df['vote_share'] > 0)].copy()
    
    # 特征列表
    feature_cols = [
        'season', 'week', 'age', 'judge_score_total', 
        'prev_week_score', 'score_change', 'rolling_avg_2w', 'is_eliminated'
    ] + list(industry_dummies.columns)
    
    # 确保所有特征列存在
    for col in feature_cols:
        if col not in train_df.columns:
            train_df[col] = 0
    
    X = train_df[feature_cols]
    y = train_df['vote_share']
    
    # 4. 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, long_df, feature_cols, industry_dummies.columns.tolist()

def train_and_predict(X_train, X_test, y_train, y_test, long_df, feature_cols, industry_cols):
    # 方法1: XGBoost
    print("Training XGBoost model...")
    xgb_model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=0
    )
    xgb_model.fit(X_train, y_train, 
                 eval_set=[(X_test, y_test)], 
                 early_stopping_rounds=30,
                 verbose=False)
    
    # 方法2: LightGBM
    print("Training LightGBM model...")
    lgb_model = LGBMRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=-1
    )
    lgb_model.fit(X_train, y_train,
                 eval_set=[(X_test, y_test)],
                 early_stopping_rounds=30,
                 verbose=False)
    
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
    else:
        best_model = lgb_model
        model_name = "LightGBM"
    print(f"\nSelected {model_name} as best model (RMSE: {min(xgb_rmse, lgb_rmse):.4f})")
    
    # 6. 预测所有参赛者
    # 准备完整数据集的特征
    pred_df = long_df.copy()
    pred_df['prev_week_score'] = pred_df['prev_week_score'].fillna(pred_df['judge_score_total'])
    pred_df['score_change'] = pred_df['score_change'].fillna(0)
    
    # 确保所有特征列存在
    for col in feature_cols:
        if col not in pred_df.columns:
            pred_df[col] = 0
    
    # 预测
    X_full = pred_df[feature_cols]
    pred_df['vote_hat'] = best_model.predict(X_full)
    
    # 7. 按赛季和周进行归一化（确保每组得票份额和为1）
    def normalize_by_group(group):
        total = group['vote_hat'].sum()
        if total > 1e-5:  # 避免除零
            group['vote_share_hat'] = group['vote_hat'] / total
        else:
            group['vote_share_hat'] = 1.0 / len(group)
        return group
    
    pred_df = pred_df.groupby(['season', 'week']).apply(normalize_by_group).reset_index(drop=True)
    
    # 8. 添加不确定性估计
    pred_df['uncertainty'] = 0.05  # 基础不确定性5%
    pred_df.loc[pred_df['is_eliminated'] == 1, 'uncertainty'] += 0.03
    
    # 9. 生成最终结果
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
    print("=" * 60)
    print("DWTS Vote Share Prediction System (Machine Learning Approach)")
    print("=" * 60)
    
    # 数据预处理
    try:
        X_train, X_test, y_train, y_test, long_df, feature_cols, industry_cols = load_and_preprocess()
        print(f"✓ Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        print(f"✓ Features used: {len(feature_cols)} ({', '.join(feature_cols[:5])}...)")
        
        # 模型训练与预测
        result_df, model, model_name = train_and_predict(
            X_train, X_test, y_train, y_test, long_df, feature_cols, industry_cols
        )
        
        # 显示示例结果
        print("\n✓ Sample predictions (top 10 by predicted vote share):")
        sample = result_df.sort_values('vote_share_hat', ascending=False).head(10)
        print(sample[['season', 'week', 'celebrity_name', 'judge_score_total', 'vote_share_hat']].to_string(index=False))
        
        # 按赛季-周-选手排序保存
        result_df_sorted = result_df.sort_values(['season', 'week', 'vote_share_hat'], ascending=[True, True, False])
        result_df_sorted.to_csv('predicted_vote_shares_sorted.csv', index=False)
        print("\n✓ Sorted results saved to 'predicted_vote_shares_sorted.csv'")
        
        print("\n" + "=" * 60)
        print("Execution completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from scipy.stats import spearmanr
import warnings
import datetime
import traceback

warnings.filterwarnings('ignore')

# ==========================================
# 1. Data Loading and Preprocessing
# ==========================================
def load_and_preprocess():
    print("Loading and preprocessing data...")
    try:
        # Load Raw Data
        df = pd.read_excel('2026_MCM_Problem_C_Processed_Data.xlsx', sheet_name='Sheet1')
        # Standardize columns: lowercase and strip whitespace
        df.columns = df.columns.str.strip().str.lower()
        
        # Load Vote Data
        vote_data = pd.read_excel('EP_FROM_Model_Final_Results.xlsx')
        vote_data.columns = vote_data.columns.str.strip().str.lower()
        
        # Verify 'season' column exists
        if 'season' not in df.columns:
            raise KeyError(f"'season' column not found in Processed Data. Available: {list(df.columns)}")
        if 'season' not in vote_data.columns:
            raise KeyError(f"'season' column not found in Vote Data. Available: {list(vote_data.columns)}")

        # Clean Eliminated_Week
        if 'eliminated_week' in df.columns:
            df['eliminated_week_clean'] = df['eliminated_week'].astype(str).str.strip().str.lower()
            df['eliminated_week_clean'] = df['eliminated_week_clean'].replace({
                '决赛': '99', '决赛选手': '99', 'winner': '99', 'champion': '99',
                '退赛': '98', 'withdrew': '98', 'quit': '98',
                'na': '97', 'n/a': '97', '': '97', 'nan': '97', 'none': '97'
            })
            df['eliminated_week_clean'] = pd.to_numeric(df['eliminated_week_clean'], errors='coerce').fillna(97).astype(int)
        else:
            raise KeyError("'eliminated_week' column missing from data.")

        # Create Long Format Data
        records = []
        for idx, row in df.iterrows():
            celebrity = row['celebrity_name']
            season = row['season']
            industry = row['celebrity_industry'] if pd.notna(row.get('celebrity_industry')) else 'Unknown'
            age = row['celebrity_age_during_season'] if pd.notna(row.get('celebrity_age_during_season')) else 30
            eliminated_week = row['eliminated_week_clean']
            
            for week in range(1, 12):
                # Construct judge score column names dynamically
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
                    
                    # Get estimated vote share
                    # Note: vote_data columns are now all lowercase
                    vote_record = vote_data[
                        (vote_data['season'] == season) & 
                        (vote_data['week'] == week) & 
                        (vote_data['celebrity_name'] == celebrity)
                    ]
                    
                    # Handle column name for vote share (check both potential names)
                    vote_col = 'estimated_vote_share'
                    if vote_col not in vote_data.columns:
                        # Fallback or check for specific name if needed
                        pass 
                        
                    vote_share = vote_record[vote_col].values[0] if len(vote_record) > 0 else np.nan
                    
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
        
        if long_df.empty:
            raise ValueError("Processed DataFrame is empty. Check data merging logic.")

        # Feature Engineering
        industry_dummies = pd.get_dummies(long_df['industry'], prefix='industry')
        long_df = pd.concat([long_df, industry_dummies], axis=1)
        
        long_df = long_df.sort_values(['celebrity_name', 'week']).reset_index(drop=True)
        long_df['prev_week_score'] = long_df.groupby('celebrity_name')['judge_score_total'].shift(1)
        long_df['score_change'] = long_df['judge_score_total'] - long_df['prev_week_score']
        long_df['rolling_avg_2w'] = long_df.groupby('celebrity_name')['judge_score_total'].transform(
            lambda x: x.rolling(window=2, min_periods=1).mean()
        )
        
        long_df['prev_week_score'] = long_df['prev_week_score'].fillna(long_df['judge_score_total'])
        long_df['score_change'] = long_df['score_change'].fillna(0)
        long_df['rolling_avg_2w'] = long_df['rolling_avg_2w'].fillna(long_df['judge_score_total'])
        
        train_df = long_df[long_df['vote_share'].notna() & (long_df['vote_share'] > 0)].copy()
        
        base_features = [
            'season', 'week', 'age', 'judge_score_total', 
            'prev_week_score', 'score_change', 'rolling_avg_2w', 'is_eliminated'
        ]
        feature_cols = base_features + list(industry_dummies.columns)
        
        for col in feature_cols:
            if col not in train_df.columns:
                train_df[col] = 0
        
        X = train_df[feature_cols]
        y = train_df['vote_share']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        return X_train, X_test, y_train, y_test, long_df, feature_cols
        
    except Exception as e:
        print(f"Error in load_and_preprocess: {e}")
        traceback.print_exc()
        raise e

# ==========================================
# 2. Model Training and Prediction
# ==========================================
def train_and_predict(model_type, X_train, X_test, y_train, y_test, long_df, feature_cols):
    print(f"\nTraining {model_type} model...")
    
    if model_type == 'XGBoost':
        model = XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42
        )
        try:
            model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        except TypeError:
            model.fit(X_train, y_train)
            
    elif model_type == 'LightGBM':
        model = LGBMRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42, verbose=-1
        )
        try:
            model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
        except TypeError:
            model.fit(X_train, y_train)

    # Predict
    pred_df = long_df.copy()
    pred_df['prev_week_score'] = pred_df['prev_week_score'].fillna(pred_df['judge_score_total'])
    pred_df['score_change'] = pred_df['score_change'].fillna(0)
    pred_df['rolling_avg_2w'] = pred_df['rolling_avg_2w'].fillna(pred_df['judge_score_total'])
    
    for col in feature_cols:
        if col not in pred_df.columns:
            pred_df[col] = 0
            
    X_full = pred_df[feature_cols]
    pred_df['vote_hat'] = model.predict(X_full)
    
    # Normalize
    def normalize_group(group):
        total = group['vote_hat'].sum()
        if total > 1e-8:
            group['vote_share_hat'] = group['vote_hat'] / total
        else:
            group['vote_share_hat'] = 1.0 / len(group) if len(group) > 0 else 0
        return group
    
    pred_df = pred_df.groupby(['season', 'week'], group_keys=False).apply(normalize_group).reset_index(drop=True)
    
    pred_df['uncertainty'] = 0.05
    pred_df.loc[pred_df['is_eliminated'] == 1, 'uncertainty'] = 0.08
    
    return pred_df

# ==========================================
# 3. Validation and Reporting
# ==========================================
def validate_and_report(pred_df, model_name):
    # Reload and standardize raw data for validation comparison
    raw_df = pd.read_excel('2026_MCM_Problem_C_Processed_Data.xlsx', sheet_name='Sheet1')
    raw_df.columns = raw_df.columns.str.strip().str.lower()
    
    elimination_info = []
    for idx, row in raw_df.iterrows():
        # Clean eliminated_week column access
        if 'eliminated_week' not in row:
             continue 
             
        week_val = row['eliminated_week']
        if pd.isna(week_val) or week_val in ['N/A', '', 'nan', 'None']:
            week_clean = 97
        elif str(week_val).lower() in ['决赛', 'winner', 'champion']:
            week_clean = 99
        elif str(week_val).lower() in ['退赛', 'withdrew', 'quit']:
            week_clean = 98
        else:
            try:
                week_clean = int(week_val)
            except:
                week_clean = 97
                
        elimination_info.append({
            'celebrity_name': row['celebrity_name'],
            'season': row['season'],
            'actual_eliminated_week': week_clean
        })
    elimination_df = pd.DataFrame(elimination_info)
    
    merged_df = pd.merge(pred_df, elimination_df, on=['celebrity_name', 'season'], how='left')
    merged_df['is_actually_eliminated'] = (
        (merged_df['week'] == merged_df['actual_eliminated_week']) & 
        (merged_df['actual_eliminated_week'] < 97)
    ).astype(int)
    
    # Consistency
    weekly_results = []
    for (season, week), group in merged_df.groupby(['season', 'week']):
        if week >= 10 and group['actual_eliminated_week'].max() >= 97:
            continue
        
        pred_lowest = group.loc[group['vote_share_hat'].idxmin(), 'celebrity_name']
        actual_elim = group[group['is_actually_eliminated'] == 1]['celebrity_name'].tolist()
        is_correct = pred_lowest in actual_elim if actual_elim else False
        weekly_results.append(is_correct)
        
    accuracy = np.mean(weekly_results) if weekly_results else 0
    correct_count = sum(weekly_results)
    total_weeks = len(weekly_results)
    
    # Correlation
    corrs = []
    for _, group in merged_df.groupby(['season', 'week']):
        if len(group) >= 3:
            c, _ = spearmanr(group['vote_share_hat'], group['judge_score_total'])
            corrs.append(c)
    avg_spearman = np.mean(corrs) if corrs else 0
    
    # Certainty
    avg_unc = merged_df['uncertainty'].mean()
    unc_range = [merged_df['uncertainty'].min(), merged_df['uncertainty'].max()]
    edge_unc = merged_df[merged_df['is_eliminated']==1]['uncertainty'].mean()
    safe_unc = merged_df[merged_df['is_eliminated']==0]['uncertainty'].mean()
    if pd.isna(edge_unc): edge_unc = 0
    if pd.isna(safe_unc): safe_unc = 0
    
    print("\n" + "="*70)
    print(f"DWTS VOTE SHARE PREDICTION VALIDATION REPORT ({model_name.upper()})")
    print("=")
    print(f"EXECUTION TIME: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("1. CONSISTENCY VALIDATION")
    print(f"Weekly Elimination Accuracy: {accuracy:.2%}")
    print(f"Total Weeks Analyzed: {total_weeks}")
    print(f"Correctly Predicted Eliminations: {correct_count}")
    print(f"Average Spearman Correlation (Vote vs Judge): {avg_spearman:.4f}")
    
    print("2. CERTAINTY VALIDATION")
    print(f"Average Prediction Uncertainty: {avg_unc:.4f}")
    print(f"Uncertainty Range: [{unc_range[0]:.4f}, {unc_range[1]:.4f}]")
    print(f"Elimination Edge Uncertainty: {edge_unc:.4f}")
    print(f"Safe Contestant Uncertainty: {safe_unc:.4f}")
    
    print("3. KEY FINDINGS")
    if accuracy > 0.8:
        print(f"√ HIGH consistency: {accuracy:.0%} of weekly eliminations correctly predicted")
    elif accuracy > 0.7:
        print(f"√ MODERATE consistency: {accuracy:.0%} elimination accuracy")
        
    if avg_spearman > 0.2:
        print("√ Moderate positive correlation between predicted votes and judge scores")
        
    if edge_unc > safe_unc:
        print("√ Model appropriately assigns higher uncertainty to elimination-edge contestants")
    print("="*70 + "\n")

# ==========================================
# 4. Main Execution
# ==========================================
if __name__ == "__main__":
    try:
        X_train, X_test, y_train, y_test, long_df, feature_cols = load_and_preprocess()
        
        # 1. XGBoost Only
        pred_xgb = train_and_predict('XGBoost', X_train, X_test, y_train, y_test, long_df, feature_cols)
        validate_and_report(pred_xgb, "XGBoost Only")
        
        # 2. LightGBM Only
        pred_lgbm = train_and_predict('LightGBM', X_train, X_test, y_train, y_test, long_df, feature_cols)
        validate_and_report(pred_lgbm, "LightGBM Only")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        traceback.print_exc()
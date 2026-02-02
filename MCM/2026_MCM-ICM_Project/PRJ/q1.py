import pandas as pd
import numpy as np
import re
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import lightgbm as lgb
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
# 在现有的 sklearn 导入附近添加
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

# Step 1: Load and prepare the data
def load_and_clean_data(file_path):
    """
    Load and clean the DWTS data from CSV file.
    Handles missing values, transforms data format, and prepares for analysis.
    """
    # Load the data
    df = pd.read_csv(file_path)
    
    # Data cleaning
    # Replace 0.0 with NaN for scores (0.0 represents eliminated or not participating)
    score_columns = [col for col in df.columns if re.match(r'week\d+_judge\d+_score', col)]
    for col in score_columns:
        df[col] = df[col].replace(0.0, np.nan)
    
    # Handle N/A values - keep as NaN for calculation
    df = df.replace('N/A', np.nan)
    
    # Convert numeric columns to float
    for col in score_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Add "eliminated" status based on 0 scores
    df['eliminated'] = df[score_columns].isna().all(axis=1)
    
    # Add "still_in_competition" marker
    df['still_in_competition'] = ~df['eliminated']
    
    return df

# Step 2: Feature engineering
def engineer_features(df):
    """
    Create new features including weekly averages and score shares.
    """
    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Extract week and judge info from column names
    week_columns = [col for col in df.columns if re.match(r'week\d+_judge\d+_score', col)]
    
    # Process each week
    weeks = sorted(set([int(re.search(r'week(\d+)', col).group(1)) for col in week_columns]))
    
    # Calculate weekly total scores and average scores
    for week in weeks:
        week_cols = [col for col in week_columns if f'week{week}' in col]
        
        # Calculate total score for the week (sum of available judges)
        df[f'week{week}_judge_score_total'] = df[week_cols].sum(axis=1)
        
        # Calculate number of judges for the week
        df[f'week{week}_judge_count'] = df[week_cols].notna().sum(axis=1)
        
        # Calculate average score for the week
        df[f'week{week}_avg_score'] = df[f'week{week}_judge_score_total'] / df[f'week{week}_judge_count']
        
        # Calculate score share (for the week)
        # First, we'll calculate this after reshaping to long format
    
    return df

# Step 3: Reshape data to long format
def reshape_to_long(df):
    """
    Reshape the data from wide format to long format.
    Each row represents a contestant's performance in a specific week.
    """
    # Identify identifier columns
    id_vars = ['celebrity_name', 'ballroom_partner', 'celebrity_industry', 'celebrity_homestate', 
               'celebrity_homecountry/region', 'celebrity_age_during_season', 'season', 'results', 
               'placement', 'eliminated', 'still_in_competition']
    
    # Identify value columns (judge scores)
    value_vars = [col for col in df.columns if re.match(r'week\d+_judge\d+_score', col) or 
                 re.match(r'week\d+_judge_score_total|week\d+_judge_count|week\d+_avg_score', col)]
    
    # Melt the DataFrame
    long_df = pd.melt(df, 
                      id_vars=id_vars,
                      value_vars=value_vars,
                      var_name='variable',
                      value_name='value')
    
# Extract week
    long_df['week'] = long_df['variable'].str.extract(r'week(\d+)')
    
    # Clean extraction: remove 'weekX_' prefix to get the metric name
    # e.g., 'week1_judge_score_total' becomes 'judge_score_total'
    long_df['metric'] = long_df['variable'].str.replace(r'week\d+_', '', regex=True)
    
    # Drop the original variable column
    long_df = long_df.drop('variable', axis=1)
    
    # Pivot to get separate columns for different metrics
    long_df = long_df.pivot_table(
        index=id_vars + ['week'],
        columns='metric',
        values='value',
        aggfunc='first'
    ).reset_index()
    
    # Flatten the multi-index columns
    # long_df.columns = ['_'.join(col).strip() for col in long_df.columns.values]
    # long_df.columns = [col.replace('_value', '') for col in long_df.columns]
    
    # Add a column for the week number as integer
    long_df['week'] = pd.to_numeric(long_df['week'])
    
    # Sort by season and week
    long_df = long_df.sort_values(['season', 'week']).reset_index(drop=True)
    
    # Calculate judge score share for each week (for the whole season)
    # First, calculate total judge score for each week across all contestants
    week_totals = long_df.groupby(['season', 'week'])['judge_score_total'].sum().reset_index()
    week_totals = week_totals.rename(columns={'judge_score_total': 'week_total_judge_score'})
    
    # Merge back to the main dataframe
    long_df = pd.merge(long_df, week_totals, on=['season', 'week'], how='left')
    
    # Calculate judge score share
    long_df['judge_score_share'] = long_df['judge_score_total'] / long_df['week_total_judge_score']
    
    # Clean up columns
    long_df = long_df.drop(columns=['week_total_judge_score'])
    
    return long_df

# Step 4: Prepare data for modeling
def prepare_modeling_data(long_df):
    """
    Prepare the data for modeling by creating features and target variables.
    """
    # Create features from past performance
    features_df = long_df.copy()
    
    # Sort by season and week
    features_df = features_df.sort_values(['season', 'week'])
    
    # Create lag features for previous weeks' performance
    for lag in range(1, 4):  # Use up to 3 weeks of history
        features_df[f'avg_score_lag{lag}'] = features_df.groupby('celebrity_name')['avg_score'].shift(lag)
        features_df[f'judge_score_share_lag{lag}'] = features_df.groupby('celebrity_name')['judge_score_share'].shift(lag)
    
    # Create rolling window features
    features_df['avg_score_rolling_mean'] = features_df.groupby('celebrity_name')['avg_score'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean())
    
    features_df['judge_score_share_rolling_mean'] = features_df.groupby('celebrity_name')['judge_score_share'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean())
    
    # Create trend features (slope of the last 3 weeks)
    features_df['avg_score_trend'] = features_df.groupby('celebrity_name')['avg_score'].transform(
        lambda x: np.polyfit(range(len(x)), x.fillna(0), 1)[0] if len(x) > 1 else 0)
    
    features_df['judge_score_share_trend'] = features_df.groupby('celebrity_name')['judge_score_share'].transform(
        lambda x: np.polyfit(range(len(x)), x.fillna(0), 1)[0] if len(x) > 1 else 0)
    
    # Create features for the current week
    features_df['current_week_avg_score'] = features_df['avg_score']
    features_df['current_week_judge_score_share'] = features_df['judge_score_share']
    
    # Create features for the season
    features_df['season_avg_score'] = features_df.groupby('season')['avg_score'].transform('mean')
    features_df['season_judge_score_share'] = features_df.groupby('season')['judge_score_share'].transform('mean')
    
    # Create features for the celebrity (static)
    features_df['celebrity_age'] = features_df['celebrity_age_during_season']
    features_df['celebrity_industry'] = features_df['celebrity_industry']
    features_df['celebrity_homecountry'] = features_df['celebrity_homecountry/region']
    
    # One-hot encode categorical variables
    features_df = pd.get_dummies(features_df, columns=['celebrity_industry', 'celebrity_homecountry'], prefix=['industry', 'country'])
    
    # Create target variable: we'll use judge_score_share as a proxy for popularity
    # In reality, we don't have the true vote share, but we can use it as a target for our models
    features_df['vote_share_hat'] = features_df['judge_score_share']
    
    # Create a binary target for whether the contestant was eliminated
    features_df['eliminated_next_week'] = features_df.groupby('celebrity_name')['eliminated'].shift(-1).fillna(False)
    
    return features_df

# Step 5: Build models to estimate vote shares
def build_models(data):
    """
    Build two models to estimate vote shares:
    1. A linear regression model (interpretable)
    2. A gradient boosting model (more predictive)
    """
    # Filter out rows where we don't have enough historical data
    data = data.dropna(subset=['avg_score_lag1'])
    
    # Define features and target
    features = [
        'current_week_avg_score', 'current_week_judge_score_share',
        'avg_score_lag1', 'avg_score_lag2', 'avg_score_lag3',
        'judge_score_share_lag1', 'judge_score_share_lag2', 'judge_score_share_lag3',
        'avg_score_rolling_mean', 'judge_score_share_rolling_mean',
        'avg_score_trend', 'judge_score_share_trend',
        'season_avg_score', 'season_judge_score_share',
        'celebrity_age'
    ]
    
    # Add all one-hot encoded features
    for col in data.columns:
        if col.startswith('industry_') or col.startswith('country_'):
            features.append(col)
    
    # Filter out rows where the target is NaN
    data = data.dropna(subset=['vote_share_hat'])
    
    # Split data into training and testing sets (by season)
    train_seasons = [s for s in data['season'].unique() if s <= 30]  # Use seasons 1-30 for training
    test_seasons = [s for s in data['season'].unique() if s > 30]    # Use seasons 31-34 for testing
    
    train_data = data[data['season'].isin(train_seasons)]
    test_data = data[data['season'].isin(test_seasons)]
    
    # # Scale features
    # scaler = StandardScaler()
    # train_features = scaler.fit_transform(train_data[features])
    # test_features = scaler.transform(test_data[features])
    # Impute missing values and scale features
    imputer = SimpleImputer(strategy='mean')
    scaler = StandardScaler()
    
    # 先填充缺失值，再进行标准化
    train_features = imputer.fit_transform(train_data[features])
    train_features = scaler.fit_transform(train_features)
    
    test_features = imputer.transform(test_data[features])
    test_features = scaler.transform(test_features)
    # 1. Linear regression model (interpretable)
    lr_model = LinearRegression()
    lr_model.fit(train_features, train_data['vote_share_hat'])
    
    # Predict on test data
    lr_pred = lr_model.predict(test_features)
    
    # Calculate uncertainty (using standard error)
    residuals = train_data['vote_share_hat'] - lr_model.predict(train_features)
    std_error = np.std(residuals)
    
    # 2. Gradient boosting model (more predictive)
    gb_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    gb_model.fit(train_features, train_data['vote_share_hat'])
    
    # Predict on test data
    gb_pred = gb_model.predict(test_features)
    
    # Calculate uncertainty (using out-of-bag error)
    gb_pred_train = gb_model.predict(train_features)
    gb_residuals = train_data['vote_share_hat'] - gb_pred_train
    gb_std_error = np.std(gb_residuals)
    
    # Combine predictions (weighted average)
    # In a real scenario, we would use cross-validation to determine optimal weights
    combined_pred = 0.3 * lr_pred + 0.7 * gb_pred
    combined_std_error = 0.3 * std_error + 0.7 * gb_std_error
    
    # Add predictions to test data
    test_data['vote_share_hat'] = combined_pred
    test_data['uncertainty'] = combined_std_error
    
    # Calculate vote_hat (assuming a total vote pool of 10 million for simplicity)
    # In reality, this would vary by week and season
    test_data['vote_hat'] = test_data['vote_share_hat'] * 10_000_000
    
    # Return results
    # return test_data[['season', 'week', 'celebrity_name', 'vote_hat', 'vote_share_hat', 'uncertainty']]
    # Calculate model performance metrics
    performance_df = pd.DataFrame({
        'model_type': ['linear_regression', 'gradient_boosting', 'combined'],
        'rmse': [
            np.sqrt(mean_squared_error(test_data['vote_share_hat'], lr_pred)),
            np.sqrt(mean_squared_error(test_data['vote_share_hat'], gb_pred)),
            np.sqrt(mean_squared_error(test_data['vote_share_hat'], combined_pred))
        ]
    })

    # Return results AND performance metrics
    return test_data[['season', 'week', 'celebrity_name', 'vote_hat', 'vote_share_hat', 'uncertainty']], performance_df

# Step 6: Main function to run the entire process
def main():
    """
    Main function to run the entire data processing and modeling pipeline.
    """
    # Get current timestamp for sources file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load and clean data
    print("Loading and cleaning data...")
    df = load_and_clean_data('2026_MCM_Problem_C_Data.csv')
    
    # Engineer features
    print("Engineering features...")
    df = engineer_features(df)
    
    # Reshape to long format
    print("Reshaping to long format...")
    long_df = reshape_to_long(df)
    
    # Prepare data for modeling
    print("Preparing data for modeling...")
    modeling_data = prepare_modeling_data(long_df)
    
    # Build models and estimate vote shares
    # Build models and estimate vote shares
    print("Building models and estimating vote shares...")
    # 修改这里：接收两个返回值
    results, performance_df = build_models(modeling_data)
    
    # Save results to CSV
    results.to_csv('vote_estimates.csv', index=False)
    print("Results saved to vote_estimates.csv")
    
    # Save sources information
    sources_content = f"# Data Sources and Processing Timestamp\n\n"
    sources_content += f"Processed on: {timestamp}\n\n"
    sources_content += "Source data: 2026_MCM_Problem_C_Data.csv\n"
    sources_content += "Source description: DWTS competition data from seasons 1-34\n"
    sources_content += "Source URL: Not applicable (provided in problem statement)\n\n"
    sources_content += "Additional data sources:\n"
    sources_content += "- COMAP MCM Problem C 2026: https://www.comap.org/\n"
    
    with open('sources.md', 'w') as f:
        f.write(sources_content)
    
    print("Source information saved to sources.md")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total records: {len(results)}")
    print(f"Estimated vote range: {results['vote_hat'].min():,.0f} to {results['vote_hat'].max():,.0f}")
    print(f"Average uncertainty: {results['uncertainty'].mean():.4f}")
    
    # Save model performance metrics (for reference)
    performance_df.to_csv('model_performance.csv', index=False)
    print("Model performance metrics saved to model_performance.csv")
if __name__ == "__main__":
    main()
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from pathlib import Path

# Path("output/figures").mkdir(parents=True, exist_ok=True)
# Path("output/results").mkdir(parents=True, exist_ok=True)

# # Read prediction data (keep all contestants including finalists)
# df = pd.read_csv("predicted_vote_shares.csv")
# df = df[df['week'] >= 1].copy()
# df = df.dropna(subset=['judge_score_total', 'vote_share_hat', 'season', 'week', 'celebrity_name']).copy()

# df['judge_score_total'] = pd.to_numeric(df['judge_score_total'], errors='coerce')
# df['vote_share_hat'] = pd.to_numeric(df['vote_share_hat'], errors='coerce')
# df['season'] = pd.to_numeric(df['season'], errors='coerce')
# df['week'] = pd.to_numeric(df['week'], errors='coerce')
# df = df.dropna(subset=['judge_score_total', 'vote_share_hat', 'season', 'week']).copy()

# # Define controversy cases with EXACT names from dataset
# controversies = [
#     {'name': 'Jerry Rice', 'season': 2, 'description': 'Runner-up despite lowest judge scores 12 times'},
#     {'name': 'Bobby Bones', 'season': 27, 'description': 'Winner despite consistently low judge scores'},
#     {'name': 'Bristol Palin', 'season': 11, 'description': '3rd place despite lowest judge scores 12 times'},
#     {'name': 'Billy Ray Cyrus', 'season': 4, 'description': '5th place despite lowest judge scores 6 times'}
# ]

# def calculate_rank_method(df_week):
#     df_week = df_week.copy()
#     df_week['judge_rank'] = df_week['judge_score_total'].rank(ascending=False, method='min')
#     df_week['fan_rank'] = df_week['vote_share_hat'].rank(ascending=False, method='min')
#     df_week['combined_rank'] = df_week['judge_rank'] + df_week['fan_rank']
#     return df_week

# def calculate_percent_method(df_week):
#     df_week = df_week.copy()
#     total_judge = df_week['judge_score_total'].sum()
#     total_fan = df_week['vote_share_hat'].sum()
    
#     if total_judge == 0 or total_fan == 0:
#         df_week['judge_pct'] = 0
#         df_week['fan_pct'] = 0
#         df_week['combined_pct'] = 0
#     else:
#         df_week['judge_pct'] = df_week['judge_score_total'] / total_judge * 100
#         df_week['fan_pct'] = df_week['vote_share_hat'] / total_fan * 100
#         df_week['combined_pct'] = df_week['judge_pct'] + df_week['fan_pct']
#     return df_week

# def simulate_contestant_path(name, season):
#     """Simulate contestant path with exact name matching"""
#     contestant_data = df[(df['celebrity_name'] == name) & (df['season'] == season)].sort_values('week')
#     if contestant_data.empty:
#         # Try case-insensitive match as fallback
#         contestant_data = df[(df['celebrity_name'].str.lower() == name.lower()) & (df['season'] == season)].sort_values('week')
#         if contestant_data.empty:
#             print(f"  Warning: No data found for '{name}' (S{season})")
#             return {'path': pd.DataFrame(), 'elim_rank': None, 'elim_pct': None, 'final_placement': 'Unknown'}
    
#     weeks = sorted(contestant_data['week'].unique())
#     path = []
#     eliminated_week_rank = None
#     eliminated_week_pct = None
    
#     for week in weeks:
#         week_data = df[(df['season'] == season) & (df['week'] == week)]
#         if len(week_data) < 3:
#             continue
            
#         week_rank = calculate_rank_method(week_data)
#         week_pct = calculate_percent_method(week_data)
        
#         # Check if contestant in this week
#         if name not in week_rank['celebrity_name'].values:
#             # Case-insensitive fallback
#             matches = week_rank[week_rank['celebrity_name'].str.lower().str.contains(name.lower().split()[0].lower())]
#             if matches.empty:
#                 continue
#             contestant_row_rank = matches.iloc[0]
#             contestant_row_pct = week_pct[week_pct['celebrity_name'] == contestant_row_rank['celebrity_name']].iloc[0]
#         else:
#             contestant_row_rank = week_rank[week_rank['celebrity_name'] == name].iloc[0]
#             contestant_row_pct = week_pct[week_pct['celebrity_name'] == name].iloc[0]
        
#         # Check elimination status
#         worst_rank = week_rank['combined_rank'].max()
#         worst_pct = week_pct['combined_pct'].min()
        
#         if eliminated_week_rank is None and contestant_row_rank['combined_rank'] == worst_rank:
#             eliminated_week_rank = week
#         if eliminated_week_pct is None and contestant_row_pct['combined_pct'] == worst_pct:
#             eliminated_week_pct = week
        
#         path.append({
#             'week': float(week),
#             'judge_score': float(contestant_row_rank['judge_score_total']),
#             'fan_share': float(contestant_row_rank['vote_share_hat']) * 100,
#             'judge_rank': float(contestant_row_rank['judge_rank']),
#             'fan_rank': float(contestant_row_rank['fan_rank']),
#             'combined_rank': float(contestant_row_rank['combined_rank']),
#             'combined_pct': float(contestant_row_pct['combined_pct'])
#         })
    
#     path_df = pd.DataFrame(path)
#     if path_df.empty:
#         path_df = pd.DataFrame(columns=['week', 'judge_score', 'fan_share', 'judge_rank', 'fan_rank', 'combined_rank', 'combined_pct'])
#     else:
#         path_df['week'] = pd.to_numeric(path_df['week'], errors='coerce')
    
#     final_placement = 'Unknown'
#     if 'placement' in contestant_data.columns and not contestant_data['placement'].isna().all():
#         final_placement = contestant_data['placement'].iloc[0]
    
#     return {
#         'path': path_df,
#         'elim_rank': eliminated_week_rank,
#         'elim_pct': eliminated_week_pct,
#         'final_placement': final_placement
#     }

# # Analyze controversy cases
# controversy_results = []

# for case in controversies:
#     print(f"\nAnalyzing: {case['name']} (S{case['season']})")
#     result = simulate_contestant_path(case['name'], case['season'])
    
#     if result['path'].empty:
#         print(f"  Skipped: No path data available")
#         continue
        
#     print(f"  Weeks competed: {len(result['path'])}")
#     print(f"  Final placement: {result['final_placement']}")
    
#     controversy_results.append({
#         'celebrity': case['name'],
#         'season': case['season'],
#         'description': case['description'],
#         'actual_placement': result['final_placement'],
#         'elim_rank_week': result['elim_rank'] if result['elim_rank'] else 'Finalist',
#         'elim_pct_week': result['elim_pct'] if result['elim_pct'] else 'Finalist'
#     })
    
#     # Generate individual contestant charts (only for Bobby Bones as required)
#     if case['name'] == 'Bobby Bones':
#         fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor='white')
        
#         # Judge scores
#         axes[0,0].plot(result['path']['week'], result['path']['judge_score'], 
#                        marker='o', linewidth=2.5, markersize=8, color='#87CEEB')
#         axes[0,0].set_title('Bobby Bones: Judge Scores Trend (S27)', fontsize=14, fontweight='bold')
#         axes[0,0].set_ylabel('Judge Total Score')
#         axes[0,0].grid(True, alpha=0.3, color='#D3D3D3')
        
#         # Fan vote share
#         axes[0,1].plot(result['path']['week'], result['path']['fan_share'], 
#                        marker='s', linewidth=2.5, markersize=8, color='#98FB98')
#         axes[0,1].set_title('Fan Vote Share Trend', fontsize=14, fontweight='bold')
#         axes[0,1].set_ylabel('Fan Share (%)')
#         axes[0,1].grid(True, alpha=0.3, color='#D3D3D3')
        
#         # Rank method combined rank
#         axes[1,0].plot(result['path']['week'], result['path']['combined_rank'], 
#                        marker='^', linewidth=2.5, markersize=8, color='#DDA0DD')
#         axes[1,0].set_title('Rank Method: Combined Rank', fontsize=14, fontweight='bold')
#         axes[1,0].set_ylabel('Combined Rank (Lower = Better)')
#         axes[1,0].set_xlabel('Week')
#         axes[1,0].invert_yaxis()
#         axes[1,0].grid(True, alpha=0.3, color='#D3D3D3')
        
#         # Percent method combined score
#         axes[1,1].plot(result['path']['week'], result['path']['combined_pct'], 
#                        marker='v', linewidth=2.5, markersize=8, color='#FFB6C1')
#         axes[1,1].set_title('Percent Method: Combined Score', fontsize=14, fontweight='bold')
#         axes[1,1].set_ylabel('Combined Score (%)')
#         axes[1,1].set_xlabel('Week')
#         axes[1,1].grid(True, alpha=0.3, color='#D3D3D3')
        
#         plt.suptitle('Controversy Case Analysis: Bobby Bones', 
#                      fontsize=16, fontweight='bold', y=0.99)
#         plt.tight_layout(rect=[0, 0.03, 1, 0.95])
#         plt.savefig("output/figures/bobby_bones_case.png", dpi=300, bbox_inches='tight', facecolor='white')
#         plt.close()

# # Save controversy analysis results
# if controversy_results:
#     controversy_df = pd.DataFrame(controversy_results)
#     controversy_df.to_csv("output/results/controversy_analysis.csv", index=False)
    
#     # Generate comparison chart for all controversy cases
#     plt.figure(figsize=(12, 8), facecolor='white')
#     x = np.arange(len(controversy_results))
#     width = 0.35

#     elim_rank_vals = [c['elim_rank_week'] if isinstance(c['elim_rank_week'], (int, float)) else 15 for c in controversy_results]
#     elim_pct_vals = [c['elim_pct_week'] if isinstance(c['elim_pct_week'], (int, float)) else 15 for c in controversy_results]

#     bars1 = plt.bar(x - width/2, elim_rank_vals, width, label='Rank Method Elimination Week', 
#                     color='#87CEEB', alpha=0.9, edgecolor='white')
#     bars2 = plt.bar(x + width/2, elim_pct_vals, width, label='Percent Method Elimination Week', 
#                     color='#98FB98', alpha=0.9, edgecolor='white')
#     plt.axhline(y=12, color='#4682B4', linestyle='--', linewidth=2, label='Actual Finalist Threshold')

#     plt.ylabel('Elimination Week (Higher = Longer Survival)', fontsize=13)
#     plt.title('Controversy Cases: Elimination Prediction by Voting Method', fontsize=16, fontweight='bold', pad=20)
#     plt.xticks(x, [f"{c['celebrity']}\nS{c['season']}" for c in controversy_results], fontsize=11)
#     plt.legend(fontsize=11, frameon=False)
#     plt.grid(axis='y', alpha=0.3, color='#D3D3D3')
#     plt.ylim(0, 16)

#     # Add value labels
#     for bar in bars1:
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width()/2., height,
#                  f'{int(height)}' if height < 15 else 'Finalist',
#                  ha='center', va='bottom', fontsize=10, fontweight='bold')
#     for bar in bars2:
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width()/2., height,
#                  f'{int(height)}' if height < 15 else 'Finalist',
#                  ha='center', va='bottom', fontsize=10, fontweight='bold')

#     plt.tight_layout()
#     plt.savefig("output/figures/controversy_cases.png", dpi=300, bbox_inches='tight', facecolor='white')
#     plt.close()

# print("\nControversy Analysis Complete!")
# print(f"  Successfully analyzed {len(controversy_results)} controversy cases")
# if controversy_results:
#     print(f"  Results saved to: output/results/controversy_analysis.csv")
#     print(f"  Charts saved to: output/figures/controversy_cases.png and bobby_bones_case.png")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

Path("output/figures").mkdir(parents=True, exist_ok=True)
Path("output/results").mkdir(parents=True, exist_ok=True)

df = pd.read_csv("predicted_vote_shares.csv")
df = df[df['week'] >= 1].copy()
df = df.dropna(subset=['judge_score_total', 'vote_share_hat', 'season', 'week', 'celebrity_name']).copy()
df['judge_score_total'] = pd.to_numeric(df['judge_score_total'], errors='coerce')
df['vote_share_hat'] = pd.to_numeric(df['vote_share_hat'], errors='coerce')
df['season'] = pd.to_numeric(df['season'], errors='coerce')
df['week'] = pd.to_numeric(df['week'], errors='coerce')
df = df.dropna(subset=['judge_score_total', 'vote_share_hat', 'season', 'week']).copy()

def calculate_rank_method(df_week):
    df_week = df_week.copy()
    df_week['judge_rank'] = df_week['judge_score_total'].rank(ascending=False, method='min')
    df_week['fan_rank'] = df_week['vote_share_hat'].rank(ascending=False, method='min')
    df_week['combined_rank'] = df_week['judge_rank'] + df_week['fan_rank']
    return df_week

def calculate_percent_method(df_week):
    df_week = df_week.copy()
    total_judge = df_week['judge_score_total'].sum()
    total_fan = df_week['vote_share_hat'].sum()
    if total_judge == 0 or total_fan == 0:
        df_week['judge_pct'] = 0
        df_week['fan_pct'] = 0
        df_week['combined_pct'] = 0
    else:
        df_week['judge_pct'] = df_week['judge_score_total'] / total_judge * 100
        df_week['fan_pct'] = df_week['vote_share_hat'] / total_fan * 100
        df_week['combined_pct'] = df_week['judge_pct'] + df_week['fan_pct']
    return df_week

def find_celebrity(name, season, df):
    """Robust name matching: exact -> first name -> last name"""
    target = name.strip().lower()
    # Exact match (normalized)
    mask = (df['season'] == season) & (df['celebrity_name'].str.strip().str.lower() == target)
    match = df[mask]
    if not match.empty:
        return match.sort_values('week')
    # First name match
    first = target.split()[0]
    mask = (df['season'] == season) & (df['celebrity_name'].str.contains(first, case=False, na=False))
    match = df[mask]
    if not match.empty:
        print(f"  ⚠ Using first-name match for '{name}': {match['celebrity_name'].iloc[0]}")
        return match.sort_values('week')
    # Last name match
    last = target.split()[-1]
    mask = (df['season'] == season) & (df['celebrity_name'].str.contains(last, case=False, na=False))
    match = df[mask]
    if not match.empty:
        print(f"  ⚠ Using last-name match for '{name}': {match['celebrity_name'].iloc[0]}")
        return match.sort_values('week')
    return pd.DataFrame()

def simulate_contestant(name, season, df):
    contestant_data = find_celebrity(name, season, df)
    if contestant_data.empty:
        print(f"  ✗ No data found for '{name}' (S{season})")
        season_names = df[df['season'] == season]['celebrity_name'].unique()[:5]
        print(f"    Sample names in S{season}: {season_names}")
        return None
    weeks = sorted(contestant_data['week'].unique())
    path = []
    elim_rank = None
    elim_pct = None
    for week in weeks:
        week_data = df[(df['season'] == season) & (df['week'] == week)]
        if len(week_data) < 3:
            continue
        week_rank = calculate_rank_method(week_data)
        week_pct = calculate_percent_method(week_data)
        if name not in week_rank['celebrity_name'].values:
            # Try normalized match
            normalized_names = week_rank['celebrity_name'].str.strip().str.lower()
            if target not in normalized_names.values:
                continue
            idx = normalized_names[normalized_names == target].index[0]
            contestant_rank = week_rank.loc[idx]
            contestant_pct = week_pct.loc[idx]
        else:
            contestant_rank = week_rank[week_rank['celebrity_name'] == name].iloc[0]
            contestant_pct = week_pct[week_pct['celebrity_name'] == name].iloc[0]
        worst_rank = week_rank['combined_rank'].max()
        worst_pct = week_pct['combined_pct'].min()
        if elim_rank is None and contestant_rank['combined_rank'] == worst_rank:
            elim_rank = week
        if elim_pct is None and contestant_pct['combined_pct'] == worst_pct:
            elim_pct = week
        path.append({
            'week': float(week),
            'judge_score': float(contestant_rank['judge_score_total']),
            'fan_share': float(contestant_rank['vote_share_hat']) * 100,
            'judge_rank': float(contestant_rank['judge_rank']),
            'fan_rank': float(contestant_rank['fan_rank']),
            'combined_rank': float(contestant_rank['combined_rank']),
            'combined_pct': float(contestant_pct['combined_pct'])
        })
    if not path:
        return None
    path_df = pd.DataFrame(path)
    final_place = contestant_data['placement'].iloc[0] if 'placement' in contestant_data.columns else 'Unknown'
    return {
        'path': path_df,
        'elim_rank': elim_rank,
        'elim_pct': elim_pct,
        'final_place': final_place
    }

controversies = [
    {'name': 'Jerry Rice', 'season': 2, 'description': 'Runner-up despite lowest judge scores 12 times'},
    {'name': 'Bobby Bones', 'season': 27, 'description': 'Winner despite consistently low judge scores'},
    {'name': 'Bristol Palin', 'season': 11, 'description': '3rd place despite lowest judge scores 12 times'},
    {'name': 'Billy Ray Cyrus', 'season': 4, 'description': '5th place despite last place judge scores 6 times'}
]

results = []
for case in controversies:
    print(f"\nAnalyzing: {case['name']} (Season {case['season']})")
    sim = simulate_contestant(case['name'], case['season'], df)
    if sim is None:
        print(f"  ✗ Skipped: No valid data path")
        continue
    print(f"  Weeks competed: {len(sim['path'])} | Final place: {sim['final_place']}")
    results.append({
        'celebrity': case['name'],
        'season': case['season'],
        'description': case['description'],
        'final_place': sim['final_place'],
        'elim_rank_week': sim['elim_rank'] if sim['elim_rank'] else 'Finalist',
        'elim_pct_week': sim['elim_pct'] if sim['elim_pct'] else 'Finalist'
    })
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor('white')
    axes[0,0].plot(sim['path']['week'], sim['path']['judge_score'], marker='o', linewidth=2.5, markersize=8, color='#4682B4')
    axes[0,0].set_title(f'{case["name"]} Judge Scores (S{case["season"]})', fontsize=12, fontweight='bold')
    axes[0,0].set_ylabel('Total Judge Score', fontsize=11)
    axes[0,0].grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    axes[0,1].plot(sim['path']['week'], sim['path']['fan_share'], marker='s', linewidth=2.5, markersize=8, color='#90EE90')
    axes[0,1].set_title('Fan Vote Share Trend', fontsize=12, fontweight='bold')
    axes[0,1].set_ylabel('Fan Share (%)', fontsize=11)
    axes[0,1].grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    axes[1,0].plot(sim['path']['week'], sim['path']['combined_rank'], marker='^', linewidth=2.5, markersize=8, color='#87CEEB')
    axes[1,0].set_title('Rank Method Combined Rank', fontsize=12, fontweight='bold')
    axes[1,0].set_ylabel('Combined Rank (Lower = Better)', fontsize=11)
    axes[1,0].set_xlabel('Week', fontsize=11)
    axes[1,0].invert_yaxis()
    axes[1,0].grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    axes[1,1].plot(sim['path']['week'], sim['path']['combined_pct'], marker='v', linewidth=2.5, markersize=8, color='#F08080')
    axes[1,1].set_title('Percent Method Combined Score', fontsize=12, fontweight='bold')
    axes[1,1].set_ylabel('Combined Score (%)', fontsize=11)
    axes[1,1].set_xlabel('Week', fontsize=11)
    axes[1,1].grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    plt.suptitle(f'Controversy Case Analysis: {case["name"]}', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    safe_name = case['name'].lower().replace(' ', '_').replace('.', '').replace("'", '')
    plt.savefig(f"output/figures/{safe_name}_analysis.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

if results:
    results_df = pd.DataFrame(results)
    results_df.to_csv("output/results/controversy_detailed_analysis.csv", index=False)
    plt.figure(figsize=(13, 8))
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['figure.facecolor'] = 'white'
    x = np.arange(len(results))
    width = 0.35
    elim_rank_vals = [r['elim_rank_week'] if isinstance(r['elim_rank_week'], (int, float)) else 15 for r in results]
    elim_pct_vals = [r['elim_pct_week'] if isinstance(r['elim_pct_week'], (int, float)) else 15 for r in results]
    bars1 = plt.bar(x - width/2, elim_rank_vals, width, label='Rank Method Elimination Week', color='#87CEEB', alpha=0.9, edgecolor='black', linewidth=0.8)
    bars2 = plt.bar(x + width/2, elim_pct_vals, width, label='Percent Method Elimination Week', color='#90EE90', alpha=0.9, edgecolor='black', linewidth=0.8)
    plt.axhline(y=12, color='#4682B4', linestyle='--', linewidth=2, label='Actual Final Week (Reference)')
    plt.ylabel('Elimination Week (Higher = Longer Survival)', fontsize=12)
    plt.title('Controversy Cases: Elimination Week Prediction by Voting Method', fontsize=14, fontweight='bold', pad=15)
    plt.xticks(x, [f"{r['celebrity']}\nS{r['season']}" for r in results], fontsize=11)
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    plt.ylim(0, 16)
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}' if height < 15 else 'Final', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}' if height < 15 else 'Final', ha='center', va='bottom', fontsize=10, fontweight='bold')
    plt.tight_layout()
    plt.savefig("output/figures/controversy_cases.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
else:
    # Create empty file to prevent downstream errors
    pd.DataFrame(columns=['celebrity','season','description','final_place','elim_rank_week','elim_pct_week']).to_csv("output/results/controversy_detailed_analysis.csv", index=False)
    print("\n⚠ Warning: No controversy cases analyzed successfully. Empty file created for downstream compatibility.")

bobby = find_celebrity('Bobby Bones', 27, df)
if not bobby.empty:
    weeks = bobby['week'].values
    judge_scores = bobby['judge_score_total'].values
    fan_shares = bobby['vote_share_hat'].values * 100
    plt.figure(figsize=(12, 7))
    fig, ax1 = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')
    color1 = '#4682B4'
    ax1.set_xlabel('Week', fontsize=12)
    ax1.set_ylabel('Total Judge Score', color=color1, fontsize=12)
    ax1.plot(weeks, judge_scores, marker='o', color=color1, linewidth=2.5, markersize=8, label='Judge Score')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax1.set_ylim(15, 35)
    ax2 = ax1.twinx()
    color2 = '#90EE90'
    ax2.set_ylabel('Fan Vote Share (%)', color=color2, fontsize=12)
    ax2.plot(weeks, fan_shares, marker='s', color=color2, linewidth=2.5, markersize=8, label='Fan Share')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(5, 15)
    plt.title('Bobby Bones (Season 27): Low Judge Scores vs High Fan Support', fontsize=14, fontweight='bold', pad=20)
    fig.tight_layout()
    plt.savefig("output/figures/bobby_bones_analysis.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
else:
    print("⚠ Bobby Bones data not found for special analysis")

print("\nControversy Analysis Complete!")
print(f"  Successfully analyzed {len(results)} controversy cases")
print(f"  Results saved to: output/results/controversy_detailed_analysis.csv")
print(f"  Charts saved to: output/figures/")
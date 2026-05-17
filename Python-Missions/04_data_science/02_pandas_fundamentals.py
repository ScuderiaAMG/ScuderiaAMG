#!/usr/bin/env python3
"""
Pandas 基础 —— 数据分析利器
涵盖：Series / DataFrame 创建、索引与选择、数据清洗、分组聚合、
      合并与连接、时间序列、透视表、apply / transform / pipe
"""

import numpy as np
import pandas as pd
from io import StringIO


# 显示设置
pd.set_option("display.max_columns", 12)
pd.set_option("display.width", 120)
pd.set_option("display.precision", 2)


# ============================================================
# §1  Series 与 DataFrame 创建
# ============================================================

def demo_creation() -> None:
    print("=" * 60)
    print("§1  Series & DataFrame 创建")
    print("=" * 60)

    # --- Series ---
    s1 = pd.Series([10, 20, 30, 40], index=["a", "b", "c", "d"])
    s2 = pd.Series({"x": 1.5, "y": 2.5, "z": 3.5})
    s3 = pd.Series(np.random.randn(5), name="random")
    print(f"Series from list:\n{s1}\n")
    print(f"Series from dict:\n{s2}\n")
    print(f"Series from numpy:\n{s3}\n")

    # --- DataFrame ---
    # 从字典
    df1 = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Diana"],
        "age": [25, 30, 35, 28],
        "salary": [50000, 60000, 75000, 55000],
        "department": ["Engineering", "Sales", "Engineering", "HR"],
    })
    print(f"DataFrame from dict:\n{df1}\n")

    # 从 NumPy 数组
    df2 = pd.DataFrame(
        np.random.randn(5, 4),
        columns=["A", "B", "C", "D"],
        index=pd.date_range("2024-01-01", periods=5),
    )
    print(f"DataFrame from numpy:\n{df2}\n")

    # 从 CSV 字符串
    csv_data = StringIO("""\
product,price,quantity,category
Laptop,1200,5,Electronics
Mouse,25,100,Electronics
Desk,350,20,Furniture
Chair,150,35,Furniture
Pen,3,500,Stationery
""")
    df3 = pd.read_csv(csv_data)
    print(f"DataFrame from CSV:\n{df3}\n")

    # 属性
    print(f"shape={df1.shape}, columns={list(df1.columns)}, "
          f"dtypes=\n{df1.dtypes}")


# ============================================================
# §2  索引、选择与过滤
# ============================================================

def demo_selection() -> None:
    print("\n" + "=" * 60)
    print("§2  索引、选择与过滤")
    print("=" * 60)

    df = pd.DataFrame({
        "A": range(1, 11),
        "B": np.random.randn(10),
        "C": list("aabbccddee"),
        "D": np.random.uniform(0, 100, 10),
    }, index=pd.Index([f"row_{i}" for i in range(10)], name="idx"))

    print(f"原始:\n{df}\n")

    # 列选择
    print(f"df['A']:\n{df['A']}\n")
    print(f"df[['A', 'C']]:\n{df[['A', 'C']]}\n")

    # loc — 标签索引 (闭区间)
    print(f"df.loc['row_2':'row_5', ['A', 'B']]:\n{df.loc['row_2':'row_5', ['A', 'B']]}\n")

    # iloc — 位置索引 (半开区间)
    print(f"df.iloc[2:5, 0:2]:\n{df.iloc[2:5, 0:2]}\n")
    print(f"df.iloc[[0, 3, 7]]:\n{df.iloc[[0, 3, 7]]}\n")

    # at / iat — 快速标量访问
    print(f"df.at['row_3', 'B'] = {df.at['row_3', 'B']:.4f}")
    print(f"df.iat[4, 3]        = {df.iat[4, 3]:.4f}\n")

    # 布尔索引
    mask = df["D"] > 50
    print(f"df[D > 50]:\n{df[mask]}\n")

    # query — 字符串表达式
    print(f"df.query('A > 5 and C == \"c\"'):\n{df.query('A > 5 and C == \"c\"')}\n")

    # 复合条件
    high_d = df[df["D"] > 50]
    print(f"df[(df['D']>50) & (df['A']%2==0)]:\n{df[(df['D'] > 50) & (df['A'] % 2 == 0)]}\n")

    # isin
    print(f"df[df['C'].isin(['a', 'e'])]:\n{df[df['C'].isin(['a', 'e'])]}\n")

    # between
    print(f"df[df['A'].between(3, 7)]:\n{df[df['A'].between(3, 7)]}\n")

    # where / mask
    print(f"df.where(df['A'] > 4, other=-1):\n{df.where(df['A'] > 4, other=-1)}\n")


# ============================================================
# §3  数据清洗与预处理
# ============================================================

def demo_cleaning() -> None:
    print("\n" + "=" * 60)
    print("§3  数据清洗与预处理")
    print("=" * 60)

    # 构造脏数据
    df = pd.DataFrame({
        "name": ["Alice", "Bob", None, "Diana", "Eve"],
        "age": [25, np.nan, 35, 28, 22],
        "salary": [50000, 60000, None, 55000, 60000],
        "city": ["NYC", "LA", "NYC", None, "LA"],
    })
    print(f"原始脏数据:\n{df}\n")

    # 缺失值检测
    print(f"isnull:\n{df.isnull()}\n")
    print(f"isnull sum:\n{df.isnull().sum()}\n")

    # 缺失值处理
    # 1) 删除含 NaN 的行
    print(f"dropna:\n{df.dropna()}\n")

    # 2) 填充
    df_filled = df.copy()
    df_filled["age"] = df_filled["age"].fillna(df_filled["age"].median())
    df_filled["salary"] = df_filled["salary"].fillna(0)
    df_filled["city"] = df_filled["city"].fillna("Unknown")
    df_filled["name"] = df_filled["name"].fillna(method="ffill")
    print(f"fillna:\n{df_filled}\n")

    # 3) 插值
    df_interp = pd.DataFrame({
        "time": range(10),
        "value": [1, np.nan, np.nan, 4, np.nan, np.nan, 7, np.nan, np.nan, 10],
    })
    df_interp["linear"] = df_interp["value"].interpolate(method="linear")
    df_interp["quadratic"] = df_interp["value"].interpolate(method="quadratic")
    print(f"插值:\n{df_interp}\n")

    # 重复值
    dup_df = pd.DataFrame({
        "a": [1, 1, 2, 3, 3],
        "b": [10, 10, 20, 30, 31],
    })
    print(f"含重复:\n{dup_df}\n")
    print(f"duplicated:\n{dup_df.duplicated()}\n")
    print(f"drop_duplicates:\n{dup_df.drop_duplicates()}\n")
    print(f"drop_duplicates(subset='a'):\n{dup_df.drop_duplicates(subset='a')}\n")

    # 类型转换
    mixed = pd.DataFrame({
        "int_col": ["1", "2", "3", "four"],
        "float_col": ["1.5", "2.7", "N/A", "4.2"],
    })
    print(f"类型转换:\n{mixed}\n")

    # pd.to_numeric (errors='coerce' 将无效值转为 NaN)
    mixed["int_parsed"] = pd.to_numeric(mixed["int_col"], errors="coerce")
    mixed["float_parsed"] = pd.to_numeric(mixed["float_col"], errors="coerce")
    print(f"to_numeric:\n{mixed}\n")

    # 替换
    replacements = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"replace 1->100:\n{replacements.replace(1, 100)}\n")
    print(f"replace {1: 'one', 2: 'two'}:\n{replacements.replace({1: 'one', 2: 'two'})}\n")


# ============================================================
# §4  分组聚合 (groupby)
# ============================================================

def demo_groupby() -> None:
    print("\n" + "=" * 60)
    print("§4  分组聚合 (groupby)")
    print("=" * 60)

    df = pd.DataFrame({
        "department": ["Engineering", "Engineering", "Sales", "Sales",
                       "HR", "Engineering", "Sales", "HR", "HR", "Engineering"],
        "employee": [f"emp_{i}" for i in range(10)],
        "salary": np.random.randint(40_000, 120_000, size=10),
        "bonus": np.random.uniform(0, 20_000, size=10),
        "years": np.random.randint(1, 15, size=10),
    })
    print(f"原始数据:\n{df}\n")

    # 基本聚合
    grouped = df.groupby("department")
    print("基础聚合 (mean):")
    print(grouped[["salary", "bonus", "years"]].mean())

    # agg — 自定义多聚合
    agg_result = grouped.agg(
        avg_salary=("salary", "mean"),
        max_salary=("salary", "max"),
        total_bonus=("bonus", "sum"),
        headcount=("employee", "count"),
        avg_years=("years", lambda x: x.mean()),
    )
    print(f"\n多聚合:\n{agg_result}\n")

    # transform — 保持原形状
    df["dept_mean_salary"] = grouped["salary"].transform("mean")
    df["salary_zscore"] = grouped["salary"].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    print(f"transform (dept_mean, z-score):\n{df[['department', 'salary', 'dept_mean_salary', 'salary_zscore']]}\n")

    # filter — 按组过滤
    large_depts = grouped.filter(lambda x: len(x) >= 3)
    print(f"filter (size >= 3):\n{large_depts}\n")

    # apply — 灵活操作
    def top_n(group: pd.DataFrame, n: int = 2) -> pd.DataFrame:
        return group.nlargest(n, "salary")

    top_salaries = grouped.apply(top_n, n=2)
    print(f"每组 top 2 薪资:\n{top_salaries}\n")

    # 多键分组
    df["level"] = np.where(df["years"] > 5, "Senior", "Junior")
    multi_grouped = df.groupby(["department", "level"])
    print(f"多键分组 mean:\n{multi_grouped[['salary', 'bonus']].mean()}\n")

    # rolling / expanding
    ts = pd.Series(np.random.randn(20), index=pd.date_range("2024-01-01", periods=20))
    print(f"rolling(5) mean 前 10 行:\n{ts.rolling(5).mean().head(10)}")
    print(f"expanding mean 前 8 行:\n{ts.expanding().mean().head(8)}")


# ============================================================
# §5  合并与连接
# ============================================================

def demo_merging() -> None:
    print("\n" + "=" * 60)
    print("§5  合并与连接")
    print("=" * 60)

    # 主表
    employees = pd.DataFrame({
        "emp_id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "dept_id": [10, 20, 10, 30, 20],
    })

    departments = pd.DataFrame({
        "dept_id": [10, 20, 30, 40],
        "dept_name": ["Engineering", "Sales", "HR", "Marketing"],
    })

    salaries = pd.DataFrame({
        "emp_id": [1, 2, 3, 6],
        "salary": [50_000, 60_000, 75_000, 80_000],
    })

    print(f"employees:\n{employees}\n")
    print(f"departments:\n{departments}\n")

    # inner join (默认)
    inner = employees.merge(departments, on="dept_id", how="inner")
    print(f"inner merge:\n{inner}\n")

    # left join
    left = employees.merge(departments, on="dept_id", how="left")
    print(f"left merge:\n{left}\n")

    # outer join
    outer = employees.merge(departments, on="dept_id", how="outer", indicator=True)
    print(f"outer merge:\n{outer}\n")

    # 不同列名
    left_on_right = employees.merge(
        salaries.rename(columns={"emp_id": "id"}),
        left_on="emp_id", right_on="id", how="left"
    )
    print(f"merge on different cols:\n{left_on_right}\n")

    # concat — 纵向/横向拼接
    df_a = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    df_b = pd.DataFrame({"A": [5, 6], "B": [7, 8]})
    df_c = pd.DataFrame({"C": [9, 10], "D": [11, 12]})

    print(f"concat axis=0 (纵向):\n{pd.concat([df_a, df_b], axis=0, ignore_index=True)}\n")
    print(f"concat axis=1 (横向):\n{pd.concat([df_a, df_c], axis=1)}\n")

    # join — 基于索引
    left_idx = pd.DataFrame({"A": [1, 2, 3]}, index=["x", "y", "z"])
    right_idx = pd.DataFrame({"B": [10, 20, 30]}, index=["x", "y", "w"])
    print(f"join (inner):\n{left_idx.join(right_idx, how='inner')}\n")
    print(f"join (left):\n{left_idx.join(right_idx, how='left')}\n")


# ============================================================
# §6  重塑与透视
# ============================================================

def demo_reshaping() -> None:
    print("\n" + "=" * 60)
    print("§6  重塑与透视")
    print("=" * 60)

    # melt — 宽表 → 长表
    wide = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "math": [90, 85, 92],
        "physics": [88, 91, 87],
        "chemistry": [95, 89, 93],
    })
    print(f"宽表:\n{wide}\n")
    long = wide.melt(
        id_vars=["name"],
        var_name="subject",
        value_name="score",
    )
    print(f"长表 (melt):\n{long}\n")

    # pivot — 长表 → 宽表
    wide_again = long.pivot(index="name", columns="subject", values="score")
    print(f"宽表 (pivot):\n{wide_again}\n")

    # pivot_table — 支持聚合的透视
    sales = pd.DataFrame({
        "region": ["North", "North", "South", "South", "North", "South"],
        "product": ["A", "B", "A", "B", "A", "B"],
        "quarter": ["Q1", "Q1", "Q1", "Q1", "Q2", "Q2"],
        "revenue": [100, 150, 200, 120, 110, 130],
    })
    print(f"销售数据:\n{sales}\n")

    pivot = sales.pivot_table(
        values="revenue",
        index="region",
        columns="product",
        aggfunc="mean",
        margins=True,
        margins_name="Total",
    )
    print(f"pivot_table (mean revenue):\n{pivot}\n")

    # stack / unstack
    multi_idx = pd.DataFrame({
        "A": [1, 2, 3, 4],
        "B": [5, 6, 7, 8],
    }, index=pd.MultiIndex.from_tuples([("x", "a"), ("x", "b"), ("y", "a"), ("y", "b")],
                                       names=["outer", "inner"]))
    print(f"多级索引:\n{multi_idx}\n")
    print(f"unstack:\n{multi_idx.unstack(level='outer')}\n")

    # crosstab — 交叉表
    survey = pd.DataFrame({
        "gender": ["M", "F", "M", "F", "M", "F", "M", "M"],
        "preference": ["A", "A", "B", "C", "B", "B", "C", "A"],
    })
    ct = pd.crosstab(survey["gender"], survey["preference"], margins=True)
    print(f"crosstab:\n{ct}\n")


# ============================================================
# §7  时间序列
# ============================================================

def demo_timeseries() -> None:
    print("\n" + "=" * 60)
    print("§7  时间序列")
    print("=" * 60)

    # 创建时间序列
    date_range = pd.date_range("2024-01-01", periods=12, freq="ME")  # 月末频率
    ts = pd.Series(
        np.random.randn(12).cumsum(),
        index=date_range,
        name="cumulative",
    )
    print(f"时间序列:\n{ts}\n")

    # 日期属性
    print(f"ts.index.year:   {ts.index.year.tolist()}")
    print(f"ts.index.month:  {ts.index.month.tolist()}")
    print(f"ts.index.dayofweek: {ts.index.dayofweek.tolist()}")

    # 切片
    print(f"\n2024-03 到 2024-08:\n{ts['2024-03':'2024-08']}\n")

    # 移动 (shift)
    print(f"shift(1) — 滞后:\n{ts.shift(1)}\n")
    print(f"diff(1):\n{ts.diff()}\n")
    print(f"pct_change():\n{ts.pct_change()}\n")

    # 重采样
    daily = pd.date_range("2024-01-01", periods=90, freq="D")
    daily_ts = pd.Series(np.random.randn(90).cumsum(), index=daily)
    print(f"重采样 日→周 mean:\n{daily_ts.resample('W').mean().head(5)}\n")
    print(f"重采样 日→月 ohlc:\n{daily_ts.resample('ME').ohlc()}\n")

    # asfreq — 改变频率（不对齐的值填 NaN）
    print(f"asfreq('D'):\n{ts.asfreq('D').head(15)}\n")


# ============================================================
# §8  apply / pipe / 向量化
# ============================================================

def demo_apply_and_pipe() -> None:
    print("\n" + "=" * 60)
    print("§8  apply / pipe / 向量化")
    print("=" * 60)

    df = pd.DataFrame({
        "A": range(1, 6),
        "B": range(10, 60, 10),
        "C": np.random.uniform(0, 1, 5),
    })
    print(f"原始:\n{df}\n")

    # apply 沿行/列
    print(f"apply(np.mean, axis=0):\n{df.apply(np.mean)}\n")
    print(f"apply(np.mean, axis=1):\n{df.apply(np.mean, axis=1)}\n")
    print(f"applymap (逐元素):\n{df.applymap(lambda x: f'{x:.3f}')}\n")

    # pipe — 链式操作
    def add_column(df: pd.DataFrame, col_name: str, value: float) -> pd.DataFrame:
        return df.assign(**{col_name: value})

    def scale_column(df: pd.DataFrame, col: str, factor: float) -> pd.DataFrame:
        new_df = df.copy()
        new_df[col] = new_df[col] * factor
        return new_df

    result_pipe = (
        df
        .pipe(add_column, "D", 100)
        .pipe(scale_column, "B", 2.0)
        .pipe(lambda d: d.assign(E=d["A"] + d["B"]))
    )
    print(f"pipe 链式操作:\n{result_pipe}\n")

    # cut / qcut — 离散化
    ages = pd.Series(np.random.randint(0, 100, 20))
    print(f"pd.cut (均宽分箱):\n{pd.cut(ages, bins=4).value_counts()}\n")
    print(f"pd.qcut (均量分箱):\n{pd.qcut(ages, q=4).value_counts()}\n")

    # get_dummies — one-hot 编码
    colors = pd.Series(["red", "blue", "green", "red", "blue"])
    print(f"pd.get_dummies:\n{pd.get_dummies(colors)}\n")


# ============================================================
# §9  实战：泰坦尼克数据分析
# ============================================================

def demo_titanic_analysis() -> None:
    print("\n" + "=" * 60)
    print("§9  实战: 泰坦尼克数据分析")
    print("=" * 60)

    # 生成模拟的泰坦尼克数据集
    n = 200
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "PassengerId": range(1, n + 1),
        "Pclass": rng.choice([1, 2, 3], size=n, p=[0.24, 0.21, 0.55]),
        "Sex": rng.choice(["male", "female"], size=n, p=[0.65, 0.35]),
        "Age": rng.normal(30, 14, size=n).clip(0.5, 80),
        "SibSp": rng.poisson(0.5, size=n),
        "Parch": rng.poisson(0.4, size=n),
        "Fare": np.exp(rng.normal(3.5, 0.8, size=n)).clip(10, 500),
        "Embarked": rng.choice(["S", "C", "Q"], size=n, p=[0.7, 0.2, 0.1]),
        "Survived": rng.integers(0, 2, size=n, endpoint=True),
    })

    # 引入一些 NaN
    df.loc[rng.choice(n, 30, replace=False), "Age"] = np.nan
    df.loc[rng.choice(n, 5, replace=False), "Embarked"] = np.nan

    print(f"数据集形状: {df.shape}")
    print(f"缺失值:\n{df.isnull().sum()}\n")

    # 缺失值处理
    df["Age"] = df["Age"].fillna(df.groupby(["Pclass", "Sex"])["Age"].transform("median"))
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # 特征工程
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)
    df["AgeBin"] = pd.cut(df["Age"], bins=[0, 18, 35, 55, 80],
                          labels=["Child", "YoungAdult", "Adult", "Senior"])

    # 探索性分析
    print(f"--- 总体生还率 ---")
    print(f"Survived mean: {df['Survived'].mean():.2%}\n")

    print(f"--- 按性别 ---")
    gender_stats = df.groupby("Sex").agg(
        人数=("PassengerId", "count"),
        生还率=("Survived", "mean"),
        平均年龄=("Age", "mean"),
        平均票价=("Fare", "mean"),
    )
    print(f"{gender_stats}\n")

    print(f"--- 按舱位等级 ---")
    pclass_stats = df.groupby("Pclass").agg(
        人数=("PassengerId", "count"),
        生还率=("Survived", "mean"),
        平均票价=("Fare", "mean"),
    ).sort_index()
    print(f"{pclass_stats}\n")

    print(f"--- 按年龄组 ---")
    age_stats = df.groupby("AgeBin", observed=False).agg(
        人数=("PassengerId", "count"),
        生还率=("Survived", "mean"),
    )
    print(f"{age_stats}\n")

    # 透视表：性别 × 舱位等级
    pivot_survival = df.pivot_table(
        values="Survived",
        index="Sex",
        columns="Pclass",
        aggfunc="mean",
    )
    print(f"生还率透视 (Sex × Pclass):\n{pivot_survival}\n")


if __name__ == "__main__":
    demo_creation()
    demo_selection()
    demo_cleaning()
    demo_groupby()
    demo_merging()
    demo_reshaping()
    demo_timeseries()
    demo_apply_and_pipe()
    demo_titanic_analysis()
    print("\n✅ Pandas 基础篇全部执行完毕!")

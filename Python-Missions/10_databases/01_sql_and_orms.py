#!/usr/bin/env python3
"""
数据库与 SQL 交互 —— 完整学习脚本
涵盖：SQLite 内建操作、SQL 查询全集（CRUD/JOIN/子查询/窗口函数/CTE/事务）、
      自定义 ORM 实现 (元类/描述符)、连接池模式、
      Redis 风格键值存储自实现、LSM-Tree 原理代码
"""

import sqlite3
import threading
import time
import json
import heapq
import os
import math
from collections import defaultdict, OrderedDict
from abc import ABC, abstractmethod
from typing import Any, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field


# ============================================================
# §1  SQLite 基础 CRUD
# ============================================================

@contextmanager
def get_connection(db_path: str = ":memory:") -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def demo_sqlite_basics() -> sqlite3.Connection:
    """演示 SQLite 的完整 CRUD 操作。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # 建表
    conn.executescript("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT DEFAULT 'Unknown'
        );

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            salary REAL CHECK(salary > 0),
            dept_id INTEGER,
            hire_date DATE DEFAULT (date('now')),
            FOREIGN KEY (dept_id) REFERENCES departments(id) ON DELETE SET NULL
        );

        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            budget REAL
        );

        CREATE TABLE employee_projects (
            emp_id INTEGER REFERENCES employees(id),
            proj_id INTEGER REFERENCES projects(id),
            hours REAL DEFAULT 0,
            PRIMARY KEY (emp_id, proj_id)
        );

        CREATE INDEX idx_emp_dept ON employees(dept_id);
        CREATE INDEX idx_emp_salary ON employees(salary);
    """)

    # INSERT
    conn.executescript("""
        INSERT INTO departments (name, location) VALUES
            ('Engineering', 'Building A'),
            ('Sales', 'Building B'),
            ('HR', 'Building A'),
            ('Marketing', 'Building C');

        INSERT INTO employees (name, email, salary, dept_id) VALUES
            ('Alice Wang', 'alice@example.com', 85000, 1),
            ('Bob Li', 'bob@example.com', 72000, 1),
            ('Charlie Zhang', 'charlie@example.com', 65000, 2),
            ('Diana Chen', 'diana@example.com', 78000, 1),
            ('Eve Liu', 'eve@example.com', 58000, 3),
            ('Frank Xu', 'frank@example.com', 92000, 2),
            ('Grace Wu', 'grace@example.com', 61000, 3);

        INSERT INTO projects VALUES
            (1, 'Project Alpha', 500000),
            (2, 'Project Beta', 300000),
            (3, 'Project Gamma', 750000);

        INSERT INTO employee_projects VALUES
            (1, 1, 120), (1, 2, 80), (2, 1, 160),
            (3, 2, 90), (4, 1, 200), (5, 3, 100),
            (6, 2, 150), (6, 3, 110), (7, 3, 140);
    """)

    conn.commit()
    return conn


def demo_sql_queries(conn: sqlite3.Connection) -> None:
    print("=" * 60)
    print("§1  SQL 查询演示 (SQLite)")
    print("=" * 60)

    # SELECT / WHERE / ORDER BY / LIMIT
    print("\n--- 基础查询: 工资 > 65000 的员工 (按工资降序) ---")
    rows = conn.execute(
        "SELECT name, salary, dept_id FROM employees "
        "WHERE salary > 65000 ORDER BY salary DESC LIMIT 5"
    ).fetchall()
    for r in rows:
        print(f"  {r['name']}: ¥{r['salary']:,.0f} (dept={r['dept_id']})")

    # JOIN
    print("\n--- INNER JOIN: 员工 + 部门 ---")
    rows = conn.execute(
        "SELECT e.name, e.salary, d.name AS department, d.location "
        "FROM employees e INNER JOIN departments d ON e.dept_id = d.id "
        "ORDER BY e.salary DESC"
    ).fetchall()
    for r in rows:
        print(f"  {r['name']}: {r['salary']:,.0f} | {r['department']} @ {r['location']}")

    # LEFT JOIN
    print("\n--- LEFT JOIN: 部门 + 员工数 + 均工资 ---")
    rows = conn.execute(
        "SELECT d.name, COUNT(e.id) AS headcount, "
        "COALESCE(AVG(e.salary), 0) AS avg_salary "
        "FROM departments d LEFT JOIN employees e ON d.id = e.dept_id "
        "GROUP BY d.id, d.name ORDER BY avg_salary DESC"
    ).fetchall()
    for r in rows:
        print(f"  {r['name']}: {r['headcount']} 人, 均薪 ¥{r['avg_salary']:,.0f}")

    # 子查询
    print("\n--- 子查询: 工资高于部门平均值的员工 ---")
    rows = conn.execute(
        "SELECT e.name, e.salary, e.dept_id FROM employees e "
        "WHERE e.salary > (SELECT AVG(salary) FROM employees WHERE dept_id = e.dept_id) "
        "ORDER BY e.dept_id, e.salary DESC"
    ).fetchall()
    for r in rows:
        print(f"  {r['name']}: ¥{r['salary']:,.0f} (dept={r['dept_id']})")

    # EXISTS
    print("\n--- EXISTS: 参与了项目的员工 ---")
    rows = conn.execute(
        "SELECT name FROM employees e WHERE EXISTS "
        "(SELECT 1 FROM employee_projects ep WHERE ep.emp_id = e.id)"
    ).fetchall()
    print(f"  参与项目: {[r['name'] for r in rows]}")

    # 窗口函数
    print("\n--- 窗口函数: 每个部门内的工资排名 ---")
    rows = conn.execute(
        "SELECT name, salary, dept_id, "
        "RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rank, "
        "AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg "
        "FROM employees ORDER BY dept_id, rank"
    ).fetchall()
    for r in rows:
        print(f"  [{r['dept_id']}]#{r['rank']} {r['name']}: ¥{r['salary']:,.0f} "
              f"(dept avg: ¥{r['dept_avg']:,.0f})")

    # CTE
    print("\n--- CTE: 员工与项目参与统计 ---")
    rows = conn.execute("""
        WITH emp_hours AS (
            SELECT emp_id, COUNT(proj_id) AS proj_count,
                   SUM(hours) AS total_hours
            FROM employee_projects GROUP BY emp_id
        )
        SELECT e.name, COALESCE(eh.proj_count, 0) AS projects,
               COALESCE(eh.total_hours, 0) AS total_hours
        FROM employees e LEFT JOIN emp_hours eh ON e.id = eh.emp_id
        ORDER BY total_hours DESC
    """).fetchall()
    for r in rows:
        print(f"  {r['name']}: {r['projects']} 项目, {r['total_hours']:.0f} 小时")

    # 事务
    print("\n--- 事务: 转账演示 ---")
    conn.execute("BEGIN")
    try:
        conn.execute("UPDATE employees SET salary = salary - 5000 WHERE id = 1")
        conn.execute("UPDATE employees SET salary = salary + 5000 WHERE id = 3")
        conn.execute("COMMIT")
        print("  转账成功: Alice -> Charlie, ¥5,000")
    except Exception as e:
        conn.execute("ROLLBACK")
        print(f"  转账失败: {e}")

    # UPDATE / DELETE
    conn.execute("UPDATE employees SET salary = salary * 1.05 WHERE dept_id = 1")
    affected = conn.execute("DELETE FROM employees WHERE salary < 60000")
    print(f"\nEngineering 部门加薪 5%, 删除低薪员工 {affected.rowcount} 人")


# ============================================================
# §2  自定义 ORM
# ============================================================

class Field:
    """ORM 字段描述符。"""

    def __init__(self, column_type: str = "TEXT", primary_key: bool = False,
                 nullable: bool = True, default: Any = None,
                 unique: bool = False, foreign_key: str | None = None) -> None:
        self.column_type = column_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.foreign_key = foreign_key
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name


class IntegerField(Field):
    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("column_type", "INTEGER")
        super().__init__(**kwargs)


class FloatField(Field):
    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("column_type", "REAL")
        super().__init__(**kwargs)


class TextField(Field):
    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("column_type", "TEXT")
        super().__init__(**kwargs)


class ModelMeta(type):
    """ORM 元类 —— 自动收集字段并创建表。"""

    def __new__(mcs, name: str, bases: tuple, attrs: dict) -> type:
        if name == "Model":
            return super().__new__(mcs, name, bases, attrs)

        fields: dict[str, Field] = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields[k] = v

        attrs["_fields"] = fields
        attrs["_table_name"] = attrs.get("__tablename__", name.lower() + "s")
        return super().__new__(mcs, name, bases, attrs)


class Model(metaclass=ModelMeta):
    """ORM 基类 —— 提供 CRUD 操作。"""

    _conn: sqlite3.Connection | None = None

    @classmethod
    def set_connection(cls, conn: sqlite3.Connection) -> None:
        cls._conn = conn

    def __init__(self, **kwargs: Any) -> None:
        for field_name, field_obj in self._fields.items():
            value = kwargs.get(field_name, field_obj.default)
            setattr(self, field_name, value)

    @classmethod
    def create_table(cls) -> None:
        columns: list[str] = []
        for fname, fobj in cls._fields.items():
            col_def = f"{fname} {fobj.column_type}"
            if fobj.primary_key:
                col_def += " PRIMARY KEY AUTOINCREMENT"
            if not fobj.nullable:
                col_def += " NOT NULL"
            if fobj.unique:
                col_def += " UNIQUE"
            if fobj.foreign_key:
                col_def += f" REFERENCES {fobj.foreign_key}"
            if fobj.default is not None:
                col_def += f" DEFAULT {fobj.default!r}"
            columns.append(col_def)

        sql = f"CREATE TABLE IF NOT EXISTS {cls._table_name} ({', '.join(columns)})"
        cls._conn.execute(sql)  # type: ignore[union-attr]
        cls._conn.commit()  # type: ignore[union-attr]

    def save(self) -> None:
        fields = [k for k, v in self._fields.items() if not v.primary_key]
        values = [getattr(self, f) for f in fields]
        placeholders = ", ".join(["?"] * len(fields))
        sql = (f"INSERT INTO {self._table_name} ({', '.join(fields)}) "
               f"VALUES ({placeholders})")
        cur = self._conn.execute(sql, values)  # type: ignore[union-attr]
        self._conn.commit()  # type: ignore[union-attr]

        for fname, fobj in self._fields.items():
            if fobj.primary_key:
                setattr(self, fname, cur.lastrowid)
                break

    @classmethod
    def all(cls) -> list["Model"]:
        sql = f"SELECT * FROM {cls._table_name}"
        rows = cls._conn.execute(sql).fetchall()  # type: ignore[union-attr]
        return [cls(**dict(r)) for r in rows]

    @classmethod
    def filter(cls, **conditions: Any) -> list["Model"]:
        where_clause = " AND ".join(f"{k}=?" for k in conditions)
        values = list(conditions.values())
        sql = f"SELECT * FROM {cls._table_name} WHERE {where_clause}"
        rows = cls._conn.execute(sql, values).fetchall()  # type: ignore[union-attr]
        return [cls(**dict(r)) for r in rows]

    @classmethod
    def get(cls, id_value: int) -> "Model | None":
        pk = next((k for k, v in cls._fields.items() if v.primary_key), "id")
        sql = f"SELECT * FROM {cls._table_name} WHERE {pk}=?"
        row = cls._conn.execute(sql, (id_value,)).fetchone()  # type: ignore[union-attr]
        return cls(**dict(row)) if row else None

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={getattr(self, k)!r}"
                          for k in self._fields)
        return f"{self.__class__.__name__}({attrs})"


# ============================================================
# §3  LSM-Tree 风格键值存储
# ============================================================

@dataclass
class SSTable:
    """Sorted String Table —— LSM-Tree 的磁盘层。"""
    filename: str
    data: OrderedDict[str, str] = field(default_factory=OrderedDict)

    def write(self, memtable: dict[str, str]) -> None:
        sorted_items = sorted(memtable.items())
        with open(self.filename, "w", encoding="utf-8") as f:
            for k, v in sorted_items:
                f.write(f"{len(k):08d}{k}{len(v):08d}{v}")
        self.data = OrderedDict(sorted_items)

    def read(self, key: str) -> str | None:
        if key not in self.data:
            return None
        return self.data[key]

    @classmethod
    def from_file(cls, filename: str) -> "SSTable | None":
        if not os.path.exists(filename):
            return None
        data = OrderedDict()
        with open(filename, "r", encoding="utf-8") as f:
            while True:
                len_k_bytes = f.read(8)
                if not len_k_bytes:
                    break
                len_k = int(len_k_bytes)
                k = f.read(len_k)
                len_v = int(f.read(8))
                v = f.read(len_v)
                data[k] = v
        return cls(filename, data)


class LSMEngine:
    """LSM-Tree 键值存储引擎的简化实现。

    结构: WAL (Write-Ahead Log) → MemTable → SSTable
    """

    def __init__(self, db_path: str = "lsm_db",
                 memtable_size: int = 100) -> None:
        self.db_path = db_path
        self.memtable_size = memtable_size
        os.makedirs(db_path, exist_ok=True)

        # WAL
        self.wal_path = os.path.join(db_path, "wal.log")
        self.wal_file = open(self.wal_path, "a+", encoding="utf-8")

        # MemTable (活跃内存表)
        self.memtable: OrderedDict[str, str] = OrderedDict()

        # SSTable 层 (按时间排序)
        self.sstables: list[SSTable] = []
        self._recover()

    def _recover(self) -> None:
        """从 WAL 恢复未刷新的数据。"""
        self.wal_file.seek(0)
        for line in self.wal_file:
            if line.strip():
                op, key, *rest = line.strip().split("\t", 2)
                if op == "PUT":
                    self.memtable[key] = rest[0] if rest else ""
                elif op == "DEL":
                    self.memtable.pop(key, None)

        # 加载已有 SSTable
        for fname in sorted(os.listdir(self.db_path)):
            if fname.endswith(".sst"):
                sst = SSTable.from_file(os.path.join(self.db_path, fname))
                if sst:
                    self.sstables.append(sst)

    def _flush_memtable(self) -> None:
        """将 MemTable 刷写到 SSTable。"""
        if not self.memtable:
            return

        sst_name = os.path.join(
            self.db_path,
            f"sst_{len(self.sstables):06d}.sst"
        )
        sst = SSTable(sst_name)
        sst.write(dict(self.memtable))
        self.sstables.append(sst)

        self.memtable.clear()

        # 截断 WAL
        self.wal_file.close()
        self.wal_file = open(self.wal_path, "w", encoding="utf-8")

    def put(self, key: str, value: str) -> None:
        self.wal_file.write(f"PUT\t{key}\t{value}\n")
        self.wal_file.flush()
        self.memtable[key] = value

        if len(self.memtable) >= self.memtable_size:
            self._flush_memtable()

    def get(self, key: str) -> str | None:
        # 先查 MemTable
        if key in self.memtable:
            return self.memtable[key]

        # 再查 SSTable (从新到旧)
        for sst in reversed(self.sstables):
            val = sst.read(key)
            if val is not None:
                return val

        return None

    def delete(self, key: str) -> None:
        self.wal_file.write(f"DEL\t{key}\n")
        self.wal_file.flush()
        self.memtable.pop(key, None)

    def compact(self) -> None:
        """合并所有 SSTable 为一个 (简化版合并)。"""
        if len(self.sstables) <= 1:
            return

        merged: dict[str, str] = {}
        for sst in self.sstables:
            merged.update(sst.data)

        # 删除旧 SSTables
        for sst in self.sstables:
            os.remove(sst.filename)

        self.sstables.clear()

        sst = SSTable(os.path.join(self.db_path, "sst_000000.sst"))
        sst.write(merged)
        self.sstables.append(sst)

    def close(self) -> None:
        self._flush_memtable()
        self.wal_file.close()


# ============================================================
# §4  连接池
# ============================================================

class ConnectionPool:
    """简单的数据库连接池。"""

    def __init__(self, db_path: str, min_conn: int = 2,
                 max_conn: int = 10) -> None:
        self.db_path = db_path
        self.min_conn = min_conn
        self.max_conn = max_conn
        self._pool: list[sqlite3.Connection] = []
        self._in_use: set[sqlite3.Connection] = set()
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

        for _ in range(min_conn):
            self._pool.append(self._create_connection())

    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def acquire(self, timeout: float = 5.0) -> sqlite3.Connection:
        end_time = time.time() + timeout
        with self._condition:
            while True:
                if self._pool:
                    conn = self._pool.pop()
                    self._in_use.add(conn)
                    return conn
                if len(self._in_use) < self.max_conn:
                    conn = self._create_connection()
                    self._in_use.add(conn)
                    return conn
                remaining = end_time - time.time()
                if remaining <= 0:
                    raise TimeoutError("获取连接超时")
                self._condition.wait(remaining)

    def release(self, conn: sqlite3.Connection) -> None:
        with self._condition:
            if conn in self._in_use:
                self._in_use.discard(conn)
                if len(self._pool) < self.min_conn:
                    self._pool.append(conn)
                else:
                    conn.close()
                self._condition.notify()

    def close_all(self) -> None:
        with self._lock:
            for conn in self._pool:
                conn.close()
            for conn in self._in_use:
                conn.close()
            self._pool.clear()
            self._in_use.clear()


# ============================================================
# §5  查询优化器基础
# ============================================================

class SimpleQueryPlanner:
    """简单的查询代价估算器 —— 用于理解数据库查询优化原理。"""

    def __init__(self, stats: dict[str, dict[str, float]]) -> None:
        """
        stats = {table_name: {"rows": int, "distinct(col)": int, ...}}
        """
        self.stats = stats

    def estimate_cardinality(self, table: str,
                             conditions: dict[str, Any] | None = None) -> int:
        if table not in self.stats:
            return 0
        rows = int(self.stats[table].get("rows", 0))
        if not conditions:
            return rows

        # 简化估算: 假设条件均匀分布
        selectivity = 1.0
        for col, val in conditions.items():
            key = f"distinct({col})"
            if key in self.stats[table]:
                selectivity *= 1.0 / self.stats[table][key]

        return max(1, int(rows * selectivity))

    def estimate_join_cost(self, table1: str, table2: str,
                           join_conditions: dict[str, str]) -> dict[str, float]:
        """估算两种 JOIN 方式的代价。"""
        rows1 = self.estimate_cardinality(table1)
        rows2 = self.estimate_cardinality(table2)

        nested_loop_cost = rows1 * rows2
        hash_join_cost = rows1 + rows2

        return {
            "nested_loop": nested_loop_cost,
            "hash_join": hash_join_cost,
            "recommended": "hash_join" if hash_join_cost < nested_loop_cost else "nested_loop",
        }

    def plan_query(self, query: dict[str, Any]) -> dict[str, Any]:
        """为查询选择最优执行计划。"""
        plan = {"steps": [], "total_cost": 0.0}

        if query.get("type") == "select":
            table = query["table"]
            conditions = query.get("conditions", {})
            cardinality = self.estimate_cardinality(table, conditions)
            cost = cardinality
            plan["steps"].append({
                "operation": f"SCAN {table}",
                "estimated_rows": cardinality,
                "cost": cost,
            })
            plan["total_cost"] += cost

        if query.get("type") == "join":
            join_info = self.estimate_join_cost(
                query["table1"], query["table2"],
                query.get("on", {}),
            )
            plan["steps"].append({
                "operation": f"JOIN {join_info['recommended']}",
                "cost": join_info[join_info["recommended"]],
            })
            plan["total_cost"] += join_info[join_info["recommended"]]

        return plan


# ============================================================
# §6  演示
# ============================================================

def demo_database_full() -> None:
    # SQLite 演示
    conn = demo_sqlite_basics()
    demo_sql_queries(conn)
    conn.close()

    # ORM 演示
    print("\n" + "=" * 60)
    print("§2  ORM 演示")
    print("=" * 60)

    orm_conn = sqlite3.connect(":memory:")
    orm_conn.row_factory = sqlite3.Row
    Model.set_connection(orm_conn)

    class User(Model):
        __tablename__ = "users"
        id = IntegerField(primary_key=True)
        username = TextField(nullable=False, unique=True)
        email = TextField(nullable=False)
        age = IntegerField(default=18)

    User.create_table()

    u1 = User(username="alice", email="alice@a.com", age=25)
    u1.save()
    u2 = User(username="bob", email="bob@a.com", age=30)
    u2.save()

    users = User.all()
    print(f"所有用户: {users}")
    print(f"按 username 过滤: {User.filter(username='alice')}")
    print(f"按 ID 获取: {User.get(1)}")
    orm_conn.close()

    # LSM 演示
    print("\n" + "=" * 60)
    print("§3  LSM-Tree 键值存储演示")
    print("=" * 60)

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        lsm = LSMEngine(tmpdir, memtable_size=5)
        for i in range(15):
            lsm.put(f"key_{i}", f"value_{i}")
        print(f"put 15 keys (memtable flushed at 5)")
        print(f"get key_3: {lsm.get('key_3')}")
        print(f"get key_10: {lsm.get('key_10')}")
        print(f"memtable size: {len(lsm.memtable)}")
        print(f"sstables: {len(lsm.sstables)}")

        lsm.compact()
        print(f"compacted: {len(lsm.sstables)} sstable(s)")
        lsm.close()

    # 连接池演示
    print("\n" + "=" * 60)
    print("§4  连接池演示")
    print("=" * 60)

    pool = ConnectionPool(":memory:", min_conn=2, max_conn=5)
    conn1 = pool.acquire()
    conn2 = pool.acquire()
    print(f"获取 2 个连接, pool 剩余: {len(pool._pool)}, in_use: {len(pool._in_use)}")
    pool.release(conn1)
    pool.release(conn2)
    print(f"释放后 pool: {len(pool._pool)}, in_use: {len(pool._in_use)}")
    pool.close_all()

    # 查询优化器
    print("\n" + "=" * 60)
    print("§5  查询优化器演示")
    print("=" * 60)

    stats = {
        "employees": {"rows": 100000, "distinct(dept_id)": 10, "distinct(salary)": 5000},
        "departments": {"rows": 10, "distinct(id)": 10},
    }
    planner = SimpleQueryPlanner(stats)
    plan = planner.plan_query({"type": "select", "table": "employees",
                               "conditions": {"dept_id": 3}})
    print(f"SELECT 执行计划: {plan}")

    join_plan = planner.plan_query({"type": "join", "table1": "employees",
                                     "table2": "departments", "on": {"dept_id": "id"}})
    print(f"JOIN 执行计划: {join_plan}")


if __name__ == "__main__":
    demo_database_full()
    print("\n✅ 数据库篇执行完毕!")

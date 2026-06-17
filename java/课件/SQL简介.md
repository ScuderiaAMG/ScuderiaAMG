# SQL简介

---

## 一、本章概述

本章涵盖以下主要内容：

- **关系数据库回顾**
- **T-SQL基本知识**：命名规则、数据类型、基本运算、常用函数、流程控制
- **数据定义语言（DDL）**：数据库、表、索引、视图
- **数据修改语言（DML）**：INSERT、UPDATE、DELETE
- **数据查询语言（DQL）**：SELECT
- **存储过程**、**触发器**、**游标**

---

## 二、数据库系统概述

### 2.1 数据库系统的构成

```
数据库最终用户
    ↓
应用系统 / 应用开发工具
    ↓
DBMS（数据库管理系统）
    ↓
操作系统
```

**核心角色**：
- **DBA（数据库管理员）**：负责数据库的管理和维护
- **应用程序员**：负责开发数据库应用程序

### 2.2 常见关系数据库（RDBMS）

| 数据库 | 说明 |
|--------|------|
| DB2 | IBM |
| Oracle | Oracle Corporation |
| MSSQL Server | Microsoft |

> 本章以 **MSSQL Server** 为背景来介绍 T-SQL。

---

## 三、关系数据库常见对象

### 3.1 表（Table / 关系 Relation）

表是关系数据库中最基本的对象，由行（记录/元组）和列（字段/属性）组成。

**示例——Students表**：

| code | myname | birthday | score |
|------|--------|----------|:-----:|
| 200101184022 | 王涛 | 1983/3/9 | 84 |
| 200201184358 | 于栋 | 1982/10/15 | 95 |

**关系模式**：对关系的描述，一般表示为：
```
关系名(属性1, 属性2, ..., 属性n)
```
其中加**下划线**表示这些属性的集合构成**键码（主键）**。

### 3.2 索引（Index）

为表建立的一种实现**快速查询**的工具。

| 类型 | 说明 | 特点 |
|------|------|------|
| **簇索引（聚集索引）** | 行的物理顺序和行的索引顺序相同 | 使UPDATE和SELECT操作大大加速；**每个表只能有一个**；定义键时使用的列越少越好 |
| **非簇索引（非聚集索引）** | 指定表的逻辑顺序 | 行的物理顺序和索引顺序不尽相同；**每个表可以有多个** |

### 3.3 存储过程（Stored Procedure）

多个SQL语句的**有机集合**。存储在服务器端，可被重复调用。

### 3.4 触发器（Trigger）

一种特殊的存储过程，当满足一定的条件时，会**自动触发**它执行。多用来保证表中数据的**一致性**。

### 3.5 视图（View）

可以看成是**虚拟表**或**存储查询**。视图不作为独特的对象存储，数据库内存储的是**SELECT语句**。

**示例**：
```sql
SELECT code FROM Students
-- 该SELECT语句的结果即构成一个视图
```

---

## 四、SQL的发展与命令分类

### 4.1 SQL发展简史

| 时间 | 事件 |
|------|------|
| 1974年 | CHAMBERLIN和BOYEE提出SEQUEL（A Structured English Query Language） |
| 1976年 | 推出第二版本SEQUEL/2 |
| 1980年 | 更名为SQL |
| 至今 | SQL发展成RDBMS的标准接口，各RDBMS对SQL有扩展 |

**T-SQL（Transact SQL）**：Sybase公司对SQL的扩充版本。各厂商的扩展无太大冲突。

### 4.2 SQL命令分类

| 分类 | 英文 | 说明 | 常用命令 |
|:----:|------|------|----------|
| **DDL** | Data Definition Language（数据定义语言） | 创建、修改、删除数据库对象 | CREATE、ALTER、DROP |
| **DML** | Data Manipulation Language（数据修改语言） | 对数据的插入、删除和修改 | INSERT、DELETE、UPDATE |
| **DQL** | Data Query Language（数据查询语言） | 实现选择、投影、连接等关系操作 | SELECT |
| **DCL** | Data Control Language（数据控制语言） | 保证数据存取的安全性 | 口令、授权等 |
| **TCL** | Transaction Control Language（事务控制语言） | 保证数据完整性、一致性、可恢复性 | COMMIT、ROLLBACK |

### 4.3 SQL三级模式结构

```
        外模式          模式            内模式
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │ 视图1   │    │  表1 表2 │    │ 存储文件1 │
    │ 视图2   │ ← │  表3 表4 │ ← │ 存储文件2 │
    └─────────┘    └──────────┘    └──────────┘
        SQL
```

---

## 五、T-SQL基本知识

### 5.1 命名规则

| 规则 | 说明 |
|------|------|
| **开头字符** | 必须以字母a-z/A-Z、下划线(_)、at符号(@)或者数字符号(#)开头 |
| **后续字符** | 可以是字母、十进制数字、@、#、美元符号($)或下划线 |
| **特殊标识符** | `@`开头表示局部变量或参数；`#`开头表示临时表或过程；`##`开头表示全局临时对象 |
| **@@函数** | 某些T-SQL函数的名称以@@开始，建议不要使用以@@开头的名称 |
| **禁止字符** | 标识符不能是保留字（大小写形式都不行），不允许嵌入空格或其他特殊字符 |

### 5.2 变量的声明和赋值

**声明变量**：
```sql
DECLARE @local_variable data_type
-- 变量在声明后均初始化为NULL
```

**赋值**：
```sql
SET @local_variable = value
-- 或
SELECT @local_variable = value
```

**示例**：
```sql
DECLARE @find varchar(30)
SET @find = 'Ring%'
SELECT au_lname, au_fname, phone FROM authors
WHERE au_lname LIKE @find

DECLARE @pub_id char(4), @hire_date datetime
SET @pub_id = '0877'
SET @hire_date = '1/1/2003'
```

### 5.3 基本数据类型

| 分类 | 数据类型 | 说明 |
|------|----------|------|
| **整数** | `int` | 从 -2³¹ 到 2³¹-1 的整数 |
| **比特** | `bit` | 1或0的整数 |
| **近似数字** | `float` | 从 -1.79E+308 到 1.79E+308 的浮点精度数字 |
| | `real` | 从 -3.40E+38 到 3.40E+38 的浮点精度数字 |
| **字符串** | `char(n)` | 固定长度的非Unicode字符数据，最长8,000个字符 |
| | `varchar(n)` | 可变长度的非Unicode字符数据，最长8,000个字符。不指定n则默认长度为1 |
| **Unicode字符** | `nchar(n)` / `nvarchar(n)` | 采用双字节对字符进行编码，有前缀N |
| **日期** | `datetime` | 从1753年1月1日到9999年12月31日的日期和时间数据，精确到3.33毫秒 |

**Unicode常量示例**：`'Michél'` 是字符串常量，`N'Michél'` 则是Unicode常量。

**日期格式**（SQL Server可识别）：

| 格式 | 示例 |
|------|------|
| 字母日期格式 | `'April 15, 1998'` |
| 数字日期格式（分隔符为/、-或.） | `'4/15/1998'`、`'1990-10-02'`、`'04-15-1996'` |
| 未分隔的字符串格式 | `'19981207'` |

### 5.4 基本运算

#### 5.4.1 字符串串联（+）

```sql
SELECT (au_lname + ', ' + au_fname) AS Name FROM authors
```

#### 5.4.2 逻辑运算符

| 运算符 | 说明 |
|--------|------|
| `=` | 等于 |
| `>` | 大于 |
| `<` | 小于 |
| `>=` | 大于等于 |
| `<=` | 小于等于 |
| `<>`、`!=` | 不等于 |
| `!<` | 不小于 |
| `!>` | 不大于 |

#### 5.4.3 注释

```sql
-- 单行注释（双连字符）

/* 多行注释
   text_of_comment */
```

#### 5.4.4 BETWEEN（范围测试）

```sql
-- 语法
test_expression [NOT] BETWEEN begin_expression AND end_expression

-- 示例
WHERE payment NOT BETWEEN 4095 AND 12000
```

#### 5.4.5 IN（成员测试）

```sql
-- 语法
test_expression [NOT] IN (subquery | expression [, ...n])

-- 示例
WHERE state IN ('CA', 'IN', 'MD')
-- 等价于: WHERE state = 'CA' OR state = 'IN' OR state = 'MD'

WHERE au_id NOT IN (SELECT au_id FROM author WHERE age < 50)
```

#### 5.4.6 LIKE（模式匹配）

```sql
-- 语法
match_expression [NOT] LIKE pattern

-- 示例
WHERE au_name LIKE 'Jo%'
```

#### 5.4.7 通配符

| 通配符 | 说明 | 示例 |
|:------:|------|------|
| `%` | 匹配包含零个或多个字符的任意字符串 | `'50%'` 匹配以"50"开头的字符串 |
| `_` | 匹配任意单个字符 | `'_ean'` 匹配如"Dean"、"Jean"等 |
| `[ ]` | 匹配指定范围内的任意单个字符 | `'[A-C]arsen'` 匹配"Arsen"、"Barsen"、"Carsen" |
| `[^]` | 匹配不处于指定范围内的任意单个字符 | `'de[^a]%'` 匹配以"de"开头但第三个字符不是a的字符串 |

**通配符注意事项**：

| 注意点 | 示例 |
|--------|------|
| 转义`%` | `WHERE au_lname LIKE '50[%]'` —— 匹配字面值"50%" |
| `[^ab]` vs `[^a][^b]` | `[^ab]` 等价于 `[^a^b]`，表示一位不能是a或b；`[^a][^b]` 表示两个相连字符相继不能是a和b |

### 5.5 常用函数

#### 5.5.1 聚合函数

| 函数 | 语法 | 说明 | 示例 |
|:----:|------|------|------|
| **COUNT** | `COUNT({[ALL\|DISTINCT] expression\|*})` | 返回组中项目的数量（不含NULL，COUNT(*)含NULL） | `SELECT COUNT(DISTINCT city) FROM students` |
| **SUM** | `SUM([ALL\|DISTINCT] expression)` | 返回表达式中值的和（仅数字列，忽略NULL） | `SELECT SUM(score) FROM sScores` |
| **AVG** | `AVG([ALL\|DISTINCT] expression)` | 返回组中值的平均值（忽略NULL） | `SELECT AVG(score) FROM sScores` |
| **MAX** | `MAX([ALL\|DISTINCT] expression)` | 返回最大值（可用于数字/字符/datetime，不能用于bit） | `SELECT MAX(age) FROM students` |
| **MIN** | `MIN([ALL\|DISTINCT] expression)` | 返回最小值（可用于数字/char/varchar/datetime，不能用于bit） | `SELECT MIN(age) FROM students` |

#### 5.5.2 字符处理函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `LOWER(char_expression)` | 将大写转换为小写字符 | `SELECT LOWER('HELLO')` → 'hello' |
| `UPPER(char_expression)` | 将小写转换为大写字符 | `SELECT UPPER('hello')` → 'HELLO' |
| `RIGHT(char_expr, integer_expr)` | 返回从右边开始指定个数的字符 | `SELECT RIGHT('abcdef', 3)` → 'def' |
| `LEFT(char_expr, integer_expr)` | 返回从左边开始指定个数的字符 | `SELECT '入学年份' = LEFT(st_id, 4) FROM students` |
| `SUBSTRING(expr, start, length)` | 返回字符串的一部分 | `SELECT SUBSTRING('abcdef', 2, 3)` → 'bcd' |
| `LEN(string_expression)` | 返回字符个数（不含尾随空格） | `SELECT LEN('hello ')` → 5 |
| `REPLACE(s1, s2, s3)` | 用s3替换s1中所有出现的s2 | `SELECT REPLACE('abcabc', 'a', 'x')` → 'xbcxbc' |
| `SPACE(integer_expr)` | 返回指定数量空格组成的字符串 | `SELECT SPACE(5)` |

#### 5.5.3 日期处理函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `MONTH(date)` | 返回代表指定日期月份的整数 | `SELECT MONTH('03/12/2003')` → 3 |
| `DAY(date)` | 返回代表指定日期的天数 | `SELECT DAY('03/12/2003')` → 12 |
| `YEAR(date)` | 返回代表指定日期的年份 | `SELECT YEAR(0)` → 1900（SQL Server将0解释为'01/01/1900'） |
| `GETDATE()` | 返回当前系统日期和时间 | `SELECT GETDATE()` |

**GETDATE()在表定义中的应用**：
```sql
CREATE TABLE Score(
    stu_id char(11) NOT NULL,
    cos_name varchar(40) NOT NULL,
    exam_date datetime DEFAULT GETDATE()
)
```

#### 5.5.4 类型判断函数

| 函数 | 说明 |
|------|------|
| `ISNUMERIC(expression)` | 判断是否为有效数字类型 |
| `ISDATE(expression)` | 判断是否为有效的日期 |

---

## 六、数据定义语言（DDL）

### 6.1 数据库的建立与删除

**建立数据库**：
```sql
CREATE DATABASE UserTest
ON (NAME = UserTest_Data,
    FILENAME = 'D:\TEST_Data.mdf',  -- 数据文件
    SIZE = 1,                        -- 初始大小为1MB
    MAXSIZE = 500,                   -- 最大只能到500MB
    FILEGROWTH = 10%)                -- 以10%的速度增大空间
LOG ON
(NAME = UserTest_Log,
    FILENAME = 'D:\TEST_Log.ldf',    -- 日志文件
    SIZE = 1,
    MAXSIZE = 500,
    FILEGROWTH = 10%)
```

**删除数据库**：
```sql
DROP DATABASE UserTest
```

**使用数据库**：
```sql
USE UserTest  -- 下面的SQL语句均在UserTest中执行
```

**注意**：一批SQL语句中间没有 `GO` 的话，会一起提交。需要：
```sql
CREATE DATABASE UserTest
GO
USE UserTest
```

正在使用的数据库不能被删除。

### 6.2 表的建立（CREATE TABLE）

**基本语法**：
```sql
CREATE TABLE 表名 (
    列名1 数据类型1,
    列名2 数据类型2,
    主键说明,
    外部键说明
)
```

**约束定义**：

| 约束类型 | 语法 | 说明 |
|----------|------|------|
| **主键** | `CONSTRAINT 约束名 PRIMARY KEY [CLUSTERED\|NONCLUSTERED] (列名)` | 不能定义在可为空列上；每个表只能创建一个 |
| **外部键** | `CONSTRAINT 约束名 FOREIGN KEY (本表列名) REFERENCES 另一表(表2中对应列名)` | 表2中对应列必须为主键 |
| **唯一约束** | `UNIQUE` | 保证列值唯一 |
| **检查约束** | `CHECK (条件)` | 验证数据有效性 |
| **默认值** | `DEFAULT 值` | 插入时的默认值 |

**约束名在整个数据库中要唯一**。

**完整示例**：
```sql
-- 系别表
CREATE TABLE st_Dept(
    deptno integer NOT NULL
        CONSTRAINT pk_st_Dept PRIMARY KEY,
    deptname varchar(50) NOT NULL
        CONSTRAINT upper_name
        CHECK (deptname = UPPER(deptname)),
    fdtime datetime DEFAULT GETDATE()
)

-- 学生表
CREATE TABLE Students(
    st_id integer NOT NULL UNIQUE,
    st_name varchar(50) NOT NULL,
    pwd varchar(20) NULL DEFAULT '0000',
    birthday datetime NULL
        CONSTRAINT cc_birth
        CHECK (Year(birthday) > 1985),
    st_dept integer NOT NULL,
    CONSTRAINT pk_Students PRIMARY KEY NONCLUSTERED (st_id),
    CONSTRAINT fk_Students FOREIGN KEY (st_dept)
        REFERENCES st_Dept(deptno)
)
```

### 6.3 表的修改（ALTER TABLE）

```sql
ALTER TABLE table
    [ ALTER COLUMN 列名 数据类型等属性 ]
    | ADD [ 列的定义 | 约束的定义 ]
    | DROP { [CONSTRAINT] 约束名 | COLUMN 列名 }
    | { CHECK | NOCHECK } CONSTRAINT { ALL | 约束名 }
    | { ENABLE | DISABLE } TRIGGER { ALL | 触发器名 }
```

**示例**：
```sql
-- 不检查出生年份约束
ALTER TABLE Students NOCHECK CONSTRAINT cc_birth

-- 修改列属性
ALTER TABLE Students ALTER COLUMN st_name integer NULL

-- 添加约束
ALTER TABLE Students ADD CONSTRAINT
    pk2_Students PRIMARY KEY NONCLUSTERED (st_name)

-- 删除约束
ALTER TABLE Students DROP pk_Students
```

**注意**：
- 不能改已经对它建立了约束（主键、外部键、UNIQUE等）的列的属性
- 不能删除正由一个FOREIGN KEY约束引用的表，必须先删除引用的FOREIGN KEY约束或引用的表

### 6.4 表的删除（DROP TABLE）

```sql
DROP TABLE 表名

-- 删除有外键关系的表时需注意顺序
DROP TABLE Students
GO
DROP TABLE st_Dept
```

---

## 七、数据修改语言（DML）——INSERT

### 7.1 INSERT语法

```sql
INSERT [INTO] { 表名 | 视图名 } [ ( 列名列表 ) ]
{ VALUES ( { DEFAULT | NULL | 表达式 } )
| derived_table }
```

**参数说明**：
- `DEFAULT`：强制该列值为为该列定义的默认值。如果不存在默认值且该列允许NULL，则插入NULL
- `derived_table`：任何有效的SELECT语句

### 7.2 INSERT示例

```sql
-- 基本插入
INSERT st_Dept VALUES (184, 'AUTOMATIC CONTROL', DEFAULT)

INSERT Students VALUES (2000184013, '王菲', DEFAULT, '1976-01-01', 184)

-- 使用SELECT子查询插入
INSERT Students
SELECT st_id+10, Left(st_name,1)+'燕', pwd, '4-3-1985', st_dept
FROM Students WHERE Left(st_name,1) = '王'
```

### 7.3 INSERT注意事项

| 规则 | 说明 |
|------|------|
| **主键** | 不能为空和重复 |
| **NOT NULL列** | 不允许为空的列必须给予赋值 |
| **约束** | 赋的值要满足约束条件 |
| **外部键** | 如果要在有外部键的表中插入数据，对应外部键的列值必须在被参照表中存在 |

---

## 八、数据查询语言（DQL）——SELECT

### 8.1 SELECT基本语法

```sql
SELECT select_list         -- 要查询的内容
[ INTO new_table ]          -- 将结果存放到一个新表
FROM table_source           -- 指定所使用的表、视图
[ WHERE search_condition ]  -- 查询的条件
[ GROUP BY group_by_expression ]  -- 分组
[ ORDER BY order_expression [ ASC | DESC ] ]  -- 排序
```

### 8.2 SELECT子句

```sql
SELECT [ ALL | DISTINCT ] [ TOP n [ PERCENT ] ] <select_list>
```

| 选项 | 说明 |
|------|------|
| `ALL`（默认）| 返回所有行（包括重复），空值认为相等 |
| `DISTINCT` | 去除重复行 |
| `TOP n [PERCENT]` | 只输出前n行或前n%行；带ORDER BY时输出排序后的前n行 |

**示例**：
```sql
-- 输出最低的10种英语成绩
SELECT DISTINCT TOP 10 Eng_score
FROM st_score
ORDER BY Eng_score ASC
```

### 8.3 AS子句（别名）

为结果集列指定不同的名称或别名。

**示例**：
```sql
SELECT EmpSSN AS "Employee Social Security Number" FROM EmpTable

-- 查询各个年级的英语平均成绩
SELECT Left(st_id, 4) AS grade#,
    Sum(Eng_score) / Count(Eng_score) AS Avg_Eng
FROM st_score
GROUP BY Left(st_id, 4)
ORDER BY grade# ASC
-- 注意：GROUP BY子句不能利用别名grade#
```

### 8.4 INTO子句

将查询结果保存到一个新表/临时表中。

```sql
SELECT Cust_Name, Country, City, Phone
INTO #CustomerResults    -- #开头表示临时表
FROM Customers
WHERE Country IN('USA','Canada')
UNION
SELECT Cust_Name, Country, City, Phone
FROM SouthAmericanCustomers
```

### 8.5 UNION子句

将多个查询的结果组合成单个结果集：
- 结果集显示的列名是**前一个SELECT的列名**
- 包含联合查询中所有查询的全部行
- 如果列类型不一致，会将后一个结果转换成前一个结果的列数据类型
- **两表列数不同则不能用UNION**

**注意**：`SELECT * FROM A UNION SELECT * FROM B` 与 `SELECT * FROM B UNION SELECT * FROM A` 结果不同（列名和顺序取决于前一个SELECT）。

### 8.6 连接查询（JOIN）

```sql
-- INNER JOIN 示例
SELECT ytd_sales AS Sales,
    authors.au_fname + ' ' + authors.au_lname AS Author
INTO #Tmp_count
FROM titles
    INNER JOIN titleauthor ON titles.title_id = titleauthor.title_id
    INNER JOIN authors ON titleauthor.au_id = authors.au_id
ORDER BY Sales DESC, Author ASC
```

### 8.7 子查询（Subquery）

**子查询类型对比**：

| 类型 | 说明 | 运算符 |
|------|------|--------|
| 标量子查询 | 返回单个值 | =, >, <, ... |
| 列表子查询 | 返回一列值 | IN, NOT IN |
| EXISTS子查询 | 测试是否存在符合条件的行 | EXISTS, NOT EXISTS |

**示例——最高英语成绩的学生**：
```sql
SELECT st_id, Eng_score
FROM st_score
WHERE Eng_score = (SELECT Max(Eng_score) FROM st_score)
ORDER BY st_id
```

**示例——英语成绩为100的学生（三种写法等价）**：
```sql
-- 方式一：IN + 子查询
SELECT DISTINCT st_name FROM students
WHERE st_id IN (SELECT st_id FROM st_score WHERE Eng_score = 100)

-- 方式二：多表连接
SELECT DISTINCT st_name
FROM students a, st_score b
WHERE a.st_id = b.st_id AND b.Eng_score = 100

-- 方式三：IN + 复合条件
SELECT DISTINCT st_name INTO #highscore
FROM students
WHERE 100 IN (SELECT Eng_score FROM st_score
              WHERE st_score.st_id = students.st_id)
```

**示例——EXISTS用法**：
```sql
-- 查询存在check类型账户的客户名称（三种写法等价）
-- EXISTS
SELECT DISTINCT cust_name FROM customers
WHERE EXISTS (SELECT * FROM accounts
              WHERE acc_id = customers.acc_id AND type = 'check')

-- IN
SELECT DISTINCT cust_name FROM customers
WHERE acc_id IN (SELECT acc_id FROM accounts WHERE type = 'check')

-- JOIN
SELECT DISTINCT cust_name
FROM customers AS a INNER JOIN accounts AS b ON a.acc_id = b.acc_id
WHERE b.type = 'check'
```

### 8.8 三表联合查询

```sql
-- 查询在'import'类型的课程中考过最高分的学生名字
-- 方式一：多表连接
SELECT st_name
FROM students a, st_highscore b, courses c
WHERE a.st_id = b.st_id AND b.course_id = c.course_id
    AND c.type = 'import'

-- 方式二：嵌套子查询
SELECT st_name FROM students
WHERE st_id IN (
    SELECT st_id FROM st_highscore
    WHERE course_id IN (
        SELECT course_id FROM courses WHERE type = 'import'
    )
)
```

### 8.9 SELECT步骤总结

| 步骤 | 操作 | 说明 |
|:----:|------|------|
| I | 分析查询内容和条件分布在哪些表中 | 确定涉及的表 |
| II | 在SELECT子句中写要查询的内容 | 使用"表名.列名"引用 |
| III | 在FROM子句中写所涉及的表 | 多个表用逗号或JOIN |
| IV | 在WHERE子句中写所有的条件 | 各种条件组合 |
| V | 如需分组加入GROUP BY子句 | — |
| VI | 如需排序利用ORDER BY子句 | ASC升序 / DESC降序 |
| VII | 如需保存结果利用INTO子句 | 临时表或永久表 |

---

## 九、数据修改语言（DML）——UPDATE/DELETE

### 9.1 UPDATE

**语法**：
```sql
UPDATE 表名
SET 列名1 = 值1, 列名2 = 值2, ...
[ WHERE 条件 ]
```

**注意**：如果不加WHERE条件，将更新全部行。

### 9.2 DELETE

**语法**：
```sql
DELETE FROM 表名
[ WHERE 条件 ]
```

**注意**：如果不加WHERE条件，将删除全部行。

---

## 十、存储过程（Stored Procedure）

### 10.1 为什么要使用存储过程

**客户端直接发送SQL的问题**：
- 客户端数据需要通过多层网络软件
- 服务器在解释消息前也必须通过多层网络软件
- 服务器必须对SQL语句进行解释、优化、执行
- 返回结果集也需要经过多层网络软件（尤其结果集过大时）
- 每个数据库请求以单个SQL语句形式发送，客户机和服务器间的数据传送量大大增加

**存储过程的优点**：

| 优点 | 说明 |
|------|------|
| **性能** | 在服务器上运行，服务器通常性能更强；数据库信息已物理地在同一系统中准备好，不需要等待记录通过网络传递 |
| **客户/服务器开发益处** | 客户方和服务器方开发任务分离，减少项目完成时间；服务器方组件可在客户应用程序间重复使用 |
| **安全性** | 用户可被授予执行存储过程的许可权，即使他在引用表或视图上没有许可权 |
| **编译优化** | 第一次运行时被编译并存储在数据库系统表中；编译时优化选择访问表信息的最佳路径（考虑数据实际形式、索引可用性、表负载等因素） |

### 10.2 创建存储过程

```sql
CREATE PROC [EDURE] 存储过程名 [;number]
[@参数名 数据类型] [=default] [OUTPUT] [, ...n]
[WITH {RECOMPILE, ENCRYPTION}]
AS sql_statement
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `;number` | 可选的整数，用来对同名的过程分组，以便用一条DROP PROCEDURE语句将同组过程一起删除 |
| `@参数名` | 每个过程的参数仅用于该过程本身。默认参数只能代替常量。最多**2,100个参数** |
| `default` | 参数的默认值（必须是常量或NULL）。有默认值时不必指定该参数即可执行 |
| `OUTPUT` | 表明参数是返回参数，值可以返回给EXEC[UTE] |
| `RECOMPILE` | SQL Server不会将计划放入缓存，运行时重新编译 |
| `ENCRYPTION` | SQL Server加密syscomments表中包含CREATE PROCEDURE文本的条目 |

### 10.3 执行存储过程

```sql
EXEC [UTE]
{ [@return_status =] { 存储过程名 [;number] | @procedure_name_var }
  [ [@参数名 =] { value | @variable [OUTPUT] | [DEFAULT] } ] }
```

- `@return_status`：可选的整型变量，保存返回状态（必须提前声明）
- `OUTPUT`：存储过程必须返回一个参数，值必须作为变量传递

### 10.4 删除存储过程

```sql
DROP PROCEDURE { procedure } [, ...n]
```

### 10.5 存储过程示例

**示例1——计算平均成绩**：
```sql
CREATE PROCEDURE prc_tot_score
    @grade int,
    @course_id string,
    @avg_score int OUTPUT
AS
SELECT @avg_score = AVG(score)
FROM st_score
WHERE Left(st_id, 4) = @grade AND course_id = @course_id

-- 执行
DECLARE @tot_amt int
EXECUTE prc_tot_score 2001, '0101', @tot_amt OUTPUT
SELECT @tot_amt
```

**示例2——检验用户是否存在**：
```sql
CREATE PROCEDURE usercheck
    @infullname varchar(50),
    @inpassword varchar(50),
    @outcheck char(3) OUTPUT
AS
IF EXISTS (SELECT * FROM userinfo
           WHERE fullname = @infullname AND password = @inpassword)
    SELECT @outcheck = 'yes'
ELSE
    SELECT @outcheck = 'no'
```

**示例3——带默认值的多表连接存储过程**：
```sql
CREATE PROCEDURE au_info2
    @lastname varchar(30) = 'D%',
    @firstname varchar(18) = '%'
AS
SELECT au_lname, au_fname, title, pub_name
FROM authors a INNER JOIN titleauthor ta ON a.au_id = ta.au_id
    INNER JOIN titles t ON t.title_id = ta.title_id
    INNER JOIN publishers p ON t.pub_id = p.pub_id
WHERE au_fname LIKE @firstname AND au_lname LIKE @lastname
GO

-- 多种执行方式
EXECUTE au_info2
EXECUTE au_info2 'Wh%'
EXECUTE au_info2 @firstname = 'A%'
EXECUTE au_info2 'Hunter', 'Sheryl'
EXECUTE au_info2 'H%', 'S%'
```

---

## 十一、零基础补充：SQL 入门全景图

### 11.1 数据库、表、行、列

可以把关系数据库先想象成很多张表：

| 数据库概念 | 类比 | 例子 |
|------------|------|------|
| 数据库 | 一个 Excel 文件夹 | 学校管理系统数据库 |
| 表 | 一张 Excel 表 | Students |
| 行/记录/元组 | 表中的一条数据 | 一个学生 |
| 列/字段/属性 | 表中的一个数据项 | 学号、姓名、生日 |
| 主键 | 唯一标识一行的列 | 学号 |

### 11.2 SQL 各类命令再整理

| 分类 | 全称 | 作用 | 常见命令 |
|------|------|------|----------|
| DDL | Data Definition Language | 定义结构 | `CREATE`、`ALTER`、`DROP` |
| DML | Data Manipulation Language | 修改数据 | `INSERT`、`UPDATE`、`DELETE` |
| DQL | Data Query Language | 查询数据 | `SELECT` |
| DCL | Data Control Language | 权限控制 | `GRANT`、`REVOKE` |
| TCL | Transaction Control Language | 事务控制 | `COMMIT`、`ROLLBACK` |

### 11.3 SELECT 的执行理解

虽然 SQL 写法通常从 `SELECT` 开始，但理解时可以按下面顺序：

```text
FROM 找表
    ↓
WHERE 筛选行
    ↓
GROUP BY 分组
    ↓
HAVING 筛选组
    ↓
SELECT 选择列/计算表达式
    ↓
ORDER BY 排序
```

### 11.4 JOIN 入门说明

连接查询用于把多张表按相关字段拼起来。

```sql
SELECT s.name, d.dept_name
FROM Students s
JOIN Departments d ON s.dept_id = d.id;
```

| JOIN 类型 | 含义 |
|-----------|------|
| `INNER JOIN` | 只保留两边都匹配的行 |
| `LEFT JOIN` | 保留左表所有行，右表没有则补 NULL |
| `RIGHT JOIN` | 保留右表所有行，左表没有则补 NULL |

### 11.5 存储过程参数细节补充

创建存储过程的通用形式：

```sql
CREATE PROCEDURE 存储过程名
    @参数名 数据类型 = 默认值 OUTPUT
AS
    SQL语句
```

补充 PDF 中容易漏掉的参数细节：

| 细节 | 说明 |
|------|------|
| 参数作用域 | 每个存储过程的参数只在该过程内部有效 |
| 参数用途限制 | 默认情况下参数通常代替常量，不能直接代替表名、列名等数据库对象名 |
| 默认值 | 如果参数定义了默认值，执行时可以不传这个参数 |
| `OUTPUT` | 表明参数可以把值返回给调用者 |
| 参数数量 | SQL Server 存储过程最多可以有 2100 个参数 |
| `RECOMPILE` | 运行时重新编译，不把执行计划放入缓存 |
| `ENCRYPTION` | 加密系统表中保存的存储过程定义文本 |
| `RAISERROR` | 在存储过程中返回用户自定义错误信息，并可设置错误状态 |

`RAISERROR` 示例：

```sql
RAISERROR('用户不存在', 16, 1)
```

含义：抛出一条错误消息，错误严重级别为 16，状态码为 1。

### 11.6 初学者写 SQL 的检查清单

1. `SELECT` 是否只查需要的列，而不是总写 `*`？
2. `WHERE` 条件是否避免误更新/误删除大量数据？
3. `JOIN` 条件是否写在正确字段上？
4. 建表时是否有主键？
5. 外键、唯一约束、检查约束是否符合业务规则？
6. 字符串和日期是否使用正确格式？
7. 多条相关修改是否需要事务？

## 自动查漏补充

- 关系模式中，如果多个属性名带下划线，表示这些属性的集合共同构成键码。
- 每个表只能有一个簇索引，但可以建立多个非簇索引。
- DCL 数据控制命令用于保证数据存取安全性，例如口令、权限授予和权限回收。
- 标识符不能是保留字的大写或小写形式，也不允许嵌入空格或其他特殊字符。
- 日期分隔符可使用斜杠 `/`、连字符 `-` 或句号 `.`，但实际项目中应统一日期格式。
- `LIKE` 中的 `[^]` 表示匹配不处于指定范围内、或不属于方括号指定集合中的任意字符。
- `SPACE(integer_expression)` 返回由指定数量空格组成的字符串。
- 正在使用的数据库通常不能直接删除，需要先切换到其他数据库或断开连接。
- 外部键定义要求被引用表中的对应列通常必须是主键或唯一键。
- `UNION` 会把多个查询组成最终结果集，参与合并的查询列数和兼容类型需要一致。
- 客户/服务器方式下，如果每个请求都以单个 SQL 语句发送给服务器，会增加网络传输和服务器解释优化负担。
- 存储过程可减少客户端与服务器之间的传输量，并利用服务器端编译优化提高执行速度。
- 存储过程参数只在过程内部有效；默认情况下参数通常不能直接代替表名、列名等数据库对象名。
- 执行存储过程时，调用者必须为没有默认值的参数提供值；带默认值的参数可以省略。
- `AS` 指定存储过程真正要执行的 SQL 操作。
- 存储过程中可以使用 `RAISERROR` 返回用户自定义错误信息、设置错误状态并记录错误。

## PDF逐页知识点补全索引

这一节按原 PDF 页码补全知识点，用来兜底检查前文是否遗漏。零基础学习时，可以先读前文讲解，再用这里逐页核对。

### 第 1 页：SQL
- 关系数据库回顾
- 数据查询语言
- T-SQL基本知识
- Select
- 发 展 命名规则
- 存储过程
- 数据类型 基本运算
- 触发器

### 第 2 页：数据库系统的构成
- 最终用户
- 应用系统
- 应用开发工具
- 应用程序员
- DBMS
- 操作系统
- 数据库管理员
- DBA

### 第 3 页：关系数据库简介
- 常见的RDBMS有：DB2, Oracle, MS SQL Server等。
- 关系数据库中常见的对象：
- 表(关系)：
- 【例】下表为Students表
- 字段
- 属性
- code myname birthday score
- 200101184022 王涛 1983/3/9 84

### 第 4 页：关系数据库
- 关系数据库中常见的对象：
- 表(关系)
- 索引： 为 表建立的 一种实现 快速查询 的工具 。 可分为簇 索
- 引(聚集索引)和非簇索引(非聚集索引) 。
- 簇索引是行的物理顺序和行的索引顺序相同的索引。
- 使用簇索引可以使UPDATE和SELECT操作大大加速。
- 每个表只能有一个簇索引。
- 定义簇索引键时使用的列越少越好。

### 第 5 页：关系数据库
- 关系数据库中常见的对象：
- 表(关系)
- 索引
- 存储过程：多个SQL语句的有机的集合。
- 触发器 ： 一种特殊 的存储过 程 ，当满 足一定的 条件时 ， 会
- 触发它执行。多用来保证表中数据的一致性。
- 视图： 可 以看成是 虚拟表或 存储查询 。视图不 作为独特 的
- 对象存储，数据库内存储的是SELECT语句。

### 第 6 页：的发展
- SQL
- SQL：结构化查询语言。
- 1974年由CHAMBERLIN和BOYEE提出，叫SEQUEL(A
- Structured English Query Language)，IBM公司对其进行
- 了修改，并用于其SYSTEM R关系数据库系统中；
- 1976年推出了第二版本SEQUEL/S；
- 1980年更名为SQL。
- SQL发展成了RDBMS的标准接口，被各RDBMS支持。

### 第 7 页：命令分类
- SQL
- 标准的SQL命令包括下面几类：
- 数据定义命令DDL：包括创建、修改、删除数据库、表、
- 索引、视图等，如CREATE、ALTER、DROP……。
- 数据修改命令DML：包括对数据的插入、删除和修改，如
- INSERT、DELEIE、UPDATE……。
- 数据查询 命令 DQL：即SELECT，可以 实现选择 、投影、
- 连接等关系操作。

### 第 8 页：运作模式
- SQL
- 三级模式结构：
- 视图1 视图2 外模式
- 表1 表2 表3 表4 模式
- 存储文件1 存储文件2 内模式

### 第 9 页：、命名规则
- 必须以字母a-z 和 A-Z、下划线 (_)、at 符号 (@) 或者数字
- 符号 (#)开头。
- 后续字符可以是：字母、十进制数字、@、#、美元符号 ($)
- 或下划线。
- 在 SQL Server 中
- @开始的标识符表示局部变量或参数。
- 以#开始的标识符表示临时表或过程。
- 以双数字符号 (# #) 开始的标识符表示全局临时对象。

### 第 10 页：变量的声明和赋值
- 变量的声明：DECLARE @local_variable data_type
- 变量在声明后均初始化为 NULL。
- 给变量赋值：SET @local_variable=
- 或 SELECT @local_variable=
- 【例】
- DECLARE @find varchar(30)
- SET @find = 'Ring%'
- SELECT au_lname, au_fname, phone FROM authors

### 第 11 页：、基本数据类型
- 整数 int 从 -231 到 231- 1 的整数。
- 比特 bit 1 或 0 的整数。
- 近似数字
- float 从 -1.79E + 308 到 1.79E + 308 的浮点精度数字。
- real 从 -3.40E + 38 到 3.40E + 38 的浮点精度数字。
- 字符串
- char(n) 固定长度的非 Unicode字符数据，最长 8,000 个字符。
- varchar(n) 可变长度的非 Unicode字符数据，最长 8,000 个字

### 第 12 页：基本数据类型
- 日期
- datetime 从 1753 年 1 月 1 日到 9999 年 12 月 31 日的日期
- 和时间数据，精确到百分之三秒(或 3.33 毫秒)。
- SQL Server 可以识别以下格式的日期和时间：
- 字母日期格式:
- 【例】 'April 15, 1998'
- 数字日期格式: 数字 分隔符 数字 分隔符 数字
- 数字的顺序一般为mdy。

### 第 13 页：、基本运算
- 1+, 2逻辑运算符, 3注释
- 1、+(字符串串联) 将两个字符串串联到一个表达式中。
- 语法 expression + expression
- 参数 image、ntext 或 text 除外的字符和二进制数据类型。
- 两个表达式都必须具有相同的数据类型，或者其中的一个表
- 达式必须能够隐式地转换为另一种数据类型。有时必须使用
- 字符数据的显式转换 (通过函数CONVERT或 CAST) 。
- 【例】 SELECT (au_lname + ', ' + au_fname) AS Name

### 第 14 页：基本运算
- 4BETWEEN, 5IN, 6LIKE
- 4、BETWEEN 指定测试范围。
- 语法 test_expression [ NOT ] BETWEEN begin_expression
- AND end_expression
- 【例】 WHERE ypayment NOT BETWEEN 4095 AND 12000
- 5、IN 确定给定的值是否与子查询或列表中的值相匹配。
- 语法 test_expression [ NOT ] IN (subquery| expression[ ,...n])
- 【例】 WHERE state IN ('CA', 'IN', 'MD')

### 第 15 页：基本运算
- 7通配符
- 7、通配符
- %匹配包含零个或多个字符的任意字符串。
- [ ]匹配指定范围内或者属于方括号所指定的集合中的任意
- 单个字符。
- 【例】 WHERE au_lname LIKE '[A-C]arsen'
- WHERE au_lname LIKE '[ABC]arsen'
- 【例】 WHERE au_lname LIKE '50%'

### 第 16 页：、常用函数
- 1COUNT
- 1、COUNT 返回组中项目的数量。
- 语法 COUNT( { [ ALL | DISTINCT ] expression | * } )
- 参数
- ALL 返回非空值的数量。缺省为ALL 。
- DISTINCT 指定 COUNT 返回唯一非空值的数量。
- expression 一个表达式(一般为属性名)，其数据类型不能是
- text、image 或 ntext。不允许使用聚合函数和子查询。

### 第 17 页：常用函数
- 2SUM, 3AVG
- 2、SUM 返回表达式中值的和。SUM 只能用于数字列。空
- 值将被忽略。
- 语法 SUM( [ ALL | DISTINCT ] expression )
- 参数
- ALL 对所有的值进行聚合函数运算。缺省为ALL。
- DISTINCT 指定 SUM 返回唯一值的和。
- expression是常量、列或函数(bit数据类型的除外) 。

### 第 18 页：常用函数
- 4MAX, 5MIN
- 4、MAX 返回表达式的最大值。
- 语法 MAX( [ ALL | DISTINCT ] expression )
- MAX 可用于数字列、字符列和 datetime 列，但不能用于
- bit 列。
- 【例】 SELECT MAX(age) FROM students
- 5、MIN 返回表达式的最小值。
- 语法 MIN( [ ALL | DISTINCT ] expression )

### 第 19 页：常用函数
- 6字符处理
- 6、 常用的字符处理函数
- LOWER(char_expression )将大写转换为小写字符。
- UPPER(char_expression )将小写转换为大写字符。
- RIGHT(char_expre, integer_expre)返回从右边开始指定个数
- 的字符。LEFT类似。
- 【例】 SELECT '入学年份'=LEFT(st_id,4) FROM students
- SUBSTRING(expression,start,length )返回字符串的一部分。

### 第 20 页：常用函数
- 7日期处理, 8ISNUMERIC, 9ISDATE
- 7、 常用的日期处理函数
- MONTH( date ) 返回代表指定日期月份的整数。
- 【例】 SELECT "Month Number" = MONTH('03/12/2003')
- SQL Server 将 0 解释为 '01/01/1900'。
- 【例】 SELECT MONTH(0), DAY(0), YEAR(0)
- GETDATE( )返回当前系统日期和时间。
- 【例】 SELECT GETDATE()

### 第 21 页：数据库的建立、删除
- 1、建立
- CREATE DATABASE UserTest --数据库名
- ON (NAME=UserTest_Data, --数据设备名
- FILENAME='D:\TEST_Data.mdf', --数据文件
- 默认为
- SIZE=1, --初始大小为1M
- MB
- MAXSIZE=500, --最大只能到500M

### 第 22 页：数据库的使用
- 3、使用
- USE UserTest
- 则以下的对表进行操作的SQL语句均在UserTest 中。
- 如下语句能够正确执行吗？
- CREATE DATABASE UserTest
- 出错，因为一批SQL语句中间没有GO的话，会认为一起提
- 交。改正：
- GO

### 第 23 页：表的建立
- 1、建立表：CREATE TABLE 表名(
- 列名1 数据类型1,列名2 数据类型2,主键说明,外部键说明)
- 基本构件：关键字、表名、列名、数据类型。
- 表名在整个数据库中要唯一。
- 主键的定义：
- CONSTRAINT 主键约束的名字 PRIMARY KEY
- [CLUSTERED | NONCLUSTERED] (作为主键的列名)
- 主键不能定义在可以为空的列上。

### 第 24 页：表的建立
- 1、建立表
- CREATE TABLE Students(
- 学生
- st_id integer NOT Null UNIQUE,
- st_name varchar(50) NOT Null,
- 属于
- pwd varchar(20) Null DEFAULT '0000',
- birthday datetime Null

### 第 25 页：表的建立
- CREATE TABLE st_Dept(
- deptno integer NOT Null
- CONSTRAINT pk_st_Dept PRIMARY KEY,
- deptname varchar(50) NOT Null
- CONSTRAINT upper_name
- CHECK(deptname=UPPER(deptname)),
- fdtime datetime DEFAULT GETDATE()

### 第 26 页：表的修改
- 2、修改表
- ALTER TABLE table
- [ ALTER COLUMN 列名 数据类型等属性 ]
- | ADD [列的定义|约束的定义]
- | DROP {[CONSTRAINT] 约束名|COLUMN 列名 }
- |{CHECK | NOCHECK} CONSTRAINT {ALL|约束名}
- |{ENABLE | DISABLE} TRIGGER {ALL|触发器名}

### 第 27 页：表的修改 例
- 【例】 不检查出生年份是否>1985，则
- ALTER TABLE Students NOCHECK CONSTRAINT cc_birth
- 【例】
- ALTER TABLE Students ALTER COLUMN st_name integer
- Null
- 不能改已经对它建立了约束的列的属性，包括主键、外部键、
- UNIQUE等。
- 【例】 ALTER TABLE Students ADD CONSTRAINT

### 第 28 页：表的删除
- 3、删除表
- DROP TABLE 表名
- 【例】 DROP TABLE Students
- 不能删除正由一个 FOREIGN KEY 约束引用的表。必须
- 先删除引用的 FOREIGN KEY 约束或引用的表。
- GO
- DROP TABLE st_Dept

### 第 29 页：数据修改语言
- INSERT
- 1、 INSERT将新行添加到表或视图。
- INSERT [ INTO]{ 表名 |视图名} { [ ( 列名列表 ) ]
- { VALUES({DEFAULT|NULL|表达式})
- | derived_table}
- DEFAULT强制该列值为为该列定义的默认值。
- 如果对于某列并不存在默认值，并且该列允许 NULL，则
- 插入 NULL。

### 第 30 页：INSERT
- Students(st_id,st_name,pwd,birthday,st_dept)
- st_Dept(deptno,deptname,fdtime)
- 【例】
- INSERT st_Dept VALUES(184, 'AUTOMATIC CONTROL',
- DEFAULT)
- INSERT Students VALUES(2000184013, '王菲', DEFAULT,
- '1976-01-01', 184)
- 上面两句之间用不用加上GO语句？

### 第 31 页：INSERT
- INSERT语句注意事项：
- 主键列不能为空和重复。
- 不允许为空的列必须给予赋值。
- 赋的值要满足约束条件。

### 第 32 页：数据查询语言
- SELECT
- 基本语法：
- SELECT select_list --要查询的内容
- [ INTO new_table ] --将结果存放到一个新表
- FROM table_source --指定所使用的表、视图
- [ WHERE search_condition ] --查询的条件
- [ GROUP BY group_by_expression ] --分组
- [ ORDER BY order_expression [ ASC | DESC ] ] --排序

### 第 33 页：子句
- SELECT
- SELECT[ALL|DISTINCT][TOP n [PERCENT]]
- <select_list>
- 缺省为ALL。空值认为相等。
- TOP n [PERCENT]只从查询结果中输出前n行或前n%行。
- 带 PERCENT 时，n 必须是介于 0 和 100 之间的整数。
- 如果查询包含 ORDER BY 子句，将输出由 ORDER BY 子
- 句排序的前 n 行(或前百分之 n 行)。

### 第 34 页：子句
- AS
- AS 子句可用于为结果集列指定不同的名称或别名。
- 【例】 SELECT EmpSSN AS "Employee Social Security
- Number" FROM EmpTable
- 【例】 st_score(st_id,Eng_score,Math_score,AC_score)
- 查询各个年级的英语平均成绩。
- SELECT Left(st_id,4) AS grade# ,
- Sum(Eng_score)/Count(Eng_score) AS Avg_Eng

### 第 35 页：子句
- UNION
- 可以在多个查询之间使用 UNION 运算符，以将查询的结
- 果组合成单个结果集，
- 该结果集显示的列名是前一个SELECT的列名。
- 该结果集包含联合查询中的所有查询的全部行。
- 如果UNION连接的两个查询结果列不一致，则会将后一个
- 查询结果转换成前一个查询结果的列的数据类型。
- 如果两表列数不同，则不能用UNION。

### 第 36 页：示例
- SELECT
- Customers(Cust_Name,Country,City,Phone)
- SouthAmericanCustomers (Cust_Name,Country,City,Phone)
- 【例】
- SELECT Cust_Name,Country,City,Phone
- INTO #CustomerResults
- FROM Customers
- WHERE Country IN ('USA','Canada') --北美记录

### 第 37 页：示例
- SELECT
- st_score(st_id,Eng_score,Math_score,AC_score)
- students(st_id,st_name,pwd,birthday,st_dept)
- 【例】 查询最高英语成绩的学生学号和英语成绩。
- SELECT st_id,Eng_score
- FROM st_score
- WHERE Eng_score = (SELECT
- Max(Eng_score) FROM st_score )

### 第 38 页：示例
- SELECT
- titles(title_id,ytd_sales )
- titleauthor(title_id,au_id )
- authors(au_id,au_fname,au_lname )
- 【例】 SELECT ytd_sales AS Sales,
- authors.au_fname + ' ' + authors.au_lname AS Author
- INTO #Tmp_count
- FROM titles INNER JOIN titleauthor ON titles.title_id =

### 第 39 页：示例
- SELECT
- st_score(st_id,Eng_score,Math_score,AC_score)
- students(st_id,st_name,pwd,birthday,st_dept)
- 【例】 查询英语成绩为100的学生的名字并存放在临时表
- #highscore中。
- SELECT DISTINCT st_name INTO #highscore
- FROM students
- WHERE 100 IN (SELECT Eng_score FROM st_score

### 第 40 页：示例
- SELECT
- customers(cust_name,address,postcode,acc_id)
- accouts(acc_id,type,balance,fdtime)
- 【例】 查询存款类型存在check类型的银行客户名称。
- SELECT DISTINCT cust_name
- FROM customers
- WHERE EXISTS (SELECT * FROM accouts WHERE
- acc_id = customers.acc_id AND type = 'check')

### 第 41 页：步骤总结
- SELECT
- I. 分析所要查询的内容和条件分布在哪些表中
- II. 在SELECT子句中写要查询的内容
- III. 在FROM子句中写所涉及的表
- IV. 在WHERE子句中写所有的条件
- 注意：利用“表名.”引用该表的列名。
- 若要分组查询则加入GROUP BY子句。
- 若要排序则利用ORDER BY子句。

### 第 42 页：示例
- SELECT
- st_score(st_id,Eng_score,Math_score,AC_score)
- st_highscore(st_id,score,course_id)
- courses(course_id,course_name,type,percents,teacher_id)
- 【例】查询各科成绩最高的学生的学号并将相关信息保存在
- st_highscore表中。
- INSERT st_highscore (st_id,score,course_id)
- SELECT a.st_id,a.Eng_score,b.course_id

### 第 43 页：示例
- SELECT
- 三表联合查询
- st_highscore(st_id,score,course_id)
- students(st_id,st_name,pwd,birthday,st_dept)
- courses(course_id,course_name,type,percents,teacher_id)
- 【例】查询在‘import’类型的课程中考过最高分的学生名字。
- SELECT st_name
- FROM students a, st_highscore b, courses c

### 第 44 页：为什么用存储过程
- 在利用数据库软件开发工具开发应用程序时，当客户端与数
- 据库服务器通信时，会牵涉到更多因素。
- 首先客户端数据通过多层网络软件；其次，在服务器解释消
- 息前也必须通过多层网络软件；服务器接受请求后，还必须
- 对SQL语句进行解释、优化、执行；而执行结果在返回客户
- 端的过程中同样需要两端的多层网络软件。
- 而且，客户端应用程序向服务器请求数据时，若返回结果集
- 过大，也同样要花费过多的时间。

### 第 45 页：为什么用存储过程
- 可以将多个SQL语句集合在一起形成存储过程，使用存储过
- 程有如下好处：
- 性能：因为存储过程是在服务器上运行的，而服务器通常
- 是一种功能更加强大的机器，它的执行时间要比在工作站中
- 的执行时间短。
- 另外，由于数据库信息已经物理地在同一系统中准备好，因
- 此就不必等待记录通过网络传递进行处理。相反，存储过程
- 具有对数据库的立即地、准备好地访问，这使得信息处理极

### 第 46 页：为什么用存储过程
- 安全性：存储过程不仅可以改善效能，而且可以作为安全
- 机制，因为用户可以被授予执行一个存储过程的许可权，即
- 使他在存储过程中引用的表或视图上没有许可权。
- 存储过程在第一次运行时被编译，并存储在当前数据库的
- 系统表中。当存储过程被编译时，它们被优化以选择访问表
- 信息的最佳路径，这一优化要考虑到表中数据的实际形式、
- 索引是否可用、表负载等一些因素。这些编译后的存储过程
- 可大大加强系统的性能。

### 第 47 页：存储过程的建立
- CREATE PROC[EDURE]存储过程名 [;number]
- [{@参数名 数据类型} [=default] [OUTPUT]] [,...n]
- [WITH{RECOMPILE，ENCRYPTION}]
- AS sql_statement
- 参数含义：
- number是可选的整数，用来对同名的过程分组，以便用一条
- DROP PROCEDURE 语句即可将同组的过程一起除去。
- 【例】存储过程可以命名为 orderproc;1、orderproc;2 等。

### 第 48 页：存储过程的建立
- default参数的默认值。如果定义了默认值，不必指定该参
- 数的值即可执行过程。默认值必须是常量或 NULL。
- OUTPUT表明参数是返回参数。该选项的值可以返回给
- EXEC[UTE]。
- RECOMPILE 表明 SQL Server 不会将该过程的计划放入
- 缓存，该过程将在运行时重新编译。
- ENCRYPTION 表示 SQL Server 加密 syscomments 表中
- 包含 CREATE PROCEDURE 语句文本的条目。

### 第 49 页：存储过程的执行
- EXEC[UTE]{[@return_status = ]{存储过程名
- [;number]|@procedure_name_var}[[@存储过程的参数
- =]{value|@variable[OUTPUT]|[DEFAULT]]
- @return_status可选的整型变量，保存存储过程的返回状
- 态。该变量必须提前被声明。
- @procedure_name_var局部定义变量名，代表已存在的存
- 储过程名称。
- OUTPUT指定存储过程必须返回一个参数。该存储过程的

### 第 50 页：存储过程的删除
- DROP PROCEDURE
- 从当前数据库中删除一个或多个存储过程或过程组。
- DROP PROCEDURE { procedure } [ ,...n ]
- 参数
- procedure是要删除的存储过程或存储过程组的名称。

### 第 51 页：存储过程示例
- st_score(st_id,course_id,score)
- 【例】 CREATE PROCEDURE prc_tot_score @grade int,
- @course_id string, @avg_score int OUTPUT
- AS
- SELECT @avg_score=AVG(score)
- FROM st_score
- WHERE Left(st_id,4)=@grade and course_id=@course_id
- 执行：假 设0101为 英语课程 代码 ，要 查找2001级英语课 程

### 第 52 页：存储过程示例
- 用户信息表userinfo(id int(4) not null,
- fullname varchar(50) not null,
- password varchar(20) not null,
- nikename varchar(50) not null)
- 编写存储过程检验用户是否存在。
- 【 例 】 CREATE PROCEDURE usercheck @infullname
- varchar(50), @inpassword varchar(50), @outcheck char(3)
- OUTPUT

### 第 53 页：存储过程示例
- 【例】
- CREATE PROCEDURE titles_sum @@TITLE
- varchar(40)='%', @@SUM money OUTPUT
- AS
- SELECT 'Title Name' = title
- FROM titles WHERE title LIKE @@TITLE
- SELECT @@SUM = SUM(price)
- GO

### 第 54 页：存储过程示例
- CREATE PROCEDURE au_info2 @lastname varchar(30) =
- 'D%', @firstname varchar(18) = '%' AS
- SELECT au_lname, au_fname, title, pub_name
- FROM authors a INNER JOIN titleauthor ta ON a.au_id =
- ta.au_id INNER JOIN titles t ON t.title_id = ta.title_id
- INNER JOIN publishers p ON t.pub_id = p.pub_id
- WHERE au_fname LIKE @firstname AND au_lname LIKE
- @lastname

## 十二、本章小结

本章系统介绍了SQL（以T-SQL/MS SQL Server为背景），涵盖以下核心知识点：

1. **关系数据库基础**：数据库系统架构（用户→应用→DBMS→OS）；常见RDBMS（DB2/Oracle/SQL Server）；数据库对象（表、索引、视图、存储过程、触发器）

2. **T-SQL命名规则**：@开头表示局部变量/参数，#开头表示临时表/过程，##开头为全局临时对象，@@为系统函数前缀

3. **数据类型**：int/bit/float/real/char(n)/varchar(n)/nchar/nvarchar/datetime；三种日期格式（字母/数字分隔/未分隔字符串）

4. **基本运算**：字符串串联(+)、逻辑运算符(=,>,<,>=,<=,<>,!=,!<,!>)、BETWEEN、IN、LIKE（含%,_,[ ],[^]通配符）

5. **常用函数**：聚合函数（COUNT/SUM/AVG/MAX/MIN）、字符处理（LOWER/UPPER/LEFT/RIGHT/SUBSTRING/LEN/REPLACE/SPACE）、日期处理（MONTH/DAY/YEAR/GETDATE）、类型判断（ISNUMERIC/ISDATE）

6. **DDL**：
   - 数据库：CREATE/DROP DATABASE、USE（需GO分隔）
   - 表：CREATE TABLE（含CONSTRAINT主键/外部键/UNIQUE/CHECK/DEFAULT）、ALTER TABLE（ADD/DROP/ALTER COLUMN/NOCHECK）、DROP TABLE（注意外键依赖）

7. **DML**：INSERT（VALUE/DEFAULT/SELECT子查询，注意主键/非空/约束/外部键限制）

8. **DQL（SELECT）**：完整语法（SELECT/FROM/WHERE/GROUP BY/ORDER BY/INTO）；DISTINCT/TOP/AS/UNION/JOIN/子查询（标量/IN/EXISTS）/三表联合查询；七个步骤方法论

9. **存储过程**：性能优势（服务器端编译优化执行）、安全机制（独立于表权限）、开发分离；CREATE PROCEDURE（参数/OUTPUT/RECOMPILE/ENCRYPTION）、EXECUTE执行、DROP PROCEDURE删除

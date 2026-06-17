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

## 十一、本章小结

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

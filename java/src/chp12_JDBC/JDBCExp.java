/*
 * ============================================================
 * 【功能说明】
 * 本程序是一个综合性的 JDBC 示例，演示了 Java 中三种 SQL
 * 语句执行方式的使用方法，数据库为 SQL Server：
 *
 * 1. Statement（普通语句）：
 *    - 执行 DDL 语句创建表、创建存储过程
 *    - 执行 DML 语句（INSERT、DROP 等）
 *
 * 2. PreparedStatement（预编译语句）：
 *    - 使用占位符（?）构建参数化 INSERT
 *    - 批量执行（addBatch / executeBatch）提高效率
 *
 * 3. CallableStatement（可调用语句）：
 *    - 调用 SQL Server 存储过程（proc_student_insert）
 *    - 批量执行存储过程调用
 *
 * 程序还包含 selectAll() 方法遍历查询 Student 表的所有记录
 * 并通过 List<Object[]> 集合存储查询结果。
 *
 * 【知识点】
 * 1. JDBC 三种执行语句：
 *    - Statement：执行静态 SQL
 *    - PreparedStatement：预编译参数化 SQL，防 SQL 注入
 *    - CallableStatement：调用数据库存储过程
 * 2. 批处理机制：addBatch() 积累多条 SQL，
 *    executeBatch() 一次性提交到数据库执行
 * 3. clearBatch() 清空批处理缓冲区
 * 4. DDL（数据定义语言）与 DML（数据操作语言）的区别
 * 5. SQL Server JDBC 驱动：com.microsoft.sqlserver.jdbc.SQLServerDriver
 * 6. static 静态代码块：类加载时自动执行，适合驱动注册
 * 7. ResultSet.getObject()：按 Object 类型通用获取字段值
 * 8. 存储过程的创建与调用（SQL Server T-SQL 语法）
 * 9. 异常处理：try-catch 与 throws 结合使用
 * 10. List<Object[]> 存储结构化查询结果
 * ============================================================
 */
package chp12_JDBC;                                        // 声明包路径，属于第12章JDBC综合实验

import java.sql.*;                                          // 导入java.sql包下的所有类和接口（Connection、Statement等）
import java.util.ArrayList;                                 // 导入ArrayList类，动态数组实现
import java.util.List;                                      // 导入List接口，集合框架的根接口之一

public class JDBCExp {                                     // 定义公开类JDBCExp
    // 数据库驱动类名常量：SQL Server JDBC驱动
    private static final String DRIVERCLASS = "com.microsoft.sqlserver.jdbc.SQLServerDriver"; // SQL Server JDBC驱动类的全限定名
    // 数据库连接URL：JDBC协议+SQL Server子协议+主机IP 127.0.0.1+端口1433+数据库名msdb
    private final String url = "jdbc:sqlserver://127.0.0.1:1433;DatabaseName=msdb";            // 连接本机SQL Server的msdb数据库
    private final String username = "sa";                   // SQL Server登录用户名（sa为系统管理员账户）
    private final String password = "";                     // SQL Server登录密码（此处为空字符串）
    private Connection conn;                                // 私有成员变量：数据库连接对象
    private Statement stmt;                                 // 私有成员变量：普通语句对象
    private PreparedStatement prpdStmt;                     // 私有成员变量：预编译语句对象
    private CallableStatement cablStmt;                     // 私有成员变量：可调用语句对象（用于调用存储过程）

    // 静态代码块：类加载时自动执行，用于注册数据库驱动
    static {                                                // 静态初始化块（类首次加载到JVM时执行一次）
        try {                                               // try块开始：加载数据库驱动
            Class.forName(DRIVERCLASS);                     // 通过反射加载SQL Server JDBC驱动类（自动注册驱动）
        } catch (ClassNotFoundException e) {                // 捕获驱动类未找到异常
            System.out.println("在加载数据库驱动时抛出异常，信息如下："); // 打印中文提示：驱动加载失败
            e.printStackTrace();                            // 打印详细的异常堆栈跟踪信息
        }                                                   // catch块结束
    }                                                       // 静态代码块结束

    // 使用 Statement 执行 SQL 更新操作
    public void useStatement(String sql) throws SQLException { // 方法：执行传入的SQL语句（DDL或DML），声明可能抛出SQLException
        stmt = conn.createStatement();                      // 从连接创建Statement对象
        stmt.executeUpdate(sql);                            // 执行SQL语句（INSERT/UPDATE/DELETE/CREATE/DROP等）
        stmt.close();                                       // 关闭Statement释放资源
    }                                                       // useStatement方法结束

    // 使用 PreparedStatement 执行批量插入
    public void UsePreparedStatement(int[] id, String[] names) throws SQLException { // 方法：批量插入学生记录，接收学号数组和姓名数组
        prpdStmt = conn.prepareStatement("INSERT INTO Student VALUES(?,?)"); // 预编译带占位符的INSERT语句（两个?：学号和姓名）
        prpdStmt.clearBatch();                              // 清空批处理缓冲区，确保没有残留的SQL命令
        for (int i = 0; i < id.length; i++) {              // 遍历所有学生记录
            prpdStmt.setInt(1, id[i]);                     // 为第1个占位符设置学号（int类型）
            prpdStmt.setString(2, names[i]);                // 为第2个占位符设置姓名（String类型）
            prpdStmt.addBatch();                            // 将当前参数化的SQL添加到批处理中
        }                                                   // for循环结束
        prpdStmt.executeBatch();                            // 批量执行所有累积的INSERT语句（一次数据库往返）
        prpdStmt.close();                                   // 关闭PreparedStatement释放资源
    }                                                       // UsePreparedStatement方法结束

    // 使用 CallableStatement 调用存储过程实现批量插入
    public void UseCallableStatement(int[] id, String[] names) throws SQLException { // 方法：调用存储过程批量插入，接收学号数组和姓名数组
        cablStmt = conn.prepareCall("{call proc_student_insert(?,?)}"); // 准备调用存储过程proc_student_insert，含两个参数占位符
        cablStmt.clearBatch();                              // 清空批处理缓冲区
        for (int i = 0; i < id.length; i++) {              // 遍历所有学生记录
            cablStmt.setInt(1, id[i]);                     // 为存储过程的第1个参数设置学号
            cablStmt.setString(2, names[i]);                // 为存储过程的第2个参数设置姓名
            cablStmt.addBatch();                            // 将当前存储过程调用添加到批处理中
        }                                                   // for循环结束
        cablStmt.executeBatch();                            // 批量执行所有存储过程调用
        cablStmt.close();                                   // 关闭CallableStatement释放资源
    }                                                       // UseCallableStatement方法结束

    // 查询Student表中的所有记录并打印
    public void selectAll() {                               // 方法：查询并输出Student表的所有记录
        List<Object[]> list = new ArrayList<Object[]>();    // 创建List集合，用于存储查询结果（每行为Object数组）
        try {                                               // try块开始：执行查询
            stmt = conn.createStatement();                  // 从连接创建Statement对象
            ResultSet rs = stmt.executeQuery("SELECT * FROM Student"); // 执行SELECT查询，获取Student表所有记录
            while (rs.next()) {                             // 循环遍历ResultSet结果集
                Object note[] = new Object[2];              // 创建长度为2的Object数组，存储一行中的两个字段
                for (int i = 0; i < note.length; i++) {    // 遍历当前行的每个字段
                    note[i] = rs.getObject(i + 1);         // 使用getObject通用方法获取字段值（列索引从1开始）
                }                                           // 内层for循环结束
                list.add(note);                             // 将当前行数组添加到List集合中
            }                                               // while循环结束
            stmt.close();                                   // 关闭Statement释放资源
        } catch (SQLException e) {                          // 捕获SQLException：查询过程中发生异常
            System.out.println("在查询记录时抛出异常，信息如下："); // 打印中文提示：查询异常
            e.printStackTrace();                            // 打印详细的异常堆栈跟踪信息
        }                                                   // catch块结束

        // 遍历集合并逐行打印查询结果
        for (int i = 0; i < list.size(); i++) {            // 遍历List集合
            System.out.println(list.get(i)[0].toString() + '\t' // 打印第1列（学号），以制表符分隔
                    + list.get(i)[1].toString());           // 打印第2列（姓名）
        }                                                   // for循环结束
    }                                                       // selectAll方法结束

    public static void main(String[] args) throws SQLException { // 程序入口点，声明向上抛出SQLException
        JDBCExp a = new JDBCExp();                          // 创建JDBCExp实例
        a.conn = DriverManager.getConnection(a.url, a.username, a.password); // 建立数据库连接（SQL Server）

        // 使用普通Statement创建数据表
        try {                                               // try块开始：尝试删除已存在的Student表
            a.useStatement("DROP TABLE Student");           // 执行DROP TABLE语句删除Student表
        } catch (SQLException e) {                          // 捕获异常（表不存在时抛出，忽略即可）
        }                                                   // catch块为空，表示表不存在时无需处理
        a.useStatement("CREATE TABLE Student(st_no int NOT Null PRIMARY KEY, st_name varchar(20) NOT Null)"); // 创建Student表：学号（int，非空，主键），姓名（varchar(20)，非空）

        // 使用PreparedStatement批量插入学生记录
        int[] id = {1, 2, 3};                               // 定义学号数组：1,2,3
        String[] name = {"张三", "李四", "王五"};            // 定义姓名数组：张三、李四、王五
        a.UsePreparedStatement(id, name);                   // 调用PreparedStatement方法批量插入3条记录

        // 创建存储过程，然后使用CallableStatement调用该存储过程插入数据
        try {                                               // try块开始：尝试删除已存在的存储过程
            a.useStatement("DROP PROCEDURE proc_student_insert"); // 执行DROP PROCEDURE删除存储过程
        } catch (SQLException e) {                          // 捕获异常（存储过程不存在时抛出，忽略即可）
        }                                                   // catch块为空
        // 创建名为proc_student_insert的存储过程，接收@id和@name两个参数
        a.useStatement("CREATE PROCEDURE proc_student_insert @id int,@name varchar(20) AS " +
                "INSERT INTO Student VALUES(@id,@name)");   // 存储过程体：向Student表插入一条记录
        int[] id2 = {4, 5};                                 // 定义学号数组：4,5
        String[] name2 = {"Amy", "Joan"};                   // 定义姓名数组：Amy, Joan
        a.UseCallableStatement(id2, name2);                 // 调用CallableStatement方法通过存储过程批量插入2条记录

        // 查询并打印Student表中所有记录
        a.selectAll();                                      // 调用selectAll方法显示所有记录（共5条）

        a.conn.close();                                     // 关闭数据库连接，释放资源
    }                                                       // main方法结束
}                                                           // 类定义结束

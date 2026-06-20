/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了使用 JDBC（Java Database Connectivity）进行
 * MySQL 数据库操作的基本流程。主要功能包括：
 * 1. 加载 MySQL JDBC 驱动（com.mysql.jdbc.Driver）
 * 2. 建立数据库连接（连接至 localhost 的 test 数据库）
 * 3. 使用 Statement 对象执行 SQL 的 INSERT 语句插入一条学生记录
 * 4. 使用 SELECT 语句查询所有学生记录并遍历 ResultSet 输出
 * 5. 使用条件查询（WHERE 子句）筛选数学成绩>=80的学生信息
 * 6. 按列索引和列名两种方式从 ResultSet 中获取字段值
 * 7. 关闭连接释放资源
 * 该示例展示了 JDBC 的典型使用步骤（加载驱动→建立连接→
 * 创建Statement→执行SQL→处理ResultSet→关闭资源）。
 *
 * 【知识点】
 * 1. JDBC 核心接口：Connection、Statement、ResultSet
 * 2. Class.forName() 动态加载数据库驱动
 * 3. DriverManager.getConnection() 获取数据库连接
 * 4. URL 格式：jdbc:mysql://主机名/数据库名
 * 5. executeUpdate() 执行 INSERT/UPDATE/DELETE 返回影响行数
 * 6. executeQuery() 执行 SELECT 返回 ResultSet 结果集
 * 7. ResultSet.next() 遍历结果集（指针移动）
 * 8. ResultSet.getString()/getInt() 获取字段值
 *    ——支持按列索引（从1开始）和列名两种方式
 * 9. SQLException：JDBC 操作的标准异常处理
 * 10. 资源释放：先关闭 Statement，再关闭 Connection
 * ============================================================
 */
package chp12_JDBC.exp12_1;                                // 声明包路径，属于第12章JDBC实验1

import java.sql.Connection;                                 // 导入Connection接口，表示数据库连接
import java.sql.DriverManager;                              // 导入DriverManager类，管理JDBC驱动和连接
import java.sql.ResultSet;                                  // 导入ResultSet接口，表示查询结果集
import java.sql.SQLException;                               // 导入SQLException类，JDBC操作的标准异常
import java.sql.Statement;                                  // 导入Statement接口，用于执行静态SQL语句

public class JdbcTest {                                    // 定义公开类JdbcTest
    public static void main(String args[]) {                // 程序入口点

        String url = "jdbc:mysql://localhost/test";         // 定义数据库URL：JDBC协议+MySQL子协议+主机+数据库名
        Connection con;                                     // 声明Connection引用，用于建立与数据库的连接
        String sql;                                         // 声明String变量，用于存储SQL语句
        Statement stmt;                                     // 声明Statement引用，用于执行SQL语句
        String num, name, sex;                              // 声明字符串变量：学号、姓名、性别
        int age, math, eng, spec;                           // 声明整型变量：年龄、数学成绩、英语成绩、专业成绩

        try {                                               // try块开始：加载数据库驱动
            Class.forName("com.mysql.jdbc.Driver");         // 通过反射加载MySQL JDBC驱动类（注册驱动）
        } catch (java.lang.ClassNotFoundException e) {      // 捕获类未找到异常（驱动JAR包未引入时抛出）
            System.err.print("ClassNotFoundException: ");   // 在标准错误流打印异常提示
            System.err.println(e.getMessage());             // 打印异常的详细信息
        }                                                   // catch块结束

        try {                                               // try块开始：建立连接并执行数据库操作
            con = DriverManager.getConnection(url, "root", "java"); // 使用URL、用户名root、密码java建立数据库连接
            stmt = con.createStatement();                   // 通过连接创建Statement对象，用于发送SQL到数据库

            // 向student表插入一条记录
            sql = "INSERT INTO STUDENT " +                  // 拼接INSERT INTO语句，表名为STUDENT
                    "VALUES('200108','王晓华','女',20,71,62,76)"; // VALUES指定要插入的各字段值：学号、姓名、性别、年龄、数学、英语、专业
            stmt.executeUpdate(sql);                        // 执行INSERT语句（executeUpdate返回受影响的记录行数）

            // 查询student表中的所有记录并获取结果集
            sql = " SELECT * FROM STUDENT";                 // 定义SQL查询语句：从STUDENT表中选择所有列和所有行
            ResultSet rs = stmt.executeQuery(sql);          // 执行查询，返回ResultSet结果集（包含查询到的所有行）
            System.out.println("学号        姓名        性别  年龄" +     // 打印结果集的列标题
                    "   高等数学  英语  专业课");                        // 标题各列：学号、姓名、性别、年龄、高等数学、英语、专业课
            while (rs.next()) {                             // 循环遍历ResultSet：next()移动游标到下一行，无更多行时返回false
                num = rs.getString(1);                      // 通过列索引（第1列）获取学号（String类型）
                name = rs.getString(2);                     // 通过列索引（第2列）获取姓名
                sex = rs.getString(3);                      // 通过列索引（第3列）获取性别
                age = rs.getInt(4);                         // 通过列索引（第4列）获取年龄（int类型）
                math = rs.getInt(5);                        // 通过列索引（第5列）获取高等数学成绩
                eng = rs.getInt("英语");                    // 通过列名"英语"获取英语成绩（列名方式获取）
                spec = rs.getInt("专业课");                 // 通过列名"专业课"获取专业成绩
                System.out.println(num + "    " + name + "	" + sex + "	" + age + "	" + math // 打印当前行的各字段值，以空格和制表符分隔
                        + "	" + eng + "	" + spec);       // 继续打印英语和专业课成绩
            }                                               // while循环结束

            // 查询高等数学成绩80分以上的学生信息
            rs = stmt.executeQuery("SELECT 学号,姓名,高等数学,英语,专业课 " + // 执行条件查询：只查询指定列（学号、姓名、高等数学、英语、专业课）
                    "FROM STUDENT  " +                      // 从STUDENT表查询
                    "WHERE 高等数学>=80");                  // WHERE子句：筛选高等数学成绩>=80的记录
            System.out.println();                           // 打印一个空行，作为分隔
            System.out.println("The students whose math mark is beyond 80 are:"); // 打印提示信息"数学成绩超过80分的学生："
            while (rs.next()) {                             // 循环遍历查询结果集
                num = rs.getString(1);                      // 通过列索引（第1列）获取学号
                name = rs.getString(2);                     // 通过列索引（第2列）获取姓名
                math = rs.getInt(3);                        // 通过列索引（第3列）获取高等数学成绩
                eng = rs.getInt("英语");                    // 通过列名"英语"获取英语成绩
                spec = rs.getInt("专业课");                 // 通过列名"专业课"获取专业成绩
                System.out.println("学号=" + num + "	" + "姓名=" + name + "	" + "高等数学=" + // 打印带标签的字段值
                        math + "    " + "英语=" + eng + "	" + "专业课=" + spec);             // 继续打印英语和专业课
            }                                               // while循环结束

            // 关闭连接，释放数据库资源
            stmt.close();                                   // 关闭Statement对象，释放数据库语句对象资源
            con.close();                                    // 关闭Connection连接，释放数据库连接资源
        } catch (SQLException ex) {                         // 捕获SQLException：所有数据库操作异常
            System.err.println("SQLException: " + ex.getMessage()); // 在标准错误流打印SQL异常信息
        }                                                   // catch块结束
    }                                                       // main方法结束
}                                                           // 类定义结束

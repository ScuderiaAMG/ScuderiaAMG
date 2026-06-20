/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了 JDBC 事务管理机制，包括：
 * 1. 使用 setAutoCommit(false) 关闭自动提交模式
 * 2. 手动提交事务（commit）
 * 3. 异常发生时回滚事务（rollback）
 * 程序对 COFFEES 表中的每条咖啡记录执行两个更新操作——
 * 更新 SALES（本周销量）和更新 TOTAL（累计总销量），
 * 这两个操作作为一个事务单元，要么全部成功（commit），
 * 要么全部失败（rollback），从而保证数据一致性。
 * 当循环中任一操作抛出异常时，catch 块检测到连接不为空
 * 则执行 rollback() 撤销所有已执行的更新。
 *
 * 【知识点】
 * 1. 事务的 ACID 特性：原子性（Atomicity）、一致性（Consistency）、
 *    隔离性（Isolation）、持久性（Durability）
 * 2. Connection.setAutoCommit(false)：关闭自动提交，
 *    开启手动事务管理模式
 * 3. Connection.commit()：提交事务，使所有更改永久生效
 * 4. Connection.rollback()：回滚事务，撤销所有未提交的更改
 * 5. 事务边界：以 setAutoCommit(false) 为开始，
 *    以 commit() 或 rollback() 为结束
 * 6. 在 finally 或异常处理中确保资源正确释放
 * 7. 嵌套 try-catch：回滚操作本身也可能抛出异常
 * 8. PreparedStatement 在事务环境中的应用
 * ============================================================
 */
package chp12_JDBC.exp12_3;                                // 声明包路径，属于第12章JDBC实验3

import java.sql.Connection;                                 // 导入Connection接口，表示数据库连接
import java.sql.DriverManager;                              // 导入DriverManager类，管理JDBC驱动和连接
import java.sql.PreparedStatement;                          // 导入PreparedStatement接口，预编译SQL语句
import java.sql.ResultSet;                                  // 导入ResultSet接口，表示查询结果集
import java.sql.SQLException;                               // 导入SQLException类，JDBC操作的标准异常
import java.sql.Statement;                                  // 导入Statement接口，用于执行静态SQL语句

public class TransactionTest {                              // 定义公开类TransactionTest

    public static void main(String args[]) {                // 程序入口点

        String url = "jdbc:mysql://localhost/test";         // 定义数据库URL：连接本地test数据库
        Connection con = null;                              // 声明Connection引用并初始化为null（finally中需要判断）
        Statement stmt;                                     // 声明Statement引用（用于最终查询）
        PreparedStatement updateSales;                      // 声明PreparedStatement引用：更新SALES字段
        PreparedStatement updateTotal;                      // 声明PreparedStatement引用：更新TOTAL字段

        String updateString = "update COFFEES " +           // 参数化UPDATE：更新本周销量
                "set SALES = ? where COF_NAME = ?";         // ?占位符：第1个代指新销量，第2个代指咖啡名称

        String updateStatement = "update COFFEES " +        // 参数化UPDATE：更新累计总销量
                "set TOTAL = TOTAL + ? where COF_NAME = ?"; // ?占位符：第1个代指增加的销量，第2个代指咖啡名称
        String query = "select COF_NAME, SALES, TOTAL from COFFEES"; // 查询语句：获取咖啡名称、销量和累计总量

        try {                                               // try块开始：加载数据库驱动
            Class.forName("com.mysql.jdbc.Driver");         // 通过反射加载MySQL JDBC驱动类

        } catch (java.lang.ClassNotFoundException e) {      // 捕获驱动类未找到异常
            System.err.print("ClassNotFoundException: ");   // 打印异常类型前缀
            System.err.println(e.getMessage());             // 打印异常详细信息
        }                                                   // catch块结束

        try {                                               // try块开始：建立连接并执行事务操作

            con = DriverManager.getConnection(url, "root", "java"); // 建立数据库连接（用户名root，密码java）

            // 创建两个PreparedStatement预编译对象
            updateSales = con.prepareStatement(updateString); // 预编译更新SALES的SQL语句
            updateTotal = con.prepareStatement(updateStatement); // 预编译更新TOTAL的SQL语句
            int[] salesForWeek = {175, 150, 60, 155, 90};  // 定义本周销量数组（5种咖啡的新销量）
            String[] coffees = {"Colombian", "French_Roast", // 定义咖啡名称数组
                    "Espresso", "Colombian_Decaf",          // 5种咖啡的名称
                    "French_Roast_Decaf"};
            int len = coffees.length;                       // 获取数组长度

            // 关闭自动提交模式，开启手工事务管理
            con.setAutoCommit(false);                       // 关闭自动提交，后续所有操作在同一个事务中

            // 循环中每个咖啡执行两个更新操作，作为一个事务单元
            for (int i = 0; i < len; i++) {                // 遍历5种咖啡
                updateSales.setInt(1, salesForWeek[i]);     // 为更新SALES的SQL设置销量参数
                updateSales.setString(2, coffees[i]);       // 设置咖啡名称参数
                updateSales.executeUpdate();                // 执行SALES更新操作

                updateTotal.setInt(1, salesForWeek[i]);     // 为更新TOTAL的SQL设置增量参数（累加）
                updateTotal.setString(2, coffees[i]);       // 设置咖啡名称参数
                updateTotal.executeUpdate();                // 执行TOTAL累加更新操作
                con.commit();                               // 手动提交事务：两条UPDATE作为一个原子事务提交
            }                                               // for循环结束

            // 恢复自动提交模式
            con.setAutoCommit(true);                        // 恢复数据库连接的自动提交模式

            updateSales.close();                            // 关闭PreparedStatement updateSales
            updateTotal.close();                            // 关闭PreparedStatement updateTotal

            stmt = con.createStatement();                   // 创建Statement对象用于查询
            ResultSet rs = stmt.executeQuery(query);        // 执行查询，获取COFFEES表中所有数据

            while (rs.next()) {                             // 循环遍历ResultSet结果集
                String c = rs.getString("COF_NAME");        // 通过列名获取咖啡名称
                int s = rs.getInt("SALES");                 // 通过列名获取本周销量
                int t = rs.getInt("TOTAL");                 // 通过列名获取累计总销量
                System.out.println(c + "     " + s + "    " + t); // 打印咖啡名称、销量和总销量
            }                                               // while循环结束

            stmt.close();                                   // 关闭Statement对象
            con.close();                                    // 关闭数据库连接

        } catch (SQLException ex) {                         // 捕获SQLException：数据库操作过程中发生异常
            System.err.println("SQLException: " + ex.getMessage()); // 打印SQL异常信息
            if (con != null) {                              // 检查连接是否已成功建立
                try {                                       // 内部try块：执行事务回滚（回滚操作本身也可能抛异常）
                    System.err.println("Transaction is being rolled back"); // 打印提示：事务正在回滚
                    con.rollback();                         // 执行事务回滚，撤销所有未提交的更改
                } catch (SQLException excep) {              // 捕获回滚操作本身可能抛出的异常
                    System.err.println("SQLException: " + excep.getMessage()); // 打印回滚异常信息
                }                                           // 内部catch块结束
            }                                               // if结束
        }                                                   // 外部catch块结束
    }                                                       // main方法结束
}                                                           // 类定义结束

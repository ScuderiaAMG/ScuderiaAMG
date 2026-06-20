/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了 JDBC 中 PreparedStatement（预编译语句）的使用方法。
 * 主要功能包括：
 * 1. 加载 MySQL JDBC 驱动并建立数据库连接
 * 2. 使用 Statement 查询并显示原始数据
 * 3. 使用 PreparedStatement 批量更新多条记录
 *    — 利用占位符（?）构建参数化 SQL 更新语句
 *    — 使用 setInt() / setString() 方法为占位符绑定实际值
 *    — 循环执行多次更新操作
 * 4. 更新后重新查询并显示数据，验证更新结果
 *
 * 【知识点】
 * 1. PreparedStatement —— 预编译的参数化 SQL 语句
 *    - 相比 Statement 的优点：防止 SQL 注入、提高重复执行的性能
 *    - 使用 ? 作为占位符（placeholder），后续通过 setXxx() 方法赋值
 * 2. setInt(int parameterIndex, int x)：为指定位置的占位符设置 int 值
 * 3. setString(int parameterIndex, String x)：为指定位置的占位符设置字符串值
 * 4. executeUpdate()：执行 INSERT / UPDATE / DELETE 等 DML 语句
 * 5. Class.forName() 动态加载驱动
 * 6. DriverManager.getConnection() 建立数据库连接
 * 7. ResultSet 遍历查询结果
 * 8. SQLException 异常处理
 * 9. 占位符索引从 1 开始（不是 0），与 SQL 参数的顺序对应
 * ============================================================
 */
package chp12_JDBC.exp12_2;                                  // 声明包路径，属于第12章JDBC实验2

import java.sql.Connection;                                   // 导入Connection接口，表示数据库连接
import java.sql.DriverManager;                                // 导入DriverManager类，用于管理JDBC驱动和获取数据库连接
import java.sql.PreparedStatement;                            // 导入PreparedStatement接口，用于执行预编译的参数化SQL语句
import java.sql.ResultSet;                                    // 导入ResultSet接口，表示数据库查询的结果集
import java.sql.SQLException;                                 // 导入SQLException类，JDBC操作的标准异常类型
import java.sql.Statement;                                    // 导入Statement接口，用于执行静态SQL语句

public class PreparedTest {                                   // 定义公开类PreparedTest，演示PreparedStatement用法
    public static void main(String args[]) {                  // 程序入口点
        String url = "jdbc:mysql://localhost/test";           // 定义数据库连接URL：JDBC协议+MySQL子协议+主机localhost+数据库名test
        Connection con;                                       // 声明Connection引用，用于表示与数据库的会话连接
        Statement stmt;                                       // 声明Statement引用，用于执行普通的静态SQL语句
        String name;                                          // 声明String变量name，暂存查询结果中的咖啡名称
        int sale;                                             // 声明int变量sale，暂存查询结果中的销量

        try {                                                 // try块：加载MySQL JDBC驱动
            Class.forName("com.mysql.jdbc.Driver");           // 通过反射加载MySQL JDBC驱动类，使DriverManager能够识别MySQL连接
        } catch (java.lang.ClassNotFoundException e) {        // 捕获ClassNotFoundException：驱动JAR包未引入时抛出
            System.err.print("ClassNotFoundException: ");     // 在标准错误流打印异常类型提示
            System.err.println(e.getMessage());               // 打印异常的详细消息内容
        }                                                     // catch块结束

        try {                                                 // try块：建立数据库连接并执行数据库操作
            con = DriverManager.getConnection(url, "root", "java"); // 使用URL、用户名root、密码java建立数据库连接
            stmt = con.createStatement();                     // 通过Connection创建Statement对象，用于发送SQL语句到数据库

            showValues(stmt, "The original values:");        // 调用showValues方法显示更新前的原始数据

            PreparedStatement updateSales;                    // 声明PreparedStatement引用，用于执行参数化的UPDATE语句
            String updateString = "update COFFEES " +         // 定义UPDATE SQL语句的第一部分：指定要更新的表名COFFEES
                                  "set SALES = ? where COF_NAME= ? "; // 使用两个占位符?：第1个表示新的销量值，第2个表示咖啡名称（条件）
            updateSales = con.prepareStatement(updateString); // 通过连接预编译SQL语句，返回PreparedStatement对象

            int[] salesForWeek = {150, 140, 50, 145, 85};     // 定义int数组：本周各咖啡的新销量值（按顺序对应下面的咖啡名称）
            String[] coffees = {"Colombian", "French_Roast", "Espresso", // 定义String数组：要更新销量的咖啡名称列表
                                "Colombian_Decaf", "French_Roast_Decaf"}; // 共5种咖啡
            int len = coffees.length;                          // 获取咖啡数组的长度（即需要更新的记录数 = 5）

            for (int i = 0; i < len; i++) {                  // 循环遍历每种咖啡，i从0到4
                updateSales.setInt(1, salesForWeek[i]);       // 为第1个占位符（SALES字段）设置int值：当前咖啡对应的新销量
                updateSales.setString(2, coffees[i]);         // 为第2个占位符（COF_NAME字段）设置String值：当前咖啡的名称
                updateSales.executeUpdate();                   // 执行参数化的UPDATE语句，更新数据库中对应咖啡的销量
            }                                                  // for循环结束

            System.out.println();                              // 打印空行，分隔更新前后的数据展示
            showValues(stmt, "The new values :");             // 调用showValues方法显示更新后的新数据

        } catch (SQLException ex) {                            // 捕获SQLException：数据库操作发生异常时执行
            System.err.println("SQLException: " + ex.getMessage()); // 在标准错误流打印SQL异常信息
        }                                                      // catch块结束
    }                                                          // main方法结束

    /**
     * 辅助方法：查询COFFEES表中的所有记录并显示
     *
     * @param stmt Statement对象，用于执行SQL查询
     * @param s    展示数据的标题字符串
     * @throws SQLException 查询过程中可能抛出的SQL异常
     */
    public static void showValues(Statement stmt, String s) throws SQLException { // 定义showValues方法：接收Statement和标题，声明抛出SQLException
        String name;                                          // 声明局部变量name，存储查询结果中的咖啡名称
        int sale;                                             // 声明局部变量sale，存储查询结果中的销量值

        ResultSet rs = stmt.executeQuery("SELECT COF_NAME, SALES " + // 执行SELECT查询：查询COF_NAME和SALES两列
                                         "FROM COFFEES ");            // 从COFFEES表中查询所有记录
        System.out.println(s);                                // 打印传入的标题字符串（如"The original values:"或"The new values :"）

        while (rs.next()) {                                   // 循环遍历ResultSet：next()移动到下一行，有行时返回true
            name = rs.getString(1);                           // 通过列索引1获取COF_NAME列的值（String类型）
            sale = rs.getInt(2);                              // 通过列索引2获取SALES列的值（int类型）
            System.out.println("COFF_NAME = " + name + " ; \t" + "SALE = " + sale); // 格式化输出：咖啡名称和对应销量，以制表符分隔
        }                                                      // while循环结束
    }                                                          // showValues方法结束
}                                                              // 类定义结束

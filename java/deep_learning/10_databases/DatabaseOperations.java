/**
 * 数据库操作演示 - 数据库
 * 使用JDBC进行数据库操作
 */
package deep_learning.databases;

import java.sql.*;
import java.util.*;

public class DatabaseOperations {
    private Connection connection;

    /**
     * 建立数据库连接 (使用SQLite内存数据库演示)
     */
    public void connect() throws SQLException {
        // 使用SQLite内存数据库进行演示
        // 实际应用中替换为真实的数据库URL
        String url = "jdbc:sqlite::memory:";
        connection = DriverManager.getConnection(url);
        System.out.println("数据库连接成功!");
    }

    /**
     * 创建表
     */
    public void createTable() throws SQLException {
        String sql = """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                grade REAL,
                major TEXT
            )
            """;

        try (Statement stmt = connection.createStatement()) {
            stmt.execute(sql);
            System.out.println("表创建成功!");
        }
    }

    /**
     * 插入数据
     */
    public void insertStudent(String name, int age, double grade, String major) throws SQLException {
        String sql = "INSERT INTO students (name, age, grade, major) VALUES (?, ?, ?, ?)";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, name);
            pstmt.setInt(2, age);
            pstmt.setDouble(3, grade);
            pstmt.setString(4, major);
            pstmt.executeUpdate();
        }
    }

    /**
     * 批量插入
     */
    public void batchInsert(List<Map<String, Object>> records) throws SQLException {
        String sql = "INSERT INTO students (name, age, grade, major) VALUES (?, ?, ?, ?)";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            for (Map<String, Object> record : records) {
                pstmt.setString(1, (String) record.get("name"));
                pstmt.setInt(2, (Integer) record.get("age"));
                pstmt.setDouble(3, (Double) record.get("grade"));
                pstmt.setString(4, (String) record.get("major"));
                pstmt.addBatch();
            }
            pstmt.executeBatch();
        }
    }

    /**
     * 查询所有学生
     */
    public List<Map<String, Object>> getAllStudents() throws SQLException {
        List<Map<String, Object>> results = new ArrayList<>();
        String sql = "SELECT * FROM students";

        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            ResultSetMetaData metaData = rs.getMetaData();
            int columnCount = metaData.getColumnCount();

            while (rs.next()) {
                Map<String, Object> row = new LinkedHashMap<>();
                for (int i = 1; i <= columnCount; i++) {
                    row.put(metaData.getColumnName(i), rs.getObject(i));
                }
                results.add(row);
            }
        }
        return results;
    }

    /**
     * 条件查询
     */
    public List<Map<String, Object>> queryByMajor(String major) throws SQLException {
        List<Map<String, Object>> results = new ArrayList<>();
        String sql = "SELECT * FROM students WHERE major = ?";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, major);
            ResultSet rs = pstmt.executeQuery();

            ResultSetMetaData metaData = rs.getMetaData();
            int columnCount = metaData.getColumnCount();

            while (rs.next()) {
                Map<String, Object> row = new LinkedHashMap<>();
                for (int i = 1; i <= columnCount; i++) {
                    row.put(metaData.getColumnName(i), rs.getObject(i));
                }
                results.add(row);
            }
        }
        return results;
    }

    /**
     * 更新数据
     */
    public int updateGrade(int id, double newGrade) throws SQLException {
        String sql = "UPDATE students SET grade = ? WHERE id = ?";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setDouble(1, newGrade);
            pstmt.setInt(2, id);
            return pstmt.executeUpdate();
        }
    }

    /**
     * 删除数据
     */
    public int deleteStudent(int id) throws SQLException {
        String sql = "DELETE FROM students WHERE id = ?";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            return pstmt.executeUpdate();
        }
    }

    /**
     * 统计查询
     */
    public Map<String, Object> getStatistics() throws SQLException {
        Map<String, Object> stats = new HashMap<>();
        String sql = """
            SELECT
                COUNT(*) as total,
                AVG(grade) as avg_grade,
                MAX(grade) as max_grade,
                MIN(grade) as min_grade,
                COUNT(DISTINCT major) as major_count
            FROM students
            """;

        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            if (rs.next()) {
                stats.put("total_students", rs.getInt("total"));
                stats.put("average_grade", rs.getDouble("avg_grade"));
                stats.put("max_grade", rs.getDouble("max_grade"));
                stats.put("min_grade", rs.getDouble("min_grade"));
                stats.put("major_count", rs.getInt("major_count"));
            }
        }
        return stats;
    }

    /**
     * 分组统计
     */
    public List<Map<String, Object>> getStatsByMajor() throws SQLException {
        List<Map<String, Object>> results = new ArrayList<>();
        String sql = """
            SELECT major, COUNT(*) as count, AVG(grade) as avg_grade
            FROM students
            GROUP BY major
            ORDER BY avg_grade DESC
            """;

        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                Map<String, Object> row = new LinkedHashMap<>();
                row.put("major", rs.getString("major"));
                row.put("count", rs.getInt("count"));
                row.put("avg_grade", rs.getDouble("avg_grade"));
                results.add(row);
            }
        }
        return results;
    }

    /**
     * 关闭连接
     */
    public void close() throws SQLException {
        if (connection != null && !connection.isClosed()) {
            connection.close();
            System.out.println("数据库连接已关闭");
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 数据库操作演示 ===\n");

        DatabaseOperations db = new DatabaseOperations();

        try {
            // 连接数据库
            db.connect();

            // 创建表
            db.createTable();

            // 插入数据
            System.out.println("\n插入学生数据...");
            db.insertStudent("张三", 20, 85.5, "计算机科学");
            db.insertStudent("李四", 21, 92.0, "数学");
            db.insertStudent("王五", 19, 78.5, "计算机科学");
            db.insertStudent("赵六", 22, 88.0, "物理");
            db.insertStudent("钱七", 20, 95.5, "数学");

            // 批量插入
            List<Map<String, Object>> batch = new ArrayList<>();
            batch.add(Map.of("name", "孙八", "age", 21, "grade", 82.0, "major", "计算机科学"));
            batch.add(Map.of("name", "周九", "age", 20, "grade", 90.5, "major", "物理"));
            batch.add(Map.of("name", "吴十", "age", 22, "grade", 87.0, "major", "数学"));
            db.batchInsert(batch);

            // 查询所有学生
            System.out.println("\n所有学生:");
            List<Map<String, Object>> students = db.getAllStudents();
            printTable(students);

            // 条件查询
            System.out.println("\n计算机科学专业的学生:");
            List<Map<String, Object>> csStudents = db.queryByMajor("计算机科学");
            printTable(csStudents);

            // 更新数据
            System.out.println("\n更新张三的成绩为 90.0...");
            int updated = db.updateGrade(1, 90.0);
            System.out.println("更新了 " + updated + " 条记录");

            // 统计信息
            System.out.println("\n统计信息:");
            Map<String, Object> stats = db.getStatistics();
            for (Map.Entry<String, Object> entry : stats.entrySet()) {
                System.out.printf("  %s: %s%n", entry.getKey(), entry.getValue());
            }

            // 分组统计
            System.out.println("\n按专业统计:");
            List<Map<String, Object>> majorStats = db.getStatsByMajor();
            for (Map<String, Object> row : majorStats) {
                System.out.printf("  %s: 人数=%s, 平均分=%.1f%n",
                    row.get("major"), row.get("count"), row.get("avg_grade"));
            }

            // 删除数据
            System.out.println("\n删除ID为5的学生...");
            int deleted = db.deleteStudent(5);
            System.out.println("删除了 " + deleted + " 条记录");

            // 最终数据
            System.out.println("\n最终学生列表:");
            students = db.getAllStudents();
            printTable(students);

        } catch (SQLException e) {
            System.err.println("数据库错误: " + e.getMessage());
        } finally {
            try {
                db.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }

    private static void printTable(List<Map<String, Object>> data) {
        if (data.isEmpty()) {
            System.out.println("  (无数据)");
            return;
        }

        // 打印表头
        Set<String> columns = data.get(0).keySet();
        System.out.print("  ");
        for (String col : columns) {
            System.out.printf("%-15s", col);
        }
        System.out.println();
        System.out.println("  " + "-".repeat(columns.size() * 15));

        // 打印数据
        for (Map<String, Object> row : data) {
            System.out.print("  ");
            for (Object value : row.values()) {
                System.out.printf("%-15s", value);
            }
            System.out.println();
        }
    }
}

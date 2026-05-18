import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class JDBCExp1 {
	private static final String DRIVERCLASS = "com.microsoft.sqlserver.jdbc.SQLServerDriver";
	private final String url = "jdbc:sqlserver://127.0.0.1:1433;DatabaseName=msdb";
	private final String username = "sa";
	private final String password = "";
	private Connection conn;
	private Statement stmt;
	private PreparedStatement prpdStmt;
	private CallableStatement cablStmt;

	static {
		try {
			Class.forName(DRIVERCLASS);
		} catch (ClassNotFoundException e) {
			System.out.println("在加载数据库驱动时抛出异常，内容如下：");
			e.printStackTrace();
		}
	}

	// Statement
	public void useStatement(String sql) throws SQLException {
		stmt = conn.createStatement();
		stmt.executeUpdate(sql);
		stmt.close();
	}

	// PreparedStatement
	public void UsePreparedStatement(int[] id, String[] names) throws SQLException {
		prpdStmt = conn.prepareStatement("INSERT INTO Student VALUES(?,?)");// 预处理动态INSERT语句
		prpdStmt.clearBatch();// 清除Batch
		for (int i = 0; i < id.length; i++) {
			prpdStmt.setInt(1, id[i]);// 为动态SQL语句赋值
			prpdStmt.setString(2, names[i]);
			prpdStmt.addBatch();// 向Batch中添加INSERT语句
		}
		prpdStmt.executeBatch(); // 批量执行Batch中的INSERT语句
		prpdStmt.close();
	}

	// CallableStatement
	public void UseCallableStatement(int[] id, String[] names) throws SQLException {
		cablStmt = conn.prepareCall("{call proc_student_insert(?,?)}");
		cablStmt.clearBatch();
		for (int i = 0; i < id.length; i++) {
			cablStmt.setInt(1, id[i]);
			cablStmt.setString(2, names[i]);
			cablStmt.addBatch();
		}
		cablStmt.executeBatch();
		cablStmt.close();
	}

	// 查询所有记录
	public void selectAll() {
		List<Object[]> list = new ArrayList<Object[]>();
		try {
			stmt = conn.createStatement();
			ResultSet rs = stmt.executeQuery("SELECT * FROM Student");
			while (rs.next()) {
				Object note[] = new Object[2];
				for (int i = 0; i < note.length; i++) {
					note[i] = rs.getObject(i + 1);
				}
				list.add(note);
			}
			stmt.close();
		} catch (SQLException e) {
			System.out.println("在查询记录时抛出异常，内容如下：");
			e.printStackTrace();
		}
		for (int i = 0; i < list.size(); i++) {
			System.out.println(list.get(i)[0].toString() + '\t'
					+ list.get(i)[1].toString()); }
	}

	public static void main(String[] args) throws SQLException {
		JDBCExp1 a = new JDBCExp1();
		a.conn = DriverManager.getConnection(a.url, a.username, a.password);//建立连接
	
		//用普通语句创建数据表
		try{a.useStatement("DROP TABLE Student");}catch(SQLException e){}
		a.useStatement("CREATE TABLE Student(st_no int NOT Null PRIMARY KEY, st_name varchar(20) NOT Null)");

		//用预编译语句批添加数据
		int[] id={1,2,3};
		String[] name={"张三","李四","王五"};
		a.UsePreparedStatement(id,name);

		//用存储过程批添加数据
		try{a.useStatement("DROP PROCEDURE proc_student_insert");}catch(SQLException e){}
		a.useStatement("CREATE PROCEDURE proc_student_insert @id int,@name varchar(20) AS "+ 
						"INSERT INTO Student VALUES(@id,@name)");
		int[] id2={4,5};
		String[] name2={"Amy","Joan"};
		a.UseCallableStatement(id2,name2);

		//查询记录
		a.selectAll();

		a.conn.close();//断开连接
	}
}

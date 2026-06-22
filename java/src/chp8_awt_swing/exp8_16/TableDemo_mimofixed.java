/**
 * 【功能说明】
 * 本程序演示 JTable（表格组件）和 AbstractTableModel（自定义表格模型）的使用。
 * 创建了一个显示学生信息的彩色表格，包含姓名、学号、专业、性别、年龄、是否在校等列。
 * 通过继承 AbstractTableModel 自定义数据模型，实现了：
 *   - 数据只读保护（前2列不可编辑）
 *   - 数据校验（年龄列只接受整数）
 *   - 单元格可编辑
 *   - 自动适配列数据类型（Boolean 显示为复选框、Integer 正常显示等）
 * 同时开启 DEBUG 模式，在控制台输出所有数据修改的详细信息。
 *
 * 【知识点】
 * 1. JTable —— Swing 表格组件，以行和列的形式展示数据，支持排序、编辑、选择等。
 * 2. AbstractTableModel —— 抽象表格模型类，提供了 TableModel 接口的基本实现。
 *    自定义表格模型需实现的核心方法：
 *    - getRowCount(): 返回行数
 *    - getColumnCount(): 返回列数
 *    - getValueAt(row, col): 返回指定单元格的值
 *    可选重写的方法：
 *    - getColumnName(col): 返回列名
 *    - getColumnClass(col): 返回列的数据类型（影响显示方式）
 *    - isCellEditable(row, col): 指定单元格是否可编辑
 *    - setValueAt(value, row, col): 设置单元格的值
 * 3. JScrollPane —— 带滚动条的面板，将 JTable 放入后可实现滚动效果。
 * 4. setPreferredScrollableViewportSize() —— 设置表格在滚动面板中的视口大小。
 * 5. fireTableCellUpdated(row, col) —— 通知表格某单元格数据已更新，
 *    触发界面刷新（Model-View 模式的重要方法）。
 * 6. JOptionPane.showMessageDialog() —— 显示消息对话框，此处用于错误提示。
 * 7. 数据类型自动适配 —— Boolean 类型自动显示为复选框（JCheckBox），
 *    Integer 类型可正常编辑显示，由 getColumnClass() 返回的类型决定。
 * 8. 内部类 MyTableModel —— 将表格数据模型封装为内部类，
 *    便于访问外部类成员（如 TableDemo.this 用于对话框的父窗口指定）。
 * 9. DEBUG 变量 —— 通过布尔开关控制调试信息的输出，便于开发和调试。
 */

package chp8_awt_swing.exp8_16;                             // 声明包路径，对应第8章AWT/Swing实验16

import java.awt.BorderLayout;                               // 导入边界布局管理器
import java.awt.Dimension;                                  // 导入尺寸类
import java.awt.event.WindowAdapter;                        // 导入窗口事件适配器类
import java.awt.event.WindowEvent;                          // 导入窗口事件类

import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JOptionPane;                             // 导入对话框类（用于消息提示）
import javax.swing.JScrollPane;                             // 导入滚动面板类
import javax.swing.JTable;                                  // 导入表格组件类
import javax.swing.table.AbstractTableModel;                // 导入抽象表格模型类

public class TableDemo_mimofixed extends JFrame {                     // 继承 JFrame 创建自定义窗口类

    private boolean DEBUG = true;                           // DEBUG 开关：true 时在控制台输出调试信息

    public TableDemo_mimofixed() {                                    // 构造方法：初始化表格模型和界面
        super("TableDemo");                                 // 调用父类 JFrame 构造，设置窗口标题为 "TableDemo"

        MyTableModel myModel = new MyTableModel();          // 创建自定义表格数据模型对象
        JTable table = new JTable(myModel);                 // 创建 JTable 表格，绑定自定义数据模型
        table.setPreferredScrollableViewportSize(new Dimension(500, 70));
        // ↑ 设置表格在滚动面板中的视口首选大小（宽500、高70像素）

        // 创建带滚动条的滚动面板，将表格放入其中
        JScrollPane scrollPane = new JScrollPane(table);    // 创建滚动面板，内含表格

        // 将滚动面板添加到窗口的内容面板中央
        getContentPane().add(scrollPane, BorderLayout.CENTER); // 使用 BorderLayout 的 CENTER 区域

        addWindowListener(new WindowAdapter() {             // 注册窗口事件监听器（匿名内部类）
            public void windowClosing(WindowEvent e) {      // 重写 windowClosing：点击关闭按钮时触发
                System.exit(0);                             // 退出 JVM，结束程序
            }                                               // windowClosing 方法结束
        });                                                 // 匿名内部类结束
    }                                                       // 构造方法结束

    /* 自定义表格数据模型（内部类）。
     * 继承 AbstractTableModel，必须实现 getRowCount、getColumnCount、getValueAt 三个方法
     * 可选重写 getColumnName、getColumnClass、isCellEditable、setValueAt 等方法 */
    class MyTableModel extends AbstractTableModel {         // 定义内部类，继承抽象表格模型

        // 定义列名数组
        final String[] columnNames = {"姓名", "学号", "专业", "性别", "年龄", "在校"};

        // 定义表格数据（5行6列的学生信息数据）
        final Object[][] data = {                           // 二维 Object 数组，支持多种数据类型
            {"王山", "200101", "计算机科学",                // 第1行：姓名、学号、专业
             "男", Integer.valueOf(20), Boolean.valueOf(false)},    // 性别、年龄（Integer）、是否在校（Boolean），使用valueOf替代废弃的构造函数
            {"李立明", "200103", "计算机科学",              // 第2行
             "男", Integer.valueOf(29), Boolean.valueOf(true)},
            {"李丽", "200204", "电子工程",                  // 第3行
             "女", Integer.valueOf(21), Boolean.valueOf(false)},
            {"王红", "200208", "自动化",                    // 第4行
             "女", Integer.valueOf(25), Boolean.valueOf(true)},
            {"张阿宝", "200301", "机械设计",                // 第5行
             "男", Integer.valueOf(31), Boolean.valueOf(false)}
        };

        // 返回列数（必须实现的方法）
        public int getColumnCount() {                       // 获取表格的总列数
            return columnNames.length;                      // 返回列名数组的长度（6列）
        }                                                   // getColumnCount 方法结束

        // 返回行数（必须实现的方法）
        public int getRowCount() {                          // 获取表格的总行数
            return data.length;                             // 返回数据数组的长度（5行）
        }                                                   // getRowCount 方法结束

        // 返回指定列的名称（可选重写，默认返回 A, B, C...）
        public String getColumnName(int col) {               // 获取列名
            return columnNames[col];                        // 从列名数组中返回对应索引的列名
        }                                                   // getColumnName 方法结束

        // 返回指定单元格的值（必须实现的方法）
        public Object getValueAt(int row, int col) {        // 获取指定行列单元格的数据
            return data[row][col];                          // 从二维数据数组中取值
        }                                                   // getValueAt 方法结束

        // 返回列的数据类型（JTable 利用此信息决定显示方式）
        public Class<?> getColumnClass(int c) {                 // 获取指定列的数据类型，使用泛型参数<?>替代原始类型
            return getValueAt(0, c).getClass();             // 取第1行的该列数据，反射获取其 Class 类型
            // ↑ Boolean 类显示为复选框，Integer 类显示为可编辑数字，String 类显示为文本
        }                                                   // getColumnClass 方法结束

        // 判断指定单元格是否可编辑（可选重写）
        public boolean isCellEditable(int row, int col) {   // 判断单元格是否可编辑
            // 前两列（姓名、学号）不可编辑，其他列可编辑
            if (col < 2) {                                  // 如果列索引小于2（即第0列姓名、第1列学号）
                return false;                               // 返回 false 表示不可编辑
            } else {                                        // 其他列（专业、性别、年龄、在校）
                return true;                                // 返回 true 表示可编辑
            }                                               // 条件判断结束
        }                                                   // isCellEditable 方法结束

        // 设置单元格的值（可选重写，使表格可编辑必须实现）
        public void setValueAt(Object value, int row, int col) { // 设置指定单元格的值（由表格编辑触发）

            // 在控制台输出正在修改的数据信息（DEBUG 模式）
            if (DEBUG) {                                    // 如果 DEBUG 开关打开
                System.out.println("Setting value at " + row + "," + col // 输出行、列、新值、值类型
                                   + " to " + value
                                   + " (an instance of "
                                   + value.getClass() + ")");
            }                                               // DEBUG 输出结束

            // 数据校验：如果目标列数据是 Integer 类型，但传入的不是 Integer，则尝试转换
            if (data[0][col] instanceof Integer             // 如果该列第1行是 Integer 类型
                    && !(value instanceof Integer)) {       // 并且新值 value 不是 Integer 类型
                try {                                       // 尝试将 value 转为 Integer
                    data[row][col] = Integer.valueOf(value.toString()); // 通过字符串转换为 Integer，使用valueOf替代废弃的构造函数
                    fireTableCellUpdated(row, col);         // 通知表格该单元格数据已更新（刷新界面）
                } catch (NumberFormatException e) {         // 如果转换失败（如输入了非数字）
                    JOptionPane.showMessageDialog(TableDemo_mimofixed.this, // 弹出错误对话框
                            "The \"" + getColumnName(col)   // 显示提示信息：某列只接受整数值
                            + "\" column accepts only integer values.");
                }                                           // try-catch 结束
            } else {                                        // 其他情况：无需类型转换
                data[row][col] = value;                     // 直接将新值存入数据数组
                fireTableCellUpdated(row, col);             // 通知表格数据已更新
            }                                               // 类型判断结束

            // 在控制台输出修改后的所有数据（DEBUG 模式）
            if (DEBUG) {                                    // 如果 DEBUG 开关打开
                System.out.println("New value of data:");    // 输出 "新数据值："
                int numRows = getRowCount();                 // 获取总行数
                int numCols = getColumnCount();              // 获取总列数

                for (int i = 0; i < numRows; i++) {         // 遍历每一行
                    System.out.print("    row " + i + ":"); // 输出行号
                    for (int j = 0; j < numCols; j++) {     // 遍历每一列
                        System.out.print("  " + data[i][j]); // 输出该单元格的值
                    }                                       // 内层循环结束
                    System.out.println();                    // 换行
                }                                           // 外层循环结束
                System.out.println("--------------------------"); // 输出分隔线
            }                                               // DEBUG 输出结束
        }                                                   // setValueAt 方法结束

    }                                                       // 内部类 MyTableModel 结束

    public static void main(String[] args) {                // 主入口方法
        TableDemo_mimofixed frame = new TableDemo_mimofixed();                  // 创建 TableDemo 窗口对象
        frame.pack();                                       // 自动调整窗口大小
        frame.setVisible(true);                             // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束

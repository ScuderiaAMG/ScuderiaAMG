/**
 * 【功能说明】
 * 本程序演示 JTree（树形组件）的使用。
 * 用树形结构展示 Java 系列丛书的分类，根节点为 "The Java Series"。
 * 树包含两个分类分支：
 *   1. "Books for Java Programmers" —— 包含7本 Java 编程相关书籍
 *   2. "Books for Java Implementers" —— 包含2本 JVM 规范相关书籍
 * 当用户选中树中的某个节点时，会在控制台输出该节点的文字信息。
 * 树的选择模式设置为单选（同时只能选中一个节点）。
 *
 * 【知识点】
 * 1. JTree —— Swing 的树形组件，以树状结构展示分层数据。
 * 2. DefaultMutableTreeNode —— 树节点的默认实现，每个节点可以有多个子节点。
 *    - 根节点：树的最顶层节点
 *    - 分支节点：有子节点的节点
 *    - 叶节点：没有子节点的节点
 * 3. TreeSelectionModel.SINGLE_TREE_SELECTION —— 单选模式，
 *    用户一次只能选中树中的一个节点（还有 CONTIGUOUS_TREE_SELECTION、DISCONTIGUOUS_TREE_SELECTION）。
 * 4. addTreeSelectionListener() —— 注册树选择事件监听器，
 *    当用户选中或取消选中节点时触发 valueChanged 方法。
 * 5. TreeSelectionEvent —— 树选择事件对象，提供：
 *    - getPath(): 返回选中节点的路径
 *    - getSource(): 返回事件源（JTree）
 * 6. getLastSelectedPathComponent() —— 获取最后选中的路径组件（即选中的节点对象）。
 * 7. getUserObject() —— 获取节点的用户数据对象（默认为构造时传入的字符串）。
 * 8. JScrollPane —— 将树放入滚动面板，当树内容超出可视区域时自动出现滚动条。
 * 9. 辅助方法 createBranch() —— 封装创建分支的逻辑，将第一个元素作为父节点名称，
 *    其余元素作为子节点添加到父节点下，返回父节点。
 */

package chp8_awt_swing.exp8_17;                             // 声明包路径，对应第8章AWT/Swing实验17

import java.awt.BorderLayout;                               // 导入边界布局管理器
import java.awt.event.WindowAdapter;                        // 导入窗口事件适配器类
import java.awt.event.WindowEvent;                          // 导入窗口事件类

import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JScrollPane;                             // 导入滚动面板类
import javax.swing.JTree;                                   // 导入树形组件类
import javax.swing.event.TreeSelectionEvent;                // 导入树选择事件类
import javax.swing.event.TreeSelectionListener;             // 导入树选择监听器接口
import javax.swing.tree.DefaultMutableTreeNode;              // 导入树节点默认实现类
import javax.swing.tree.TreeSelectionModel;                 // 导入树选择模式类

public class TreeDemo extends JFrame {                      // 继承 JFrame 创建自定义窗口类

    // 树形结构要展示的数据：二维数组，第一维是分类，第二维是该分类下的书籍
    String[][] data = {{"Books for Java Programmers",       // 第1个分类及其子节点
                        "The Java Tutorial: Object-Oriented Programming for the Internet",
                        "The Java Tutorial Continued: The Rest of the JDK",
                        "The JFC Swing Tutorial: A Guide to Constructing GUIs",
                        "The Java Programming Language",
                        "The Java FAQ",
                        "The Java Class Libraries: An Annotated Reference",
                        "Concurrent Programming in Java: Design Principles and Patterns"},
                       {"Books for Java Implementers",      // 第2个分类及其子节点
                        "The Java Virtual Machine Specification",
                        "The Java Language Specification"}
                     };

    public TreeDemo() {                                     // 构造方法：初始化树形结构和界面
        super("TreeDemo");                                  // 调用父类 JFrame 构造，设置窗口标题为 "TreeDemo"

        // 创建根节点："The Java Series"（Java 系列丛书）
        DefaultMutableTreeNode top = new DefaultMutableTreeNode("The Java Series");

        // 遍历数据数组，为每个分类创建一个分支节点并添加到根节点上
        for (int i = 0; i < data.length; i++) {             // 遍历 data 数组的每一行（每个分类）
            top.add(createBranch(data[i]));                 // 调用 createBranch 创建分支并添加到根节点
        }                                                   // 循环结束

        // 创建 JTree，以 top 为根节点；设置选择模式为单选
        final JTree tree = new JTree(top);                  // 创建树形组件，指定根节点
        tree.getSelectionModel().setSelectionMode           // 获取树的选择模型，设置选择模式
                (TreeSelectionModel.SINGLE_TREE_SELECTION); // 设为单选模式（每次只能选中一个节点）

        // 为树注册选择事件监听器，当用户选中节点时触发
        tree.addTreeSelectionListener(new TreeSelectionListener() { // 匿名内部类实现 TreeSelectionListener
            public void valueChanged(TreeSelectionEvent e) { // 当树的选择状态发生变化时被调用
                DefaultMutableTreeNode node = (DefaultMutableTreeNode) // 获取最后选中的路径组件并转为树节点类型
                                   tree.getLastSelectedPathComponent(); // getLastSelectedPathComponent() 返回 Object 类型
                if (node == null) return;                   // 如果节点为 null（取消选中），不做处理直接返回
                Object nodeInfo = node.getUserObject();      // 获取节点中存储的用户数据对象（即节点文字）
                System.out.println(nodeInfo.toString());     // 在控制台输出选中节点的文字信息
            }                                               // valueChanged 方法结束
        });                                                 // 匿名内部类结束

        // 创建滚动面板，将树放入其中（树内容可滚动）
        JScrollPane treeView = new JScrollPane(tree);       // 创建包含树的滚动面板

        // 将滚动面板添加到窗口的内容面板中央
        getContentPane().add(treeView, BorderLayout.CENTER); // 使用 BorderLayout 在中央区域显示
    }                                                       // 构造方法结束

    // 辅助方法：根据字符串数组创建树的一个分支
    // 数组的第一个元素作为父节点（分类名称），其余元素作为子节点（书籍名称）
    DefaultMutableTreeNode createBranch(String[] data) {    // 接收字符串数组参数
        DefaultMutableTreeNode category = new DefaultMutableTreeNode(data[0]); // 创建分类节点（数组第一个元素）
        DefaultMutableTreeNode book = null;                 // 声明书籍节点变量（用于循环中创建）

        for (int i = 1; i < data.length; i++) {             // 从数组索引1开始遍历（书籍列表）
            book = new DefaultMutableTreeNode(data[i]);     // 为每本书创建子节点
            category.add(book);                             // 将书籍子节点添加到分类父节点下
        }                                                   // 循环结束

        return category;                                    // 返回已包含所有子节点的分类节点
    }                                                       // createBranch 方法结束

    public static void main(String[] args) {                // 主入口方法
        JFrame frame = new TreeDemo();                      // 创建 TreeDemo 窗口对象

        frame.addWindowListener(new WindowAdapter() {       // 注册窗口事件监听器（匿名内部类）
            public void windowClosing(WindowEvent e) {      // 重写 windowClosing 方法
                System.exit(0);                             // 退出 JVM，结束程序
            }                                               // windowClosing 方法结束
        });                                                 // 匿名内部类结束

        frame.setSize(400, 250);                            // 设置窗口宽400像素、高250像素
        frame.setVisible(true);                             // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束

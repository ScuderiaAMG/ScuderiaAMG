/**
 * 【功能说明】
 *   演示 Java File 类的文件重命名操作及文件元信息查询功能。
 *   程序接收两个命令行参数（源文件名和目标文件名），先显示原文件的各种属性信息，
 *   然后执行重命名操作，再显示重命名后文件的信息，最后检查原文件是否还存在。
 *   展示了 File 类常用的文件信息获取方法。
 *
 * 【知识点】
 *   1. File 类：代表文件或目录路径，提供文件/目录的创建、删除、重命名、属性查询等操作。
 *   2. renameTo(File dest)：将文件重命名为指定的目标路径（可移动文件到不同目录）。
 *   3. getAbsolutePath()：获取文件的绝对路径字符串。
 *   4. canRead() / canWrite()：检查文件是否可读/可写（返回 boolean）。
 *   5. getName()：获取文件名（不含路径）。
 *   6. getParent()：获取父目录路径字符串。
 *   7. getPath()：获取构造 File 时使用的路径字符串。
 *   8. length()：获取文件大小（字节数）。
 *   9. lastModified()：获取文件最后修改时间的时间戳（毫秒数），通过 new Date() 格式化为可读日期。
 *   10. isFile() / isDirectory()：判断 File 对象是文件还是目录。
 *   11. exists()：检查文件或目录是否存在。
 *   12. 命令行参数 (args)：通过 main 方法参数接收用户输入的原文件名和目标文件名。
 */
package chp7_io.exp7_6;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_6 子包中

import java.io.File;                         // 导入 File 类，文件和目录路径名的抽象表示，提供文件和目录操作功能
import java.util.Date;                       // 导入 Date 类，用于表示日期和时间（此处将时间戳格式化为可读日期）

public class RenameFile {                    // 定义 RenameFile 公有类（文件重命名演示）

    /**
     * 私有静态方法：输出 File 对象的详细信息
     * @param f  要查询信息的 File 对象
     */
    private static void fileData(File f) {   // 定义静态方法 fileData，参数为 File 对象
        System.out.println(                  // 输出文件的多项属性信息
          "Absolute path: " + f.getAbsolutePath() +   // 输出文件的绝对路径
          "\n Can read: " + f.canRead() +             // 输出文件是否可读
          "\n Can write: " + f.canWrite() +           // 输出文件是否可写
          "\n getName: " + f.getName() +               // 输出文件名
          "\n getParent: " + f.getParent() +           // 输出父目录路径
          "\n getPath: " + f.getPath() +               // 输出路径字符串
          "\n length: " + f.length() +                 // 输出文件大小（字节数）
          "\n lastModified: " + new Date(f.lastModified()));  // 将时间戳转为 Date 对象后输出最后修改时间
        if(f.isFile())                       // 判断 File 对象是否代表一个标准文件
          System.out.println("It's a file"); // 若是文件则输出提示
        else if(f.isDirectory())             // 判断 File 对象是否代表一个目录
          System.out.println("It's a directory");  // 若是目录则输出提示
    }                                        // fileData 方法结束

    /**
     * 主方法：接收两个命令行参数，执行文件重命名操作
     * 用法：java RenameFile 原文件名 新文件名
     */
    public static void main(String[] args) { // 程序入口 main 方法（注意此处未声明抛出异常）

        File old = new File(args[0]);         // 使用第一个命令行参数创建 File 对象，代表原文件
        File rname = new File(args[1]);       // 使用第二个命令行参数创建 File 对象，代表目标文件名

        System.out.println("The original file's information:");  // 输出提示信息：显示原文件信息
        fileData(old);                        // 调用 fileData 方法输出原文件的各种属性

        old.renameTo(rname);                  // 执行重命名操作：将 old 重命名为 rname（返回 boolean 值，但此处未使用返回值）

        System.out.println("\n The file information after rename:");  // 输出提示信息：显示重命名后的文件信息
        fileData(rname);                      // 调用 fileData 方法输出目标文件的各种属性（此时已是重命名后的文件）

        if (!old.exists()){                   // 检查原文件是否还存在（重命名后原路径应不再存在）
           System.out.println("\n The original file never exists.");  // 原文件已不存在，输出确认信息
        }                                     // if 语句结束

    }                                         // main 方法结束

}                                             // RenameFile 类结束

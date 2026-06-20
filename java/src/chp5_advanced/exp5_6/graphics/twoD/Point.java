/**
 * 【功能说明】
 * 本文件定义了Point（点）类，是二维图形库的基础组件。
 * 它表示二维平面中的一个坐标点，包含x和y坐标。
 * 该类被定义在chp5_advanced.exp5_6.graphics.twoD包中，
 * 供同包下的其他图形类（如Rectangle）和外部包使用。
 *
 * 【知识点】
 * 1. package声明：Java中用于组织类的机制，避免命名冲突
 * 2. public类：可以被其他包中的类访问和引用
 * 3. 构造方法（Constructor）：用于初始化新创建的对象
 * 4. this关键字：指代当前对象，用于区分构造参数和成员变量
 * 5. 包命名规范：通常使用反转的域名作为包名前缀
 */
package chp5_advanced.exp5_6.graphics.twoD;               // 声明包路径，该文件位于chp5_advanced.exp5_6.graphics.twoD包中

public class Point {                                       // 公有的Point类，表示二维平面中的一个点
    public int x = 0;                                      // 公有的实例变量x坐标，初始值为0
    public int y = 0;                                      // 公有的实例变量y坐标，初始值为0

    public Point(int x, int y) {                           // 带参构造方法：接收x和y坐标值
        this.x = x;                                        // 将构造参数x的值赋给当前对象的实例变量x（this区分成员变量和局部参数）
        this.y = y;                                        // 将构造参数y的值赋给当前对象的实例变量y
    }
}

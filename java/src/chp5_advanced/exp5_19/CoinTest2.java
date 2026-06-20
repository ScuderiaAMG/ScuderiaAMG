/**
 * 【功能说明】
 * 本程序是CoinTest的进阶版本，演示了枚举类型中多个属性的用法。
 * Coin2枚举不仅包含面值（value）属性，还包含颜色（color）属性，
 * 每个枚举常量在声明时同时传入面值和颜色。CoinColor2枚举定义了
 * 三种颜色。main方法遍历所有Coin2常量并输出名称、面值和颜色。
 * 文件末尾包含了被注释掉的早期版本的实现代码，作为对比参考。
 *
 * 【知识点】
 * 1. 枚举的多个属性：枚举常量可以拥有多个字段（如value和color）
 * 2. 枚举构造方法的多个参数：在常量声明时传入多个初始化值
 * 3. 枚举的封装性：枚举字段通常声明为private final
 * 4. 枚举方法可以返回各种类型，包括其他枚举类型
 * 5. 枚举常量直接调用toString()输出常量名
 * 6. 枚举的优势：类型安全、可读性强、可包含方法和数据
 * 7. 被注释掉的代码展示了另一种实现模式：通过静态方法和switch判断颜色
 * 8. 注释中的早期版本更类似于CoinTest，使用switch-case映射颜色
 */
package chp5_advanced.exp5_19;                             // 声明包路径，该文件位于chp5_advanced.exp5_19包中

enum Coin2 {                                               // 定义Coin2（硬币）枚举类型，带面值和颜色两个属性
    PENNY(1, CoinColor2.COPPER),                           // 枚举常量：1分硬币，铜色
    NICKEL(5, CoinColor2.NICKEL),                          // 枚举常量：5分硬币，镍色
    DIME(10, CoinColor2.SILVER),                           // 枚举常量：10分硬币，银色
    QUARTER(25, CoinColor2.SILVER);                        // 枚举常量：25分硬币，银色

    private final int value;                               // 私有的final成员变量：硬币的面值
    private final CoinColor2 color;                        // 私有的final成员变量：硬币的颜色（CoinColor2枚举类型）

    Coin2(int value, CoinColor2 color) {                   // 枚举构造方法：接收面值和颜色两个参数
        this.value = value;                                // 将参数中的面值赋值给成员变量value
        this.color = color;                                // 将参数中的颜色赋值给成员变量color
    }

    public int value() {                                   // 公有方法：返回硬币的面值
        return value;                                      // 返回成员变量value的值
    }

    public CoinColor2 color() {                            // 公有方法：返回硬币的颜色
        return color;                                      // 返回成员变量color的值
    }
}

enum CoinColor2 {                                          // 定义CoinColor2（硬币颜色）枚举类型
    COPPER,                                                // 铜色
    NICKEL,                                                // 镍色
    SILVER                                                 // 银色
}

public class CoinTest2 {                                   // 主类（public），测试带多个属性的枚举
    public static void main(String[] args) {               // 主方法：程序执行的入口点

        // System.out.println(": "+"  "+Coin.PENNY.value());  // （已注释）早期的调试输出语句
        for (Coin2 c : Coin2.values())                     // 使用增强for-each循环遍历Coin2枚举的所有常量
            System.out.println(c + ": " + c.value() + ", " + c.color()); // 输出硬币名称、面值和颜色
    }
}

// ====== 以下是早期版本的实现代码（被注释掉，作为对比参考）======
/* enum Coin {                                              // （已注释）早期的Coin枚举定义
    PENNY(1), NICKEL(5), DIME(10), QUARTER(25);            // （已注释）仅包含面值属性

    private final int value;                                // （已注释）私有的面值字段
    Coin(int value) { this.value = value; }                 // （已注释）构造方法
    public int value() { return value; }                    // （已注释）获取面值的方法
}

public class CoinTest {                                    // （已注释）早期的主类
     public static void main(String[] args) {              // （已注释）主方法

 // System.out.println(": "+"  "+Coin.PENNY.value());      // （已注释）调试输出
         for (Coin c : Coin.values())                      // （已注释）遍历所有硬币
         System.out.println(c + ": "+ c.value() +"? " +   // （已注释）输出硬币名称和面值
         color(c));                                        // （已注释）通过静态方法获取颜色
          }

    private enum CoinColor2 { COPPER, NICKEL, SILVER }     // （已注释）内部枚举类型（颜色）

    private static CoinColor2 color(Coin c) {              // （已注释）静态方法：根据硬币类型返回颜色
      switch(c) {                                          // （已注释）switch判断硬币类型
          case PENNY:                                      // （已注释）1分硬币
//              System.out.println("in switch: "+c+"  "+Coin.PENNY.value());  // （已注释）调试输出
              return CoinColor2.COPPER;                    // （已注释）返回铜色
          case NICKEL:                                     // （已注释）5分硬币
              return CoinColor2.NICKEL;                    // （已注释）返回镍色
          case DIME: case QUARTER:                         // （已注释）10分或25分硬币
              return CoinColor2.SILVER;                    // （已注释）返回银色
          default:                                         // （已注释）默认情况
              throw new AssertionError("Unknown coin: " + c); // （已注释）如果遇到未知硬币类型，抛出断言错误
      }
    }
}
*/

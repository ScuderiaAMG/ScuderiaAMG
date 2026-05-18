# 第3章 Java 基础 — 代码解释

本章涵盖 20 个示例（exp3-1 至 exp3-20），全面介绍 Java 的基本语法：数据类型、变量、运算符、流程控制、数组。

---

## exp3-1 — CharToInt.java：字符与整数的转换

```java
public class CharToInt{
   public static void main(String args[]){
        int intResult, intVar = 10;
        char charVar='A';

        intResult = intVar + charVar;

        System.out.println("The char is :  "+ charVar);
        System.out.println("The char's Unicode is :  \\u"+Integer.toHexString(charVar));
        System.out.println("The int value corresponding to the char is :  "
                    +new Integer(charVar).toString());
        System.out.println("Int "+intVar+" adds the char, the result is :  "+intResult);
   }
}
```

**解释：**

- `char` 类型在 Java 中以 **Unicode（UTF-16）** 编码存储，每个字符对应一个整数值。'A' 的 Unicode 码点是 `A`（十进制 65）。
- `intVar + charVar` — 字符与整数运算时，char 会**自动提升**为 int 类型（值为 65），因此 `10 + 65 = 75`。
- `Integer.toHexString(charVar)` — 将字符的 Unicode 码点转为十六进制字符串。
- `new Integer(charVar).toString()` — 利用 Integer 包装类获取字符对应的十进制整数值。

**知识点：** 基本类型转换、char 本质是整数、基本类型的自动提升。

---

## exp3-2 — Assign.java：变量的声明与赋值

```java
public class Assign {
    public static void main(String args[]) {
        int x, y;
        float z = 3.414f;
        double w = 3.1415;
        boolean truth = true;
        char c;
        String str;
        String str1 = "bye";
        c = 'A';
        str = "Hi out there";
        x = 6;
        y = 1000;

        System.out.println("x="+x);
        System.out.println("y="+y);
        System.out.println("z="+z);
        System.out.println("w="+w);
        System.out.println("truth="+truth);
        System.out.println("c="+c);
        System.out.println("str="+str);
        System.out.println("str1="+str1);
    }
}
```

**解释：**

- 展示 Java 八种**基本类型**中的六种：`int`（32位整数）、`float`（32位浮点数，字面量需加 `f` 后缀）、`double`（64位浮点数）、`boolean`（true/false）、`char`（16位 Unicode 字符）。
- `String` 是**引用类型**（类），不是基本类型，用双引号包裹字面量。
- 变量可以**先声明后赋值**（如 `int x, y;` 然后 `x = 6;`），也可以在声明时**初始化**（如 `float z = 3.414f;`）。

**知识点：** 变量声明语法、基本类型 vs 引用类型、字面量后缀。

---

## exp3-3 — SomeConstTest.java：包装类的常量

```java
public class SomeConstTest{
    public static void main(String args[]){
        System.out.println("Byte.MAX_VALUE ="+ Byte.MAX_VALUE);
        System.out.println("Byte.MIN_VALUE ="+ Byte.MIN_VALUE);

        System.out.println("Short.MAX_VALUE ="+ Short.MAX_VALUE);
        System.out.println("Short.MIN_VALUE ="+ Short.MIN_VALUE);

        System.out.println("Integer.MAX_VALUE ="+ Integer.MAX_VALUE);
        System.out.println("Integer.MIN_VALUE ="+ Integer.MIN_VALUE);

        System.out.println("Long.MAX_VALUE ="+ Long.MAX_VALUE);
        System.out.println("Long.MIN_VALUE ="+Long.MIN_VALUE);

        System.out.println("Float.MAX_VALUE ="+ Float.MAX_VALUE);
        System.out.println("Float.MIN_VALUE ="+ Float.MIN_VALUE);

        System.out.println("Double.MAX_VALUE ="+ Double.MAX_VALUE);
        System.out.println("Double.MIN_VALUE ="+ Double.MIN_VALUE);

        System.out.println("Float.POSITIVE_INFINITY ="+ Float.POSITIVE_INFINITY);
        System.out.println("Float.NEGATIVE_INFINITY ="+ Float.NEGATIVE_INFINITY);

        System.out.println("Double.POSITIVE_INFINITY ="+ Double.POSITIVE_INFINITY);
        System.out.println("Double.NEGATIVE_INFINITY ="+ Double.NEGATIVE_INFINITY);

        System.out.println("Float.NaN ="+ Float.NaN);
        System.out.println("Double.NaN ="+ Double.NaN);
    }
}
```

**解释：**

- 每种基本类型对应一个**包装类**（Wrapper Class）：`Byte`、`Short`、`Integer`、`Long`、`Float`、`Double`。
- `MAX_VALUE` / `MIN_VALUE` — 该类能表示的**最大值**和**最小值**。
- `POSITIVE_INFINITY` / `NEGATIVE_INFINITY` — 正无穷大和负无穷大（如 `1.0/0.0` 的结果）。
- `NaN`（Not a Number）— 非数值（如 `0.0/0.0` 的结果）。
- 特别注意：`Float.MIN_VALUE` 和 `Double.MIN_VALUE` 表示的是**最小正值**（接近0的正数），而不是负的最大值。

**知识点：** 包装类常量、IEEE 754 浮点数特殊值。

---

## exp3-4 — TestInit.java：变量初始化

```java
public class TestInit{
    int x;   // 成员变量，默认初始化为0

    public static void main(String args[]){
        TestInit init = new TestInit();
        int x = (int)(Math.random()*100);
        int z;
        int y;
        if (x > 50){
            y = 9;
        }
        z = x + y + init.x;  // 编译错误：y可能未被初始化
        System.out.println("x="+x+" y="+y+" z="+z+" init.x="+init.x);
    }
}
```

**解释：**

- 类的**成员变量**（`int x`）会自动初始化为默认值（int 默认为 0）。
- **局部变量**（方法内定义的变量）**不会自动初始化**，使用前必须显式赋值。
- 此例中 `y` 在 `if` 块中被赋值，编译器无法确定 `if` 条件一定为 true，因此 `y = x + y + init.x` 编译时会报错"变量 y 可能尚未初始化"。
- `Math.random()` 返回 `[0.0, 1.0)` 之间的随机 double 值。

**知识点：** 成员变量默认初始化、局部变量必须手动初始化、编译器确定性赋值检查。

---

## exp3-5 — TestUnary.java：一元运算符

```java
public class TestUnary{
    public static void main(String args[]){
        int a = 9;
        int b = -a;        // 一元负号
        byte bb = 9;
        int ib = +bb;      // 一元正号（提升为int）
        int x = 4, y = 8;
        int z;
        int i = 0;
        int j = i++;       // 后缀++：先赋值再自增
        int k = ++j;       // 前缀++：先自增再赋值

        z = (x++) * (--y); // x先用后增，y先减后用

        System.out.println("a = " + a);   // 9
        System.out.println("b = " + b);   // -9
        System.out.println("i = " + i);   // 1
        System.out.println("j = " + j);   // 1
        System.out.println("k = " + k);   // 1
        System.out.println("x = " + x);   // 5
        System.out.println("y = " + y);   // 7
        System.out.println("z = " + z);   // 28 (= 4 * 7)
    }
}
```

**解释：**

- **一元负号 `-`**：取负数，`-a` 将 9 变为 -9。
- **一元正号 `+`**：对 byte/short/char 执行一元正号时，会自动提升为 int 类型。
- **`i++`（后缀自增）**：先将 i 的当前值赋给 j（j=0），然后 i 自增为 1。
- **`++j`（前缀自增）**：先将 j 自增为 1（j 原本是 0，经过 `j=i++` 赋值为 0），然后赋给 k（k=1）。注意执行顺序：`int j=i++` 后 j=0, i=1；`int k=++j` 后 j=1, k=1。
- **`z = (x++) * (--y)`**：x++ 先用 4 参与乘法，再自增为 5；--y 先自减为 7，再用 7 参与乘法；z = 4 × 7 = 28。

**知识点：** 一元运算符、前缀 vs 后缀自增/自减的区别。

---

## exp3-6 — WhileDemo.java：while 循环

```java
public class WhileDemo {
    public static void main(String[] args) {
        String copyFromMe = "Copy this string until you encounter the letter 'g'.";
        StringBuffer copyToMe = new StringBuffer();
        int i = 0;
        char c = copyFromMe.charAt(i);

        while (c != 'g') {
            copyToMe.append(c);
            c = copyFromMe.charAt(++i);
        }
        System.out.println(copyToMe);  // 输出: Copy this strin
    }
}
```

**解释：**

- `while (条件) { 循环体 }` — 先判断条件，条件为 true 时执行循环体，条件为 false 时跳出循环。
- `charAt(i)` — String 方法，获取字符串中索引 i 处的字符（索引从 0 开始）。
- `StringBuffer` — 可变字符串类，`append()` 追加字符。
- 循环逐字符复制，直到遇到字符 `'g'` 时停止（不包含 g）。

**知识点：** while 循环、String 的 charAt 方法、StringBuffer 的使用。

---

## exp3-7 — DoWhileDemo.java：do-while 循环

```java
public class DoWhileDemo {
    public static void main(String[] args) {
        String copyFromMe = "Copy this string until you encounter the letter 'g'.";
        StringBuffer copyToMe = new StringBuffer();
        int i = 0;
        char c = copyFromMe.charAt(i);

        do {
            copyToMe.append(c);
            c = copyFromMe.charAt(++i);
        } while (c != 'g');
        System.out.println(copyToMe);  // 输出: Copy this strin
    }
}
```

**解释：**

- `do { 循环体 } while (条件);` — **先执行一次循环体**，再判断条件。与 while 相反，do-while 保证循环体至少执行一次。
- 注意 while 后面有分号 `;`，这是必需语法。
- 本例中两个程序输出相同，因为第一个字符 'C' 不等于 'g'，两种情况都会进入循环。

**知识点：** do-while 循环、do-while 与 while 的区别。

---

## exp3-8 — ForDemo.java：for 循环

```java
public class ForDemo {
    public static void main(String[] args) {
        int[] arrayOfInts = { 32, 87, 3, 589, 12, 1076, 2000, 8, 622, 127 };

        for (int i = 0; i < arrayOfInts.length; i++) {
            System.out.print(arrayOfInts[i] + " ");
        }
        System.out.println();
    }
}
```

**解释：**

- `for (初始化; 条件; 迭代) { 循环体 }` — 经典 for 循环。
  - `int i = 0`：循环变量初始化，只在循环开始时执行一次。
  - `i < arrayOfInts.length`：每次迭代前检查条件。
  - `i++`：每次迭代结束后执行。
- `arrayOfInts.length` — 数组的 length 属性，返回数组元素个数（10）。

**知识点：** for 循环的完整语法、数组遍历、数组的 length 属性。

---

## exp3-9 — IfElseDemo.java：if-else 条件判断

```java
public class IfElseDemo {
    public static void main(String[] args) {
        int testscore = 76;
        char grade;

        if (testscore >= 90) {
            grade = 'A';
        } else if (testscore >= 80) {
            grade = 'B';
        } else if (testscore >= 70) {
            grade = 'C';
        } else if (testscore >= 60) {
            grade = 'D';
        } else {
            grade = 'F';
        }
        System.out.println("Grade = " + grade);  // 输出: Grade = C
    }
}
```

**解释：**

- `if-else if-else` 构成**多分支条件判断**链。条件按顺序从上到下检查，一旦某个条件为 true，执行对应代码块后**跳过后续所有条件**。
- 76 满足 `>= 70` 但不满足 `>= 80`，因此 grade = 'C'。
- 如果不使用 else if 而写多个独立 if，每个条件都会被逐个检查，逻辑不同。

**知识点：** if-else if-else 链、多分支条件的选择逻辑。

---

## exp3-10 — SwitchDemo.java 与 SwitchDemo2.java：switch 语句

### SwitchDemo.java — 基础用法

```java
public class SwitchDemo {
    public static void main(String[] args) {
        int month = 8;
        switch (month) {
            case 1:  System.out.println("January"); break;
            case 2:  System.out.println("February"); break;
            case 3:  System.out.println("March"); break;
            // ... case 4~12 ...
            case 8:  System.out.println("August"); break;
            // ...
            default: System.out.println("Hey, that's not a valid month!"); break;
        }
    }
}
```

**解释：**

- `switch (表达式)` — 表达式可以是 `byte`、`short`、`char`、`int`、enum、String（Java 7+）。
- 每个 `case` 匹配后，代码执行到遇到 `break` 才跳出 switch，否则会**穿透（fall-through）**到下一个 case。
- `default` — 所有 case 都不匹配时执行，类似 if-else 中的最后一个 else。

### SwitchDemo2.java — 穿透（Fall-through）的使用

```java
public class SwitchDemo2 {
    public static void main(String[] args) {
        int month = 2;
        int year = 2000;
        int numDays = 0;

        switch (month) {
            case 1: case 3: case 5: case 7: case 8: case 10: case 12:
                numDays = 31; break;
            case 4: case 6: case 9: case 11:
                numDays = 30; break;
            case 2:
                if (((year % 4 == 0) && !(year % 100 == 0)) || (year % 400 == 0))
                    numDays = 29;
                else
                    numDays = 28;
                break;
        }
        System.out.println("The date is 2000.2. The number of Days = " + numDays);  // 29
    }
}
```

**解释：**

- 巧妙利用 **fall-through**：多个 case 堆叠在一起共享同一段代码（1/3/5/7/8/10/12 月都为 31 天）。
- 2 月特殊处理：用**闰年公式**判断。能被 4 整除且不能被 100 整除，或者能被 400 整除的年份为闰年。2000 年能被 400 整除，故为 29 天。

**知识点：** switch-case 的 fall-through 特性、break 终止 switch、闰年条件判断。

---

## exp3-11 — BreakDemo.java：break 退出循环

```java
public class BreakDemo {
    public static void main(String[] args) {
        int[] arrayOfInts = { 32, 87, 3, 589, 12, 1076, 2000, 8, 622, 127 };
        int searchfor = 12;
        int i = 0;
        boolean foundIt = false;

        for ( ; i < arrayOfInts.length; i++) {
            if (arrayOfInts[i] == searchfor) {
                foundIt = true;
                break;    // 找到目标后立即跳出循环
            }
        }
        if (foundIt) {
            System.out.println("Found " + searchfor + " at index " + i);  // index 4
        } else {
            System.out.println(searchfor + " not in the array");
        }
    }
}
```

**解释：**

- `break` 在循环中作用是**立即终止当前循环**，程序继续执行循环后的第一条语句。
- 此处 break 使循环在找到目标 12（index=4）后停止，不再继续遍历剩余元素，提高效率。

**知识点：** break 终止循环、线性查找。

---

## exp3-12 — BreakWithLabelDemo.java：带标签的 break

```java
public class BreakWithLabelDemo {
    public static void main(String[] args) {
        int[][] arrayOfInts = { { 32, 87, 3, 589 },
                                { 12, 1076, 2000, 8 },
                                { 622, 127, 77, 955 } };
        int searchfor = 12;
        int i = 0, j = 0;
        boolean foundIt = false;

search:
        for ( ; i < arrayOfInts.length; i++) {
            for (j = 0; j < arrayOfInts[i].length; j++) {
                if (arrayOfInts[i][j] == searchfor) {
                    foundIt = true;
                    break search;   // 跳出标签指向的外层循环
                }
            }
        }
        if (foundIt) {
            System.out.println("Found " + searchfor + " at " + i + ", " + j);  // 1, 0
        }
    }
}
```

**解释：**

- 普通的 `break` 只能跳出**当前一层**循环。在嵌套循环中，如果需要跳出外层循环，可以使用**带标签的 break**。
- 语法：`标签名: for/while { ... break 标签名; }`
- `break search` 直接跳出最外层的 for 循环，避免了需要在每层都判断 foundIt 来手动退出。

**知识点：** 标签语法（label）、带标签的 break 跳出多层循环。

---

## exp3-13 — ContinueDemo.java：continue 跳过本次迭代

```java
public class ContinueDemo {
    public static void main(String[] args) {
        StringBuffer searchMe = new StringBuffer(
                  "peter piper picked a peck of pickled peppers");
        int max = searchMe.length();
        int numPs = 0;

        for (int i = 0; i < max; i++) {
            if (searchMe.charAt(i) != 'p')
                continue;      // 不是 'p' 则跳过本次循环，进入下一次迭代
            numPs++;
            searchMe.setCharAt(i, 'P');  // 将小写 p 替换为大写 P
        }
        System.out.println("Found " + numPs + " p's in the string.");
        System.out.println(searchMe);
    }
}
```

**解释：**

- `continue` 用于**跳过当前迭代的剩余代码**，直接进入下一次循环的条件判断和迭代。
- 本例中，当字符不是 'p' 时，`continue` 使程序跳过计数和替换，直接处理下一个字符。
- 结果：统计了所有 'p' 的数量，并将所有小写 'p' 改为大写 'P'。

**知识点：** continue 跳过循环体剩余部分、与 break 的区别（continue 不终止循环）。

---

## exp3-14 — ContinueWithLabelDemo.java：带标签的 continue

```java
public class ContinueWithLabelDemo {
    public static void main(String[] args) {
        String searchMe = "Look for a substring in me";
        String substring = "sub";
        boolean foundIt = false;
        int max = searchMe.length() - substring.length();

test:
        for (int i = 0; i <= max; i++) {
            int n = substring.length();
            int j = i;
            int k = 0;
            while (n-- != 0) {
                if (searchMe.charAt(j++) != substring.charAt(k++)) {
                    continue test;   // 当前字符不匹配，跳到外层 for 下一次迭代
                }
            }
            foundIt = true;
            break test;   // 所有字符匹配成功，跳出外层循环
        }
        System.out.println(foundIt ? "Found it" : "Didn't find it");  // Found it
    }
}
```

**解释：**

- 实现了一个**简单的子字符串匹配算法**（类似暴力匹配）。
- 外层 `for` 循环：从 `searchMe` 的每个位置尝试匹配。
- 内层 `while` 循环：逐字符比较 `substring`。一旦发现字符不匹配，`continue test` **跳到外层 for 循环的下一个位置**重新开始匹配（不是只跳出内层 while，而是跳过外层的当前迭代）。
- 如果内层 while 完整执行完（所有字符匹配），设置 `foundIt = true`，然后用 `break test` 跳出外层循环。

**知识点：** 带标签的 continue、暴力字符串匹配算法、标签 break 与 continue 的配合使用。

---

## exp3-15 — ArrayDemo.java：一维数组

```java
public class ArrayDemo {
    public static void main(String[] args) {
        int[] anArray;                 // 声明数组引用
        anArray = new int[10];         // 创建数组对象，分配10个元素（默认值0）

        for (int i = 0; i < anArray.length; i++) {
            anArray[i] = i;
            System.out.print(anArray[i] + " ");
        }
        System.out.println();
    }
}
```

**解释：**

- `int[] anArray` — 声明一个 int 数组**引用**，此时还未分配内存。
- `anArray = new int[10]` — 用 `new` 关键字在堆上分配 10 个 int 元素的连续内存空间，每个元素默认初始化为 0。
- `anArray[i]` — 通过**索引**（从 0 开始）访问数组元素。
- `anArray.length` — 数组的长度属性，值为 10。

**知识点：** 数组的声明、创建、初始化、通过索引访问。

---

## exp3-16 — ArrayOfStringsDemo.java：字符串数组

```java
public class ArrayOfStringsDemo {
    public static void main(String[] args) {
        String[] anArray = { "String One", "String Two", "String Three" };

        for (int i = 0; i < anArray.length; i++) {
            System.out.println(anArray[i].toLowerCase());
        }
    }
}
```

**解释：**

- 使用**静态初始化**语法：`{ 元素1, 元素2, ... }` 在声明的同时赋值，无需指定数组长度。
- `String[]` 是引用类型数组，每个元素是对 String 对象的引用。
- `toLowerCase()` — String 的方法，将所有字符转换为小写。

**知识点：** 数组的静态初始化、引用类型数组。

---

## exp3-17 — ArrayOfArraysDemo1.java：二维数组（不规则数组）

```java
public class ArrayOfArraysDemo1 {
    public static void main(String[] args) {
        int[][] aMatrix = new int[4][];   // 只指定第一维长度

        for (int i = 0; i < aMatrix.length; i++) {
            aMatrix[i] = new int[5];      // 每行创建5个元素的子数组
            for (int j = 0; j < aMatrix[i].length; j++) {
                aMatrix[i][j] = i + j;
            }
        }

        for (int i = 0; i < aMatrix.length; i++) {
            for (int j = 0; j < aMatrix[i].length; j++) {
                System.out.print(aMatrix[i][j] + " ");
            }
            System.out.println();
        }
    }
}
```

**解释：**

- Java 中没有真正的多维数组，**二维数组本质是"数组的数组"**（array of arrays）。
- `new int[4][]` — 只创建 4 个引用（每个引用指向一个一维 int 数组），初始值为 null。
- `aMatrix[i] = new int[5]` — 为每一行分别创建子数组。
- 这意味着每一行**可以有不同的长度**——Java 支持**不规则数组**（ragged array）。

**知识点：** Java 中数组的数组实现、"多维数组"的本质、不规则数组。

---

## exp3-18 — ArrayOfArraysDemo2.java：不规则二维数组

```java
public class ArrayOfArraysDemo2 {
    public static void main(String[] args) {
        String[][] cartoons = {
            { "Flintstones", "Fred", "Wilma", "Pebbles", "Dino" },
            { "Rubbles", "Barney", "Betty", "Bam Bam" },
            { "Jetsons", "George", "Jane", "Elroy", "Judy", "Rosie", "Astro" },
            { "Scooby Doo Gang", "Scooby Doo", "Shaggy", "Velma", "Fred", "Daphne" }
        };

        for (int i = 0; i < cartoons.length; i++) {
            System.out.print("cartoons["+i+"]"+", "+ cartoons[i].length+"elements: ");
            for (int j = 0; j < cartoons[i].length; j++) {
                System.out.print(cartoons[i][j] + (j<cartoons[i].length-1?", ":" "));
            }
            System.out.println();
        }
    }
}
```

**解释：**

- 二维数组的**静态初始化**：嵌套花括号直接赋值。
- 各行长度不同：第一行 5 个元素、第二行 4 个、第三行 7 个、第四行 6 个，体现了不规则数组。
- 输出示例：`cartoons[0], 5elements: Flintstones, Fred, Wilma, Pebbles, Dino`
- 三元运算符 `(j<...-1?", ":" ")` 在最后一个元素后不加逗号。

**知识点：** 二维数组静态初始化、不规则数组的实际应用。

---

## exp3-19 — NewArrayOfStringsDemo.java：增强 for 循环（for-each）

```java
public class NewArrayOfStringsDemo {
    public static void main(String[] args) {
        String[] anArray = { "String One", "String Two", "String Three" };

        for (String s : anArray) {
            System.out.println(s.toLowerCase());
        }
    }
}
```

**解释：**

- `for (类型 变量 : 数组或集合)` — Java 5 引入的**增强 for 循环**（for-each）。
- 每次迭代，`s` 自动获取数组的下一个元素，无需使用索引变量。
- 优点：语法简洁，避免数组越界错误。
- 缺点：无法获取当前索引，无法修改数组元素。

**知识点：** for-each 循环、与普通 for 循环的取舍。

---

## exp3-20 — ArrayCopyDemo.java：数组复制

```java
public class ArrayCopyDemo {
    public static void main(String[] args) {
        char[] copyFrom = { 'd', 'e', 'c', 'a', 'f', 'f', 'e',
                    'i', 'n', 'a', 't', 'e', 'd' };
        char[] copyTo = new char[7];

        System.arraycopy(copyFrom, 2, copyTo, 0, 7);
        System.out.println(new String(copyTo));   // 输出: caffein
    }
}
```

**解释：**

- `System.arraycopy(源数组, 源起始索引, 目标数组, 目标起始索引, 复制长度)` — 高效的原生数组复制方法。
- 本例从 `copyFrom[2]`（即字符 'c'）开始，复制 7 个字符到 `copyTo`，得到 "caffein"。
- `new String(copyTo)` — 利用 String 构造函数将 char 数组转换为字符串。

**知识点：** System.arraycopy 的使用、避免自己写循环复制数组。

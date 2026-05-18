# 第4章 面向对象编程 — 代码解释

本章涵盖 19 个示例（exp4-1 至 exp4-19），系统介绍 Java 面向对象编程的核心概念：类与对象、封装、方法参数传递、构造器、内部类、继承、多态。

---

## exp4-1 — ClassAndObject.java：类与对象

```java
class EmpInfo{
    String name;
    String designation;
    String department;

    public EmpInfo(String eName, String eDesign, String eDept){
        name = eName;
        designation = eDesign;
        department = eDept;
    }

    void print(){
        System.out.println(name + " is a " + designation + " at " + department + ".");
    }
}

public class ClassAndObject{
    public static void main(String args[]){
        EmpInfo e1 = new EmpInfo("Robert Java", "Manager", "Coffee shop");
        EmpInfo e2 = new EmpInfo("Tom Java", "Worker", "Coffee shop");
        e1.print();
        e2.print();
    }
}
```

**解释：**

- `class EmpInfo` — 定义一个类，包含**字段**（name, designation, department）、**构造方法**和**普通方法**（print）。
- **构造方法** `EmpInfo(String, String, String)`：与类同名、无返回值，用于初始化对象状态，通过 `new` 关键字调用。
- `EmpInfo e1 = new EmpInfo(...)` — 创建对象的过程：
  1. 声明引用变量 `e1`
  2. `new` 在堆上分配内存
  3. 调用构造方法初始化对象
  4. 将对象的引用赋给 `e1`
- 一个 `.java` 文件中可以定义多个 class，但只能有一个 `public class`，且文件名必须与该 public class 同名。

**知识点：** 类的定义、构造方法、对象的创建与使用。

---

## exp4-2 — UseMyDate.java：封装与访问控制

```java
class MyDate {
    private int day;
    private int month;
    private int year;

    public String getDate(){
        return day + "/" + month + "/" + year;
    }

    public int setDate(int a, int b, int c){
        if ((a > 0 && a <= 31) && (b > 0 && b <= 12)){
            day = a;
            month = b;
            year = c;
            return 0;    // 成功
        } else {
            return -1;   // 失败
        }
    }
}

public class UseMyDate{
    public static void main(String[] args){
        MyDate d = new MyDate();
        if (d.setDate(22, 5, 2009) == 0){
            System.out.println(d.getDate());  // 22/5/2009
        }
    }
}
```

**解释：**

- `private` 修饰的字段（day, month, year）**只能在类内部访问**，外部代码不能直接 `d.day = 22`（已注释掉的非法操作）。
- 通过 `public` 方法 `setDate()` 和 `getDate()` 提供受控的访问接口——这就是**封装**（Encapsulation）。
- `setDate` 方法包含**数据校验**，拒绝无效日期（如 day > 31 或 month > 12），返回 -1 表示失败。
- 封装的好处：保护数据完整性、隐藏实现细节、方便未来修改内部实现而不影响外部调用者。

**知识点：** private vs public 访问控制、封装原则、getter/setter 方法模式。

---

## exp4-3 — VarTest.java：变量遮蔽与 this 关键字

```java
public class VarTest{
    private int x = 1;
    private int y = 1;
    private int z = 1;

    void changeVar(int a, int b, int c){
        x = a;             // 直接访问成员变量 x
        int y = b;         // 声明了新的局部变量 y，遮蔽了成员变量 y
        int z = 9;         // 声明了新的局部变量 z，遮蔽了成员变量 z
        System.out.println("In changeVar: x = " + x + " y =" + y + " z =" + z);
        this.z = c;        // 通过 this 访问被遮蔽的成员变量 z
    }

    String getXYZ(){
        return "x = " + x + " y =" + y + " z =" + z;
    }

    public static void main(String args[]){
        VarTest v = new VarTest();
        System.out.println("Before changVar: " + v.getXYZ());  // x=1 y=1 z=1
        v.changeVar(10, 10, 10);
        System.out.println("After changeVar: " + v.getXYZ());  // x=10 y=1 z=10
    }
}
```

**解释：**

- **变量遮蔽（Shadowing）**：当局部变量与成员变量同名时，在方法内直接写变量名访问的是**局部变量**。
- `this` 关键字：代表**当前对象的引用**，`this.z` 明确访问成员变量而非同名的局部变量。
- 执行过程：
  - `x = a`：给成员变量 x 赋值为 10（没有局部变量 x 遮蔽，直接修改成员变量）。
  - `int y = b`：创建了局部变量 y=10，成员变量 y 保持为 1。
  - `int z = 9`：创建了局部变量 z=9，成员变量 z 保持为 1。
  - `this.z = c`：通过 this 将成员变量 z 赋值为 10。
  - 方法结束后局部变量销毁，但成员变量已改变：x=10, y=1, z=10。

**知识点：** 局部变量 vs 成员变量的作用域、变量遮蔽、this 关键字的作用。

---

## exp4-4 — PassTest.java：Java 的参数传递机制

```java
public class PassTest{
    float ptValue;

    // 参数为基本类型
    public void changeInt(int value){
        value = 55;
    }

    // 参数为引用类型，方法内重新指向新对象
    public void changeStr(String value){
        value = new String("different");
    }

    // 参数为引用类型，通过引用修改对象的成员
    public void changeObjValue(PassTest ref){
        ref.ptValue = 99.0f;
    }

    public static void main(String args[]){
        String str;
        int val;
        PassTest pt = new PassTest();

        val = 11;
        pt.changeInt(val);
        System.out.println("Int value is: " + val);    // 11（未变）

        str = new String("Hello");
        pt.changeStr(str);
        System.out.println("Str value is: " + str);    // Hello（未变）

        pt.ptValue = 101.0f;
        pt.changeObjValue(pt);
        System.out.println("Pt value is: " + pt.ptValue);  // 99.0（已变）
    }
}
```

**解释：**

Java 中的参数传递只有一种方式：**按值传递（pass-by-value）**。但根据参数类型不同，行为有微妙差异：

- **基本类型参数**（`changeInt`）：传递的是**值的副本**。`value = 55` 只修改了局部副本，不影响调用处的 `val`。输出仍是 11。

- **引用类型参数，重新赋值**（`changeStr`）：传递的是**引用的副本**。`value = new String("different")` 让局部引用指向了新对象，但调用处 `str` 仍指向原来的 "Hello"。输出仍是 Hello。

- **引用类型参数，修改对象状态**（`changeObjValue`）：传递的是引用的副本，但这个副本也指向**同一个对象**。`ref.ptValue = 99.0f` 通过副本引用修改了对象的内容，调用处的 `pt` 指向的是同一个对象，因此 `pt.ptValue` 变为 99.0。

关键理解：Java 传递的是引用的**值**（副本），而非引用本身。无法在方法内改变调用处引用变量的指向，但可以通过引用副本改变所指向对象的内容。

**知识点：** Java 的值传递机制、基本类型 vs 引用类型参数的行为差异。

---

## exp4-5 — Calculation.java：可变长度参数（varargs）

```java
public class Calculation {
    public float avg(int... nums) {
        int sum = 0;
        for (int x : nums) {
            sum += x;
        }
        return ((float) sum) / nums.length;
    }

    public static void main(String args[]){
        Calculation cal = new Calculation();
        float average1 = cal.avg(10, 20, 30);              // 3个参数
        float average2 = cal.avg(5, 6, 7, 8, 9, 10);       // 6个参数
        System.out.println("The average of 10,20,30 is " + average1);   // 20.0
        System.out.println("The average of 5,6,7,8,9,10 is " + average2); // 7.5
    }
}
```

**解释：**

- `int... nums` — Java 5 引入的**可变长度参数**（varargs），方法可以接受 0 到多个 int 参数。
- 在方法体内，`nums` 被当作 `int[]` 数组使用。
- 优点：调用方无需手动构造数组，直接传入逗号分隔的参数列表即可。
- `(float) sum` — 强制类型转换，确保浮点除法而非整数除法（整数除法会截断小数部分）。
- 注意事项：varargs 必须是方法的**最后一个参数**，一个方法最多只能有一个 varargs 参数。

**知识点：** 可变长度参数语法、varargs 与数组的关系、整数除法与浮点除法。

---

## exp4-6 — TestOverloading.java：方法重载（println 的多态）

```java
public class TestOverloading{
    public static void main(String[] args){
        boolean b = true;
        char c = 'A';
        int i = 100;
        long l = 1000;
        float f = 99.0f;
        double d = 999.0;
        char[] cc = {'A','B','C','D'};
        String s = "abcdefg";
        java.util.Date o = new java.util.Date();

        System.out.println(b);     // println(boolean)
        System.out.println(c);     // println(char)
        System.out.println(i);     // println(int)
        System.out.println(l);     // println(long)
        System.out.println(f);     // println(float)
        System.out.println(d);     // println(double)
        System.out.println();      // println()
        System.out.println(cc);    // println(char[]) — 特殊：打印内容而非地址
        System.out.println(s);     // println(String)
        System.out.println(o);     // println(Object)，自动调用 o.toString()
    }
}
```

**解释：**

- **方法重载（Overloading）**：同一个类中，多个方法**同名**但**参数列表不同**（类型、个数、顺序），Java 编译器根据调用时的实参类型自动选择匹配的方法。
- `System.out.println()` 为每种基本类型和 String、Object、char[] 都提供了重载版本，共约 10 个 overloads。
- 特别说明：`println(char[])` 打印字符数组的**内容**（而非 toString 的 `[C@xxxx`），这是特意设计的重载。
- `println(Object)` 内部会调用参数的 `toString()` 方法，`java.util.Date` 的 toString() 输出日期时间字符串。

**知识点：** 方法重载的概念与规则、println 的多态体现、char[] 的特殊重载。

---

## exp4-7 — MyDate.java：构造方法与 this()

```java
public class MyDate{
    private int day, month, year;

    public MyDate(int day, int month, int year){
        this.day = day;
        this.month = month;
        this.year = year;
    }

    public String tommorrow(){
        this.day = this.day + 1;
        return this.day + "/" + this.month + "/" + this.year;
    }

    public static void main(String[] args){
        MyDate d = new MyDate(12, 4, 2009);
        System.out.println(d.tommorrow());  // 13/4/2009
    }
}
```

**解释：**

- 带参数的构造方法 `MyDate(int day, int month, int year)` 允许在创建对象时直接初始化状态。
- `this.day = day` — 当构造方法参数名与成员变量名相同时，必须用 `this` 区分成员变量和参数。
- `tommorrow()` 方法直接修改了成员变量 `this.day`（加 1），演示了对象状态的可变性。
- 注意此例没有无参构造方法，因此 `new MyDate()` 会编译错误，必须 `new MyDate(12, 4, 2009)`。

**知识点：** 带参构造器、this 区分参数与成员变量、对象状态修改。

---

## exp4-8 — UseDog.java：默认构造方法

```java
class Dog {
    private int weight;

    public Dog(){              // 无参构造方法
        weight = 42;
    }

    public int getWeight(){
        return weight;
    }

    public void setWeight(int newWeight){
        weight = newWeight;
    }
}

public class UseDog{
    public static void main(String[] args){
        Dog d = new Dog();
        System.out.println("The dog's weight is " + d.getWeight());  // 42
    }
}
```

**解释：**

- `public Dog()` 是无参构造方法，体重设为默认值 42。
- 如果类中没有定义任何构造方法，编译器会**自动生成**一个默认无参构造方法（方法体为空）。但一旦类中定义了任何构造方法，编译器就不再自动生成。
- `getWeight()` 和 `setWeight()` 是标准的 getter/setter 方法，提供了对 private 字段的受控访问。

**知识点：** 无参构造器、默认构造器的自动生成规则、getter/setter 模式。

---

## exp4-9 — EmplyeeTest.java：构造方法重载与 this() 调用

```java
class Employee{
    private String name;
    private int salary;

    public Employee(String n, int s){
        name = n;
        salary = s;
    }

    public Employee(String n){
        this(n, 0);          // 调用双参构造器，salary 默认为0
    }

    public Employee(){
        this("Unknown");     // 调用单参构造器，再间接调用双参构造器
    }

    public String getName(){ return name; }
    public int getSalary(){ return salary; }
}

public class EmplyeeTest{
    public static void main(String[] args){
        Employee e = new Employee();
        System.out.println("Name: " + e.getName() + "   Salary: " + e.getSalary());
        // 输出: Name: Unknown   Salary: 0
    }
}
```

**解释：**

- **构造方法重载**：三个构造方法参数列表不同，形成重载。
- **`this(参数)`** — 在构造方法的第一行调用**本类的另一个构造方法**，实现构造方法的**链式调用（constructor chaining）**。
  1. `Employee()` → 调用 `this("Unknown")`
  2. `Employee("Unknown")` → 调用 `this("Unknown", 0)`
  3. `Employee("Unknown", 0)` → 执行实际初始化
- 这样避免了代码重复，所有初始化逻辑集中在参数最全的构造方法中。

**知识点：** 构造方法重载、this() 构造器链式调用、避免代码重复。

---

## exp4-10 — Test.java：private 访问的范围

```java
class Alpha {
    private int iamprivate;

    public Alpha(int i){
        iamprivate = i;
    }

    boolean isEqualTo(Alpha anotherAlpha) {
        if (this.iamprivate == anotherAlpha.iamprivate)  // 可以访问另一个对象的私有成员！
            return true;
        else
            return false;
    }
}

public class Test{
    public static void main(String args[]){
        Alpha aa = new Alpha(10);
        Alpha bb = new Alpha(12);
        if (aa.isEqualTo(bb)){
            System.out.println("equal ");
        } else {
            System.out.println("not equal ");  // 输出: not equal
        }
    }
}
```

**解释：**

- `private` 的访问范围是**类级别**，而非对象级别。
- 在 `Alpha` 类的方法中，不仅可以访问 `this.iamprivate`，还可以直接访问**同一个类的另一个对象**的私有成员 `anotherAlpha.iamprivate`。
- 这是 Java 语言有意设计的选择：封装是为了隐藏实现细节不被外部类干扰，同一类内的不同对象之间不需要互相防范。

**知识点：** private 访问控制在类级别而非对象级别。

---

## exp4-11 — Outer.java：成员内部类（基础）

```java
public class Outer{
    private int size;

    public class Inner{
        public void doStuff(){
            size++;    // 内部类可以直接访问外部类的私有成员
        }
    }

    Inner i = new Inner();

    public void increaseSize(){
        i.doStuff();
    }

    public static void main(String[] a){
        Outer o = new Outer();
        for (int i = 0; i < 4; i++){
            o.increaseSize();
            System.out.println("The value of size : " + o.size);  // 1, 2, 3, 4
        }
    }
}
```

**解释：**

- **成员内部类（Member Inner Class）**：定义在类中、方法外的类。
- 内部类的一个核心特性：**可以直接访问外部类的所有成员**（包括 private 成员）。`Inner.doStuff()` 中直接访问了 `Outer` 的私有字段 `size`。
- 编译器实质生成了 `Outer$Inner.class`，内部类持有对外部类对象的隐含引用。
- `Inner i = new Inner()` — 外部类可以在自己的代码中直接创建内部类对象。
- main 循环调用了 4 次 `increaseSize()`，每次使 size 加 1，输出 1, 2, 3, 4。

**知识点：** 成员内部类的定义、内部类访问外部类的私有成员、编译产物。

---

## exp4-12 — Outer.java：内部类中的变量遮蔽与解决

```java
public class Outer{
    private int size;

    public class Inner{
        private int size;       // 遮蔽外部类的 size

        public void doStuff(int size){
            size++;                     // 访问局部参数 size
            this.size++;                 // 访问内部类的成员 size
            Outer.this.size++;           // 访问外部类的成员 size
            System.out.println("size in Inner.doStuff(): " + size);
            System.out.println("size of the Inner class: " + this.size);
            System.out.println("size of the Outer class:  " + Outer.this.size);
        }
    }

    Inner i = new Inner();

    public void increaseSize(int s){
        i.doStuff(s);
    }

    public static void main(String[] a){
        Outer o = new Outer();
        o.increaseSize(10);
    }
}
```

**解释：**

- 当内部类方法中的局部变量、内部类成员变量、外部类成员变量**三者同名**时，需要用不同方式区分：
  - `size` — 不加限定，访问的是最近作用域的变量（方法的局部参数）。
  - `this.size` — 通过当前对象的 `this`，访问内部类的成员变量。
  - `Outer.this.size` — `Outer.this` 指向包含当前内部类实例的**外部类对象**，`Outer.this.size` 访问外部类的成员变量。
- `Outer.this` 是内部类引用外部类对象的特殊语法。

**知识点：** 内部类中的命名冲突解决、this / Outer.this / 局部变量的区分。

---

## exp4-13 — Outer.java：局部内部类

```java
class Outer{
    private int size = 5;

    public Object makeInner(final int finalLocalVar){
        int LocalVar = 6;

        class Inner{                         // 定义在方法内的局部内部类
            public String toString(){
                return ("#<Inner size=" + size +
                    " finalLocalVar=" + finalLocalVar + ">");
            }
        }
        return new Inner();   // 返回局部内部类的实例（向上转型为 Object）
    }

    public static void main(String[] args){
        Outer outer = new Outer();
        Object obj = outer.makeInner(40);
        System.out.println("The object is " + obj.toString());
        // 输出: #<Inner size=5 finalLocalVar=40>
    }
}
```

**解释：**

- **局部内部类（Local Inner Class）**：定义在方法体内部的类，作用域仅限于该方法内。
- 局部内部类**只能访问方法中声明为 `final` 的局部变量**（或 effectively final 的变量，Java 8+）。`finalLocalVar` 被声明为 final 所以可以访问，`LocalVar` 不是 final 所以不能访问（本例中没有使用它，但若尝试使用会编译错误）。
- 局部内部类可以访问外部类的成员变量（如 `size`），因为它们持有对外部类对象的隐含引用。
- 方法的返回类型是 `Object`，利用了向上转型（Inner 是 Object 的子类），调用方不需要知道 Inner 的具体类型。

**知识点：** 局部内部类的定义与作用域、final 局部变量的访问限制、向上转型。

---

## exp4-14 — TestInner.java：从外部类之外创建内部类对象

```java
class Outer{
    private int size;

    class Inner{
        void doStuff(){
            size++;
            System.out.println("The size value of the Outer class: " + size);
        }
    }
}

public class TestInner{
    public static void main(String[] a){
        Outer out = new Outer();
        Outer.Inner in = out.new Inner();  // 通过外部类实例创建内部类对象
        in.doStuff();  // 输出: The size value of the Outer class: 1
    }
}
```

**解释：**

- 要在**外部类的外部**（另一个类中）创建成员内部类的对象，需要特殊的语法：
  1. 先创建外部类的实例：`Outer out = new Outer()`
  2. 通过外部类实例创建内部类对象：`out.new Inner()`
- 内部类对象的类型表示为 `Outer.Inner`。
- 这是因为每个成员内部类对象都必须**依附于一个外部类对象**存在。

**知识点：** 外部创建内部类对象的语法 `outerInstance.new Inner()`、内部类对外部类实例的依赖。

---

## exp4-15 — TestSuper.java：继承与 super 关键字

```java
class Employee {
    private String name;
    private int salary;

    public Employee(String name, int salary){
        this.name = name;
        this.salary = salary;
    }

    public String getDetails(){
        return "Name: " + name + "\nSalary: " + salary;
    }
}

class Manager extends Employee {
    private String department;

    public Manager(String name, int salary, String department){
        super(name, salary);      // 调用父类构造器
        this.department = department;
    }

    public String getDetails(){
        return super.getDetails() + "\nDepartment: " + department;
        // 调用父类的 getDetails() 方法
    }
}

public class TestSuper{
    public static void main(String[] srgs){
        Manager m = new Manager("TOM", 2000, "Finance");
        System.out.println(m.getDetails());
        // 输出: Name: TOM
        //       Salary: 2000
        //       Department: Finance
    }
}
```

**解释：**

- `class Manager extends Employee` — Manager **继承** Employee，Manager 自动拥有 Employee 的所有字段和方法（但 private 字段不能直接访问，需通过父类的 public 方法访问）。
- `super(name, salary)` — 在子类构造器中用 `super()` 调用**父类的构造器**，必须是构造器的第一条语句。
- `super.getDetails()` — 在子类重写方法中，用 `super.方法名()` 调用父类中被覆盖的方法版本。
- Manager 的 `getDetails()` 覆盖了 Employee 的版本，扩展了功能（增加了部门信息），同时复用了父类的实现。

**知识点：** extends 继承、super() 调用父类构造器、super.方法() 调用父类被覆盖的方法、方法重写。

---

## exp4-16 — Sandwich.java：构造器调用顺序与静态初始化块

```java
class Meal {
    Meal() { System.out.println("Meal()"); }
}
class Bread {
    Bread() { System.out.println("Bread()"); }
}
class Cheese {
    Cheese() { System.out.println("Cheese()"); }
}
class Lettuce {
    Lettuce() { System.out.println("Lettuce()"); }
}
class Lunch extends Meal {
    Lunch() { System.out.println("Lunch()"); }
}
class PortableLunch extends Lunch {
    PortableLunch() { System.out.println("PortableLunch()"); }
}

public class Sandwich extends PortableLunch {
    private Bread b = new Bread();       // 成员对象初始化
    private Cheese c = new Cheese();
    private Lettuce l = new Lettuce();

    public Sandwich() {
        System.out.println("Sandwich()");
    }

    static {
        System.out.println("Static statement");   // 静态初始化块
    }

    public static void main(String[] args) {
        new Sandwich();
    }
}
```

**程序输出顺序：**
```
Static statement
Meal()
Lunch()
PortableLunch()
Bread()
Cheese()
Lettuce()
Sandwich()
```

**解释：**

这是理解 Java 对象**构造顺序**的经典范例。当 `new Sandwich()` 执行时，发生以下顺序：

1. **静态初始化块**（`static { ... }`）：类加载时执行，只执行一次。输出 "Static statement"。
2. **父类构造器**（从最顶层开始）：Sandwich → PortableLunch → Lunch → Meal。从 Meal() 开始向下执行构造器，输出 Meal() → Lunch() → PortableLunch()。
3. **成员变量初始化**（按声明顺序）：Bread() → Cheese() → Lettuce()。
4. **本类构造器体**：Sandwich()。

完整规则：**父类构造器 → 成员初始化（声明顺序）→ 本类构造器体**。静态块优先于这一切。

**知识点：** 继承链的构造器调用顺序、成员初始化的时机、静态初始化块、类加载时机。

---

## exp4-17 — TestOverriding.java：方法重写（覆盖）

```java
class Employee {
    String name;
    int salary;

    public Employee(String name, int salary){
        this.name = name;
        this.salary = salary;
    }

    public String getDetails(){
        return "Name: " + name + "\nSalary: " + salary;
    }
}

class Manager extends Employee {
    private String department;

    public Manager(String name, int salary, String department){
        super(name, salary);
        this.department = department;
    }

    public String getDetails(){
        return "Name: " + name + "\nSalary: " + salary + "\nDepartment: " + department;
    }
}

class Secretary extends Employee {
    public Secretary(String name, int salary){
        super(name, salary);
    }
    // 不重写 getDetails()，使用父类版本
}

public class TestOverriding{
    public static void main(String[] srgs){
        Manager m = new Manager("Tom", 2000, "Finance");
        Secretary s = new Secretary("Mary", 1500);
        System.out.println(m.getDetails());
        // 调用 Manager 的版本（包含 Department）
        System.out.println(s.getDetails());
        // 调用 Employee 的版本（不包含 Department）
    }
}
```

**解释：**

- **方法重写（Overriding）**：子类重新定义父类中已存在的方法，要求方法签名（名称、参数列表）完全相同，返回类型可以是原类型的子类型（协变返回）。
- Manager 重写了 `getDetails()` 以添加部门信息。注意这里直接访问了 `name` 和 `salary`，说明这两个字段不是 private（对比 exp4-15 中它们是 private，必须通过 super.getDetails() 访问）。
- Secretary **没有**重写 `getDetails()`，因此调用时使用继承自父类 Employee 的版本。
- 重写 vs 重载的区别：
  - **重写（Override）**：父子类之间，同名同参数，运行时多态。
  - **重载（Overload）**：同一个类中，同名不同参数，编译时多态。

**知识点：** 方法重写、重写 vs 重载、访问权限对继承的影响。

---

## exp4-18 — Shapes.java：多态（Polymorphism）

```java
import java.util.*;

class Shape {
    void draw() {}
    void erase() {}
}

class Circle extends Shape {
    void draw() { System.out.println("Calling Circle.draw()"); }
    void erase() { System.out.println("Calling Circle.erase()"); }
}

class Square extends Shape {
    void draw() { System.out.println("Calling Square.draw()"); }
    void erase() { System.out.println("Calling Square.erase()"); }
}

class Triangle extends Shape {
    void draw() { System.out.println("Calling Triangle.draw()"); }
    void erase() { System.out.println("Calling Triangle.erase()"); }
}

public class Shapes{
    static void drawOneShape(Shape s){
        s.draw();     // 多态调用：根据实际对象类型选择方法
    }

    static void drawShapes(Shape[] ss){
        for (int i = 0; i < ss.length; i++){
            ss[i].draw();   // 每个元素调用各自类型的 draw()
        }
    }

    public static void main(String[] args) {
        Random rand = new Random();
        Shape[] s = new Shape[9];

        for (int i = 0; i < s.length; i++){
            switch (rand.nextInt(3)) {
                case 0: s[i] = new Circle(); break;
                case 1: s[i] = new Square(); break;
                case 2: s[i] = new Triangle(); break;
            }
        }
        drawShapes(s);  // 随机输出 Circle/Square/Triangle.draw()
    }
}
```

**解释：**

这是多态的经典示例。核心机制：

- **向上转型（Upcasting）**：将子类对象赋给父类引用（`Shape s = new Circle()`），这是安全的，编译器自动完成。
- **动态绑定（Dynamic Binding）**：当通过父类引用调用方法时，JVM 在运行时根据**对象的实际类型**决定调用哪个版本的方法。`ss[i].draw()` 会根据元素实际是 Circle、Square 还是 Triangle 来调用对应的 `draw()`。
- 这使代码具有**可扩展性**：`drawShapes(Shape[])` 方法不需要知道具体图形类型，只要有新的 Shape 子类（如 Pentagon），它也能自动正确调用。
- `Shape` 是一个**基类/父类**，定义了通用的接口（draw/erase），子类各自实现了具体行为。

**知识点：** 多态、向上转型、动态绑定/后期绑定、运行时类型决定方法调用。

---

## exp4-19 — Shapes_2.java：多态的扩展

```java
import java.util.*;

class Shape {
    void draw() {}
    void erase() {}
}

class Circle extends Shape {
    void draw() { System.out.println("Calling Circle.draw()"); }
    void erase() { System.out.println("Calling Circle.erase()"); }
}

class Square extends Shape {
    void draw() { System.out.println("Calling Square.draw()"); }
    void erase() { System.out.println("Calling Square.erase()"); }
}

class Triangle extends Shape {
    void draw() { System.out.println("Calling Triangle.draw()"); }
    void erase() { System.out.println("Calling Triangle.erase()"); }
}

class Pentagon extends Shape {
    void draw() { System.out.println("Calling Pentagon.draw()"); }
    void erase() { System.out.println("Calling Pentagon.erase()"); }
}

public class Shapes_2 {
    static void drawOneShape(Shape s){
        s.draw();
    }

    static void drawShapes(Shape[] ss){
        for (int i = 0; i < ss.length; i++){
            ss[i].draw();
        }
    }

    public static void main(String[] args) {
        Random rand = new Random();
        Shape[] s = new Shape[9];

        for (int i = 0; i < s.length; i++){
            switch (rand.nextInt(4)) {   // 4个选项，新增 Pentagon
                case 0: s[i] = new Circle(); break;
                case 1: s[i] = new Square(); break;
                case 2: s[i] = new Triangle(); break;
                case 3: s[i] = new Pentagon(); break;
            }
        }
        drawShapes(s);
    }
}
```

**解释：**

- 在 exp4-18 的基础上添加了 `Pentagon`（五边形）类。
- 关键的是：`drawShapes()` 和 `drawOneShape()` 方法**不需要任何修改**，它们只依赖于 `Shape` 父类的接口。
- 这是面向对象设计的核心优势——**对扩展开放，对修改关闭**（开放-封闭原则）。添加新功能只需添加新子类，无需修改已有的多态代码。
- `rand.nextInt(4)` 从 3 改为 4，使得 Pentagon 也能被随机创建。

**知识点：** 多态的扩展性、开闭原则（OCP）、代码复用。

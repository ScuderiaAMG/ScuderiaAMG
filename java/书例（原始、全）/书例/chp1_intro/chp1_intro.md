# 第1章 引言 — Java 代码解释

本章仅包含一个示例 `HelloWorld.java`，是 Java 入门的第一个程序。

---

## exp1 — HelloWorld.java

```java
public class HelloWorld{
    public static void main (String args[]){
        System.out.println("Hello World!");
    }
}
```

**解释：**

- `public class HelloWorld` — 声明一个**公共类**，类名 `HelloWorld` 必须与文件名 `HelloWorld.java` 完全一致（大小写敏感）。
- `public static void main(String args[])` — 程序的**入口方法**（main 方法）。Java 虚拟机（JVM）启动时会自动调用这个方法。
  - `public`：任何外部代码都能访问这个方法，JVM 需要从类外部调用它。
  - `static`：静态方法，属于类本身而非类的实例，JVM 无需创建对象即可调用。
  - `void`：main 方法不返回任何值。
  - `String args[]`：命令行参数，以字符串数组形式传入。
- `System.out.println("Hello World!")` — 在控制台打印字符串并换行。
  - `System`：java.lang 包中的系统类。
  - `out`：System 类的静态成员，是一个 `PrintStream` 对象，代表标准输出流。
  - `println`：PrintStream 的方法，打印内容后自动追加换行符。

**知识点：** 类的定义、main 方法签名、标准输出。

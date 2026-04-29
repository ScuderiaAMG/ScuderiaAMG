// 定义一个“学生”类
class Student {
    String name;
    int age;
    double score;

    // 构造方法：用于初始化学生信息
    public Student(String name, int age, double score) {
        this.name = name;
        this.age = age;
        this.score = score;
    }

    // 自定义方法：打印学生状态
    public void displayInfo() {
        System.out.println("--- 学生档案 ---");
        System.out.println("姓名: " + name);
        System.out.println("年龄: " + age);
        System.out.println("成绩: " + score + " 分");
    }
}

// 主类
public class Main {
    public static void main(String[] args) {
        // 创建一个学生对象
        Student s1 = new Student("张三", 20, 92.5);
        
        // 调用对象的方法
        s1.displayInfo();

        // 简单的逻辑判断
        if (s1.score >= 60) {
            System.out.println("结果: 该同学及格了！");
        } else {
            System.out.println("结果: 还需要努力哦。");
        }
    }
}
/**
 * 测试框架演示 - 软件工程
 * 简单的单元测试框架实现
 */
package deep_learning.software_engineering;

import java.lang.reflect.*;
import java.util.*;

public class TestingDemo {

    // ==================== 测试注解 ====================
    @interface Test {}
    @interface BeforeEach {}
    @interface AfterEach {}

    // ==================== 断言类 ====================
    static class Assert {
        public static void assertEquals(Object expected, Object actual) {
            if (!Objects.equals(expected, actual)) {
                throw new AssertionError(
                    String.format("Expected: %s, Actual: %s", expected, actual));
            }
        }

        public static void assertEquals(double expected, double actual, double delta) {
            if (Math.abs(expected - actual) > delta) {
                throw new AssertionError(
                    String.format("Expected: %f, Actual: %f (delta: %f)",
                        expected, actual, delta));
            }
        }

        public static void assertTrue(boolean condition) {
            if (!condition) {
                throw new AssertionError("Expected true, got false");
            }
        }

        public static void assertFalse(boolean condition) {
            if (condition) {
                throw new AssertionError("Expected false, got true");
            }
        }

        public static void assertNull(Object obj) {
            if (obj != null) {
                throw new AssertionError("Expected null, got: " + obj);
            }
        }

        public static void assertNotNull(Object obj) {
            if (obj == null) {
                throw new AssertionError("Expected non-null");
            }
        }

        public static void assertThrows(Class<? extends Throwable> expected, Runnable code) {
            try {
                code.run();
                throw new AssertionError("Expected " + expected.getName() + " to be thrown");
            } catch (Throwable t) {
                if (!expected.isInstance(t)) {
                    throw new AssertionError(
                        String.format("Expected %s, got %s",
                            expected.getName(), t.getClass().getName()));
                }
            }
        }
    }

    // ==================== 测试运行器 ====================
    static class TestRunner {
        public static void runTests(Class<?> testClass) {
            System.out.println("Running tests in: " + testClass.getSimpleName());
            System.out.println("-".repeat(50));

            int passed = 0, failed = 0;
            List<String> failures = new ArrayList<>();

            Object instance = null;
            try {
                instance = testClass.getDeclaredConstructor().newInstance();
            } catch (Exception e) {
                System.err.println("Cannot instantiate test class: " + e.getMessage());
                return;
            }

            // 找到所有测试方法
            for (Method method : testClass.getDeclaredMethods()) {
                if (method.isAnnotationPresent(Test.class)) {
                    try {
                        // 执行 @BeforeEach 方法
                        for (Method m : testClass.getDeclaredMethods()) {
                            if (m.isAnnotationPresent(BeforeEach.class)) {
                                m.invoke(instance);
                            }
                        }

                        // 执行测试方法
                        method.invoke(instance);
                        System.out.println("  ✓ " + method.getName());
                        passed++;

                        // 执行 @AfterEach 方法
                        for (Method m : testClass.getDeclaredMethods()) {
                            if (m.isAnnotationPresent(AfterEach.class)) {
                                m.invoke(instance);
                            }
                        }
                    } catch (InvocationTargetException e) {
                        System.out.println("  ✗ " + method.getName());
                        failures.add(method.getName() + ": " + e.getCause().getMessage());
                        failed++;
                    } catch (Exception e) {
                        System.out.println("  ✗ " + method.getName() + " (error)");
                        failures.add(method.getName() + ": " + e.getMessage());
                        failed++;
                    }
                }
            }

            // 打印结果
            System.out.println("-".repeat(50));
            System.out.printf("Results: %d passed, %d failed, %d total%n",
                passed, failed, passed + failed);

            if (!failures.isEmpty()) {
                System.out.println("\nFailures:");
                for (String failure : failures) {
                    System.out.println("  - " + failure);
                }
            }
            System.out.println();
        }
    }

    // ==================== 被测试的类 ====================
    static class Calculator {
        public int add(int a, int b) {
            return a + b;
        }

        public int subtract(int a, int b) {
            return a - b;
        }

        public int multiply(int a, int b) {
            return a * b;
        }

        public double divide(int a, int b) {
            if (b == 0) {
                throw new ArithmeticException("Division by zero");
            }
            return (double) a / b;
        }
    }

    // ==================== 测试用例 ====================
    static class CalculatorTest {
        private Calculator calc;

        @BeforeEach
        void setUp() {
            calc = new Calculator();
        }

        @Test
        void testAdd() {
            Assert.assertEquals(5, calc.add(2, 3));
            Assert.assertEquals(0, calc.add(-1, 1));
            Assert.assertEquals(-5, calc.add(-2, -3));
        }

        @Test
        void testSubtract() {
            Assert.assertEquals(1, calc.subtract(3, 2));
            Assert.assertEquals(-2, calc.subtract(2, 4));
        }

        @Test
        void testMultiply() {
            Assert.assertEquals(6, calc.multiply(2, 3));
            Assert.assertEquals(0, calc.multiply(5, 0));
            Assert.assertEquals(-6, calc.multiply(-2, 3));
        }

        @Test
        void testDivide() {
            Assert.assertEquals(2.5, calc.divide(5, 2), 0.001);
            Assert.assertEquals(0.0, calc.divide(0, 5), 0.001);
        }

        @Test
        void testDivideByZero() {
            Assert.assertThrows(ArithmeticException.class, () -> {
                calc.divide(5, 0);
            });
        }
    }

    // ==================== 字符串工具测试 ====================
    static class StringUtils {
        public static String reverse(String str) {
            return new StringBuilder(str).reverse().toString();
        }

        public static boolean isPalindrome(String str) {
            String cleaned = str.toLowerCase().replaceAll("[^a-z0-9]", "");
            return cleaned.equals(reverse(cleaned));
        }

        public static int countWords(String str) {
            return str.trim().split("\\s+").length;
        }
    }

    static class StringUtilsTest {
        @Test
        void testReverse() {
            Assert.assertEquals("dcba", StringUtils.reverse("abcd"));
            Assert.assertEquals("", StringUtils.reverse(""));
            Assert.assertEquals("a", StringUtils.reverse("a"));
        }

        @Test
        void testIsPalindrome() {
            Assert.assertTrue(StringUtils.isPalindrome("racecar"));
            Assert.assertTrue(StringUtils.isPalindrome("A man a plan a canal Panama"));
            Assert.assertFalse(StringUtils.isPalindrome("hello"));
        }

        @Test
        void testCountWords() {
            Assert.assertEquals(3, StringUtils.countWords("hello world foo"));
            Assert.assertEquals(1, StringUtils.countWords("hello"));
            Assert.assertEquals(2, StringUtils.countWords("  hello  world  "));
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 单元测试框架演示 ===\n");

        TestRunner.runTests(CalculatorTest.class);
        TestRunner.runTests(StringUtilsTest.class);

        // 演示TDD (测试驱动开发)
        System.out.println("=== TDD 演示 ===\n");
        System.out.println("测试驱动开发 (TDD) 流程:");
        System.out.println("1. 编写失败的测试");
        System.out.println("2. 编写最少代码使测试通过");
        System.out.println("3. 重构代码");
        System.out.println("4. 重复");
    }
}

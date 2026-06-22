/**
 * 设计模式演示 - 软件工程
 * 包含常用的设计模式实现
 */
package deep_learning.software_engineering;

import java.util.*;

public class DesignPatterns {

    // ==================== 单例模式 ====================
    static class Singleton {
        private static Singleton instance;
        private String data;

        private Singleton() {
            this.data = "Singleton Instance";
        }

        public static synchronized Singleton getInstance() {
            if (instance == null) {
                instance = new Singleton();
            }
            return instance;
        }

        public String getData() {
            return data;
        }
    }

    // ==================== 工厂模式 ====================
    interface Shape {
        void draw();
        double area();
    }

    static class Circle implements Shape {
        private double radius;

        public Circle(double radius) {
            this.radius = radius;
        }

        @Override
        public void draw() {
            System.out.println("Drawing Circle with radius " + radius);
        }

        @Override
        public double area() {
            return Math.PI * radius * radius;
        }
    }

    static class Rectangle implements Shape {
        private double width, height;

        public Rectangle(double width, double height) {
            this.width = width;
            this.height = height;
        }

        @Override
        public void draw() {
            System.out.printf("Drawing Rectangle %.1f x %.1f%n", width, height);
        }

        @Override
        public double area() {
            return width * height;
        }
    }

    static class ShapeFactory {
        public static Shape createShape(String type, double... params) {
            switch (type.toLowerCase()) {
                case "circle":
                    return new Circle(params[0]);
                case "rectangle":
                    return new Rectangle(params[0], params[1]);
                default:
                    throw new IllegalArgumentException("Unknown shape: " + type);
            }
        }
    }

    // ==================== 观察者模式 ====================
    interface Observer {
        void update(String message);
    }

    static class Subject {
        private List<Observer> observers = new ArrayList<>();
        private String state;

        public void attach(Observer observer) {
            observers.add(observer);
        }

        public void detach(Observer observer) {
            observers.remove(observer);
        }

        public void setState(String state) {
            this.state = state;
            notifyAllObservers();
        }

        public String getState() {
            return state;
        }

        private void notifyAllObservers() {
            for (Observer observer : observers) {
                observer.update(state);
            }
        }
    }

    static class ConcreteObserver implements Observer {
        private String name;

        public ConcreteObserver(String name) {
            this.name = name;
        }

        @Override
        public void update(String message) {
            System.out.printf("  %s received: %s%n", name, message);
        }
    }

    // ==================== 策略模式 ====================
    interface SortStrategy {
        void sort(int[] array);
        String getName();
    }

    static class BubbleSortStrategy implements SortStrategy {
        @Override
        public void sort(int[] array) {
            int n = array.length;
            for (int i = 0; i < n - 1; i++) {
                for (int j = 0; j < n - i - 1; j++) {
                    if (array[j] > array[j + 1]) {
                        int temp = array[j];
                        array[j] = array[j + 1];
                        array[j + 1] = temp;
                    }
                }
            }
        }

        @Override
        public String getName() {
            return "Bubble Sort";
        }
    }

    static class QuickSortStrategy implements SortStrategy {
        @Override
        public void sort(int[] array) {
            quickSort(array, 0, array.length - 1);
        }

        private void quickSort(int[] arr, int low, int high) {
            if (low < high) {
                int pi = partition(arr, low, high);
                quickSort(arr, low, pi - 1);
                quickSort(arr, pi + 1, high);
            }
        }

        private int partition(int[] arr, int low, int high) {
            int pivot = arr[high];
            int i = low - 1;
            for (int j = low; j < high; j++) {
                if (arr[j] < pivot) {
                    i++;
                    int temp = arr[i];
                    arr[i] = arr[j];
                    arr[j] = temp;
                }
            }
            int temp = arr[i + 1];
            arr[i + 1] = arr[high];
            arr[high] = temp;
            return i + 1;
        }

        @Override
        public String getName() {
            return "Quick Sort";
        }
    }

    static class Sorter {
        private SortStrategy strategy;

        public Sorter(SortStrategy strategy) {
            this.strategy = strategy;
        }

        public void setStrategy(SortStrategy strategy) {
            this.strategy = strategy;
        }

        public void sort(int[] array) {
            System.out.println("Sorting with " + strategy.getName());
            strategy.sort(array);
        }
    }

    // ==================== 建造者模式 ====================
    static class Computer {
        private String cpu;
        private int ram;
        private int storage;
        private String gpu;
        private boolean hasWifi;

        private Computer() {}

        @Override
        public String toString() {
            return String.format("Computer[CPU=%s, RAM=%dGB, Storage=%dGB, GPU=%s, WiFi=%b]",
                cpu, ram, storage, gpu, hasWifi);
        }

        static class Builder {
            private Computer computer = new Computer();

            public Builder cpu(String cpu) {
                computer.cpu = cpu;
                return this;
            }

            public Builder ram(int ram) {
                computer.ram = ram;
                return this;
            }

            public Builder storage(int storage) {
                computer.storage = storage;
                return this;
            }

            public Builder gpu(String gpu) {
                computer.gpu = gpu;
                return this;
            }

            public Builder wifi(boolean hasWifi) {
                computer.hasWifi = hasWifi;
                return this;
            }

            public Computer build() {
                return computer;
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 设计模式演示 ===\n");

        // 单例模式
        System.out.println("1. 单例模式 (Singleton):");
        Singleton s1 = Singleton.getInstance();
        Singleton s2 = Singleton.getInstance();
        System.out.println("  s1 == s2: " + (s1 == s2));
        System.out.println("  Data: " + s1.getData());

        // 工厂模式
        System.out.println("\n2. 工厂模式 (Factory):");
        Shape circle = ShapeFactory.createShape("circle", 5);
        Shape rect = ShapeFactory.createShape("rectangle", 4, 6);
        circle.draw();
        System.out.printf("  Area: %.2f%n", circle.area());
        rect.draw();
        System.out.printf("  Area: %.2f%n", rect.area());

        // 观察者模式
        System.out.println("\n3. 观察者模式 (Observer):");
        Subject subject = new Subject();
        Observer obs1 = new ConcreteObserver("Observer1");
        Observer obs2 = new ConcreteObserver("Observer2");
        subject.attach(obs1);
        subject.attach(obs2);
        subject.setState("State changed to A");
        subject.setState("State changed to B");

        // 策略模式
        System.out.println("\n4. 策略模式 (Strategy):");
        int[] data = {64, 34, 25, 12, 22, 11, 90};
        Sorter sorter = new Sorter(new BubbleSortStrategy());
        int[] arr1 = data.clone();
        sorter.sort(arr1);
        System.out.println("  Result: " + java.util.Arrays.toString(arr1));

        sorter.setStrategy(new QuickSortStrategy());
        int[] arr2 = data.clone();
        sorter.sort(arr2);
        System.out.println("  Result: " + java.util.Arrays.toString(arr2));

        // 建造者模式
        System.out.println("\n5. 建造者模式 (Builder):");
        Computer pc = new Computer.Builder()
            .cpu("Intel i7")
            .ram(16)
            .storage(512)
            .gpu("NVIDIA RTX 3060")
            .wifi(true)
            .build();
        System.out.println("  " + pc);

        Computer laptop = new Computer.Builder()
            .cpu("Apple M1")
            .ram(8)
            .storage(256)
            .gpu("Integrated")
            .wifi(true)
            .build();
        System.out.println("  " + laptop);
    }
}

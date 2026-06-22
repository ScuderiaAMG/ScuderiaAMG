/**
 * 神经元模型演示 - 深度学习基础
 * 展示单个神经元的计算过程
 */
package deep_learning.basics;

import java.util.Arrays;

/**
 * 单个神经元类
 */
class Neuron {
    private double[] weights;
    private double bias;
    private String activationType;

    /**
     * 构造函数
     * @param inputSize 输入维度
     * @param activationType 激活函数类型
     */
    public Neuron(int inputSize, String activationType) {
        this.weights = new double[inputSize];
        this.bias = Math.random() - 0.5;
        this.activationType = activationType;

        // Xavier 初始化
        double limit = Math.sqrt(6.0 / inputSize);
        for (int i = 0; i < inputSize; i++) {
            weights[i] = (Math.random() * 2 - 1) * limit;
        }
    }

    /**
     * 前向传播
     * @param inputs 输入向量
     * @return 神经元输出
     */
    public double forward(double[] inputs) {
        // 加权求和
        double weightedSum = bias;
        for (int i = 0; i < inputs.length; i++) {
            weightedSum += inputs[i] * weights[i];
        }

        // 应用激活函数
        return applyActivation(weightedSum);
    }

    /**
     * 应用激活函数
     */
    private double applyActivation(double x) {
        switch (activationType.toLowerCase()) {
            case "sigmoid":
                return 1.0 / (1.0 + Math.exp(-x));
            case "tanh":
                return Math.tanh(x);
            case "relu":
                return Math.max(0, x);
            case "linear":
            default:
                return x;
        }
    }

    /**
     * 获取加权和 (用于演示)
     */
    public double getWeightedSum(double[] inputs) {
        double sum = bias;
        for (int i = 0; i < inputs.length; i++) {
            sum += inputs[i] * weights[i];
        }
        return sum;
    }

    /**
     * 打印神经元信息
     */
    public void printInfo() {
        System.out.println("Neuron Info:");
        System.out.println("  Activation: " + activationType);
        System.out.println("  Weights: " + Arrays.toString(weights));
        System.out.printf("  Bias: %.4f%n", bias);
    }

    // Getters
    public double[] getWeights() { return weights; }
    public double getBias() { return bias; }
}

public class NeuronDemo {
    public static void main(String[] args) {
        System.out.println("=== 神经元计算演示 ===\n");

        // 创建一个3输入的神经元
        Neuron neuron = new Neuron(3, "sigmoid");
        neuron.printInfo();

        // 测试输入
        double[][] testInputs = {
            {1.0, 0.5, 0.2},
            {0.1, 0.9, 0.3},
            {0.5, 0.5, 0.5}
        };

        System.out.println("\n前向传播结果:");
        System.out.println("-".repeat(50));

        for (double[] input : testInputs) {
            double weightedSum = neuron.getWeightedSum(input);
            double output = neuron.forward(input);

            System.out.printf("输入: %s%n", Arrays.toString(input));
            System.out.printf("加权和: %.4f%n", weightedSum);
            System.out.printf("激活后输出: %.4f%n", output);
            System.out.println("-".repeat(50));
        }

        // 演示不同激活函数的效果
        System.out.println("\n=== 不同激活函数对比 ===\n");

        String[] activations = {"linear", "sigmoid", "tanh", "relu"};
        double[] x = {-2, -1, 0, 1, 2};

        System.out.printf("%-10s", "x");
        for (String act : activations) {
            System.out.printf("%-12s", act);
        }
        System.out.println();
        System.out.println("-".repeat(58));

        for (double val : x) {
            System.out.printf("%-10.1f", val);
            for (String act : activations) {
                Neuron n = new Neuron(1, act);
                double[] input = {val};
                System.out.printf("%-12.4f", n.forward(input));
            }
            System.out.println();
        }
    }
}

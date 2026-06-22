/**
 * 激活函数集合 - 深度学习基础
 * 演示各种常用的激活函数及其导数
 */
package deep_learning.basics;

public class ActivationFunctions {

    /**
     * Sigmoid 函数: f(x) = 1 / (1 + e^(-x))
     * 输出范围: (0, 1)
     * 常用于二分类输出层
     */
    public static double sigmoid(double x) {
        return 1.0 / (1.0 + Math.exp(-x));
    }

    /**
     * Sigmoid 导数: f'(x) = f(x) * (1 - f(x))
     */
    public static double sigmoidDerivative(double x) {
        double s = sigmoid(x);
        return s * (1 - s);
    }

    /**
     * Tanh 函数: f(x) = (e^x - e^(-x)) / (e^x + e^(-x))
     * 输出范围: (-1, 1)
     * 常用于隐藏层
     */
    public static double tanh(double x) {
        return Math.tanh(x);
    }

    /**
     * Tanh 导数: f'(x) = 1 - tanh(x)^2
     */
    public static double tanhDerivative(double x) {
        double t = Math.tanh(x);
        return 1 - t * t;
    }

    /**
     * ReLU 函数: f(x) = max(0, x)
     * 最常用的激活函数
     */
    public static double relu(double x) {
        return Math.max(0, x);
    }

    /**
     * ReLU 导数: f'(x) = 1 if x > 0, else 0
     */
    public static double reluDerivative(double x) {
        return x > 0 ? 1 : 0;
    }

    /**
     * Leaky ReLU 函数: f(x) = x if x > 0, else 0.01 * x
     * 解决 ReLU 的神经元死亡问题
     */
    public static double leakyRelu(double x) {
        return x > 0 ? x : 0.01 * x;
    }

    /**
     * Leaky ReLU 导数
     */
    public static double leakyReluDerivative(double x) {
        return x > 0 ? 1 : 0.01;
    }

    /**
     * Softmax 函数 (用于向量)
     * 常用于多分类输出层
     */
    public static double[] softmax(double[] x) {
        double[] result = new double[x.length];
        double max = Double.NEGATIVE_INFINITY;
        for (double val : x) {
            max = Math.max(max, val);
        }
        double sum = 0;
        for (int i = 0; i < x.length; i++) {
            result[i] = Math.exp(x[i] - max);
            sum += result[i];
        }
        for (int i = 0; i < x.length; i++) {
            result[i] /= sum;
        }
        return result;
    }

    public static void main(String[] args) {
        System.out.println("=== 激活函数演示 ===\n");

        double[] testValues = {-2, -1, 0, 1, 2};

        System.out.println("x\t\tSigmoid\t\tTanh\t\tReLU\t\tLeakyReLU");
        System.out.println("-".repeat(70));

        for (double x : testValues) {
            System.out.printf("%.1f\t\t%.4f\t\t%.4f\t\t%.4f\t\t%.4f%n",
                x, sigmoid(x), tanh(x), relu(x), leakyRelu(x));
        }

        System.out.println("\n=== 激活函数导数 ===\n");
        System.out.println("x\t\tSigmoid'\tTanh'\t\tReLU'\t\tLeakyReLU'");
        System.out.println("-".repeat(70));

        for (double x : testValues) {
            System.out.printf("%.1f\t\t%.4f\t\t%.4f\t\t%.4f\t\t%.4f%n",
                x, sigmoidDerivative(x), tanhDerivative(x),
                reluDerivative(x), leakyReluDerivative(x));
        }

        System.out.println("\n=== Softmax 示例 ===\n");
        double[] logits = {2.0, 1.0, 0.1};
        double[] probs = softmax(logits);
        System.out.print("输入: [");
        for (int i = 0; i < logits.length; i++) {
            System.out.printf("%.1f%s", logits[i], i < logits.length - 1 ? ", " : "");
        }
        System.out.println("]");
        System.out.print("Softmax: [");
        for (int i = 0; i < probs.length; i++) {
            System.out.printf("%.4f%s", probs[i], i < probs.length - 1 ? ", " : "");
        }
        System.out.println("]");
    }
}

/**
 * 感知器 (Perceptron) - 深度学习基础
 * 感知器是最简单的神经网络模型，用于二分类问题
 * 本示例演示感知器的学习过程
 */
package deep_learning.basics;

public class Perceptron {
    private double[] weights;  // 权重数组
    private double bias;       // 偏置
    private double learningRate; // 学习率

    /**
     * 构造函数
     * @param inputSize 输入特征数量
     * @param learningRate 学习率
     */
    public Perceptron(int inputSize, double learningRate) {
        this.weights = new double[inputSize];
        this.bias = 0;
        this.learningRate = learningRate;
        // 随机初始化权重
        for (int i = 0; i < inputSize; i++) {
            weights[i] = Math.random() - 0.5;
        }
    }

    /**
     * 激活函数 (阶跃函数)
     * @param x 输入值
     * @return 1 if x >= 0, else 0
     */
    private int activation(double x) {
        return x >= 0 ? 1 : 0;
    }

    /**
     * 预测
     * @param inputs 输入特征
     * @return 预测结果 (0 或 1)
     */
    public int predict(double[] inputs) {
        double sum = bias;
        for (int i = 0; i < inputs.length; i++) {
            sum += inputs[i] * weights[i];
        }
        return activation(sum);
    }

    /**
     * 训练感知器
     * @param trainingInputs 训练输入数据
     * @param labels 标签
     * @param epochs 训练轮数
     */
    public void train(double[][] trainingInputs, int[] labels, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            int totalErrors = 0;
            for (int i = 0; i < trainingInputs.length; i++) {
                int prediction = predict(trainingInputs[i]);
                int error = labels[i] - prediction;

                // 更新权重和偏置
                if (error != 0) {
                    totalErrors++;
                    for (int j = 0; j < weights.length; j++) {
                        weights[j] += learningRate * error * trainingInputs[i][j];
                    }
                    bias += learningRate * error;
                }
            }
            if (epoch % 100 == 0) {
                System.out.println("Epoch " + epoch + ", Errors: " + totalErrors);
            }
            if (totalErrors == 0) {
                System.out.println("Converged at epoch " + epoch);
                break;
            }
        }
    }

    /**
     * 打印模型参数
     */
    public void printModel() {
        System.out.println("Weights: ");
        for (int i = 0; i < weights.length; i++) {
            System.out.printf("  w%d = %.4f%n", i, weights[i]);
        }
        System.out.printf("Bias: %.4f%n", bias);
    }

    public static void main(String[] args) {
        System.out.println("=== 感知器示例: 学习 AND 逻辑门 ===\n");

        // AND 逻辑门训练数据
        double[][] inputs = {
            {0, 0},
            {0, 1},
            {1, 0},
            {1, 1}
        };
        int[] labels = {0, 0, 0, 1};  // AND 的输出

        // 创建感知器
        Perceptron perceptron = new Perceptron(2, 0.1);

        // 训练
        perceptron.train(inputs, labels, 1000);

        // 测试
        System.out.println("\n测试结果:");
        for (int i = 0; i < inputs.length; i++) {
            int result = perceptron.predict(inputs[i]);
            System.out.printf("%.0f AND %.0f = %d%n",
                inputs[i][0], inputs[i][1], result);
        }

        perceptron.printModel();
    }
}

/**
 * 简单神经网络实现 - 中级深度学习
 * 实现一个支持反向传播的多层神经网络
 */
package deep_learning.intermediate;

import java.util.Random;

public class NeuralNetwork {
    private int[] layerSizes;
    private double[][] neurons;      // 各层神经元输出
    private double[][][] weights;    // 权重矩阵
    private double[][] biases;       // 偏置
    private double[][] deltas;       // 误差项
    private double learningRate;
    private Random random;

    /**
     * 构造函数
     * @param layerSizes 各层神经元数量 [输入层, 隐藏层..., 输出层]
     * @param learningRate 学习率
     */
    public NeuralNetwork(int[] layerSizes, double learningRate) {
        this.layerSizes = layerSizes;
        this.learningRate = learningRate;
        this.random = new Random(42);

        initializeNetwork();
    }

    /**
     * 初始化网络参数
     */
    private void initializeNetwork() {
        int numLayers = layerSizes.length;

        // 初始化神经元数组
        neurons = new double[numLayers][];
        deltas = new double[numLayers][];
        for (int i = 0; i < numLayers; i++) {
            neurons[i] = new double[layerSizes[i]];
            deltas[i] = new double[layerSizes[i]];
        }

        // 初始化权重和偏置 (He初始化)
        weights = new double[numLayers - 1][][];
        biases = new double[numLayers - 1][];

        for (int i = 0; i < numLayers - 1; i++) {
            int fanIn = layerSizes[i];
            int fanOut = layerSizes[i + 1];
            double std = Math.sqrt(2.0 / fanIn);

            weights[i] = new double[fanOut][fanIn];
            biases[i] = new double[fanOut];

            for (int j = 0; j < fanOut; j++) {
                biases[i][j] = 0;
                for (int k = 0; k < fanIn; k++) {
                    weights[i][j][k] = random.nextGaussian() * std;
                }
            }
        }
    }

    /**
     * ReLU 激活函数
     */
    private double relu(double x) {
        return Math.max(0, x);
    }

    /**
     * ReLU 导数
     */
    private double reluDerivative(double x) {
        return x > 0 ? 1 : 0;
    }

    /**
     * Sigmoid 激活函数
     */
    private double sigmoid(double x) {
        return 1.0 / (1.0 + Math.exp(-x));
    }

    /**
     * Sigmoid 导数
     */
    private double sigmoidDerivative(double x) {
        double s = sigmoid(x);
        return s * (1 - s);
    }

    /**
     * 前向传播
     * @param input 输入向量
     * @return 输出向量
     */
    public double[] forward(double[] input) {
        // 设置输入层
        System.arraycopy(input, 0, neurons[0], 0, input.length);

        // 逐层前向传播
        for (int layer = 0; layer < weights.length; layer++) {
            for (int j = 0; j < layerSizes[layer + 1]; j++) {
                double sum = biases[layer][j];
                for (int k = 0; k < layerSizes[layer]; k++) {
                    sum += weights[layer][j][k] * neurons[layer][k];
                }
                // 隐藏层使用ReLU，输出层使用Sigmoid
                if (layer < weights.length - 1) {
                    neurons[layer + 1][j] = relu(sum);
                } else {
                    neurons[layer + 1][j] = sigmoid(sum);
                }
            }
        }

        return neurons[neurons.length - 1].clone();
    }

    /**
     * 反向传播
     * @param target 目标输出
     */
    public void backward(double[] target) {
        int outputLayer = neurons.length - 1;

        // 计算输出层误差
        for (int i = 0; i < layerSizes[outputLayer]; i++) {
            double output = neurons[outputLayer][i];
            deltas[outputLayer][i] = (output - target[i]) *
                sigmoidDerivative(output);
        }

        // 计算隐藏层误差
        for (int layer = outputLayer - 1; layer > 0; layer--) {
            for (int i = 0; i < layerSizes[layer]; i++) {
                double error = 0;
                for (int j = 0; j < layerSizes[layer + 1]; j++) {
                    error += deltas[layer + 1][j] * weights[layer][j][i];
                }
                deltas[layer][i] = error * reluDerivative(neurons[layer][i]);
            }
        }

        // 更新权重和偏置
        for (int layer = 0; layer < weights.length; layer++) {
            for (int j = 0; j < layerSizes[layer + 1]; j++) {
                for (int k = 0; k < layerSizes[layer]; k++) {
                    weights[layer][j][k] -= learningRate *
                        deltas[layer + 1][j] * neurons[layer][k];
                }
                biases[layer][j] -= learningRate * deltas[layer + 1][j];
            }
        }
    }

    /**
     * 计算均方误差
     */
    public double calculateMSE(double[] output, double[] target) {
        double mse = 0;
        for (int i = 0; i < output.length; i++) {
            mse += Math.pow(output[i] - target[i], 2);
        }
        return mse / output.length;
    }

    /**
     * 训练网络
     * @param inputs 训练输入
     * @param targets 训练目标
     * @param epochs 训练轮数
     */
    public void train(double[][] inputs, double[][] targets, int epochs) {
        for (int epoch = 0; epoch < epochs; epoch++) {
            double totalLoss = 0;

            for (int i = 0; i < inputs.length; i++) {
                double[] output = forward(inputs[i]);
                totalLoss += calculateMSE(output, targets[i]);
                backward(targets[i]);
            }

            if (epoch % 100 == 0) {
                System.out.printf("Epoch %d, Loss: %.6f%n",
                    epoch, totalLoss / inputs.length);
            }
        }
    }

    /**
     * 打印网络结构
     */
    public void printStructure() {
        System.out.println("Neural Network Structure:");
        System.out.print("Layers: ");
        for (int i = 0; i < layerSizes.length; i++) {
            System.out.print(layerSizes[i]);
            if (i < layerSizes.length - 1) System.out.print(" -> ");
        }
        System.out.println();

        int totalParams = 0;
        for (int i = 0; i < weights.length; i++) {
            int params = (layerSizes[i] + 1) * layerSizes[i + 1];
            totalParams += params;
            System.out.printf("Layer %d->%d: %d parameters%n",
                i, i + 1, params);
        }
        System.out.println("Total parameters: " + totalParams);
    }

    public static void main(String[] args) {
        System.out.println("=== 多层神经网络演示 ===\n");

        // 创建网络: 2输入 -> 4隐藏 -> 1输出
        NeuralNetwork nn = new NeuralNetwork(new int[]{2, 4, 1}, 0.1);
        nn.printStructure();

        // XOR 问题训练数据
        double[][] inputs = {
            {0, 0}, {0, 1}, {1, 0}, {1, 1}
        };
        double[][] targets = {
            {0}, {1}, {1}, {0}
        };

        System.out.println("\n训练XOR问题:");
        nn.train(inputs, targets, 2000);

        System.out.println("\n测试结果:");
        for (int i = 0; i < inputs.length; i++) {
            double[] output = nn.forward(inputs[i]);
            System.out.printf("%.0f XOR %.0f = %.4f (目标: %.0f)%n",
                inputs[i][0], inputs[i][1], output[0], targets[i][0]);
        }
    }
}

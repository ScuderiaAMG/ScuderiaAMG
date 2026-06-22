/**
 * 循环神经网络 (RNN) 基础实现 - 高级深度学习
 * 演示RNN的基本结构和序列处理
 */
package deep_learning.advanced;

import java.util.Random;

public class RNN {
    private int inputSize;
    private int hiddenSize;
    private int outputSize;

    // 权重矩阵
    private double[][] Wxh;  // 输入到隐藏
    private double[][] Whh;  // 隐藏到隐藏
    private double[][] Why;  // 隐藏到输出
    private double[] bh;     // 隐藏层偏置
    private double[] by;     // 输出层偏置

    private Random random;

    public RNN(int inputSize, int hiddenSize, int outputSize) {
        this.inputSize = inputSize;
        this.hiddenSize = hiddenSize;
        this.outputSize = outputSize;
        this.random = new Random(42);

        initializeWeights();
    }

    private void initializeWeights() {
        double scale = Math.sqrt(2.0 / hiddenSize);

        Wxh = new double[hiddenSize][inputSize];
        Whh = new double[hiddenSize][hiddenSize];
        Why = new double[outputSize][hiddenSize];
        bh = new double[hiddenSize];
        by = new double[outputSize];

        // 随机初始化
        for (int i = 0; i < hiddenSize; i++) {
            for (int j = 0; j < inputSize; j++) {
                Wxh[i][j] = random.nextGaussian() * scale;
            }
            for (int j = 0; j < hiddenSize; j++) {
                Whh[i][j] = random.nextGaussian() * scale;
            }
            bh[i] = 0;
        }

        for (int i = 0; i < outputSize; i++) {
            for (int j = 0; j < hiddenSize; j++) {
                Why[i][j] = random.nextGaussian() * scale;
            }
            by[i] = 0;
        }
    }

    /**
     * Tanh 激活函数
     */
    private double tanh(double x) {
        return Math.tanh(x);
    }

    /**
     * Softmax 函数
     */
    private double[] softmax(double[] x) {
        double[] result = new double[x.length];
        double max = Double.NEGATIVE_INFINITY;
        for (double val : x) max = Math.max(max, val);

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

    /**
     * 前向传播 (单步)
     * @param input 当前输入
     * @param hPrev 前一时刻隐藏状态
     * @return [新的隐藏状态, 输出概率]
     */
    public double[][] forwardStep(double[] input, double[] hPrev) {
        // 计算新的隐藏状态: h = tanh(Wxh * x + Whh * h_prev + bh)
        double[] hNew = new double[hiddenSize];
        for (int i = 0; i < hiddenSize; i++) {
            double sum = bh[i];
            for (int j = 0; j < inputSize; j++) {
                sum += Wxh[i][j] * input[j];
            }
            for (int j = 0; j < hiddenSize; j++) {
                sum += Whh[i][j] * hPrev[j];
            }
            hNew[i] = tanh(sum);
        }

        // 计算输出: y = Why * h + by
        double[] y = new double[outputSize];
        for (int i = 0; i < outputSize; i++) {
            double sum = by[i];
            for (int j = 0; j < hiddenSize; j++) {
                sum += Why[i][j] * hNew[j];
            }
            y[i] = sum;
        }

        // Softmax
        double[] probs = softmax(y);

        return new double[][]{hNew, probs};
    }

    /**
     * 处理整个序列
     * @param inputs 输入序列
     * @return 所有时间步的输出概率
     */
    public double[][] forward(double[][] inputs) {
        double[] h = new double[hiddenSize];  // 初始隐藏状态
        double[][] outputs = new double[inputs.length][outputSize];

        for (int t = 0; t < inputs.length; t++) {
            double[][] result = forwardStep(inputs[t], h);
            h = result[0];
            outputs[t] = result[1];
        }

        return outputs;
    }

    /**
     * 生成序列
     * @param seed 种子输入
     * @param length 生成长度
     * @return 生成的序列
     */
    public int[] generate(double[] seed, int length) {
        int[] sequence = new int[length];
        double[] h = new double[hiddenSize];
        double[] input = seed;

        for (int t = 0; t < length; t++) {
            double[][] result = forwardStep(input, h);
            h = result[0];
            double[] probs = result[1];

            // 采样
            int maxIdx = 0;
            for (int i = 1; i < probs.length; i++) {
                if (probs[i] > probs[maxIdx]) maxIdx = i;
            }
            sequence[t] = maxIdx;

            // 将输出作为下一输入 (one-hot)
            input = new double[outputSize];
            input[maxIdx] = 1;
        }

        return sequence;
    }

    public void printStructure() {
        System.out.println("RNN Structure:");
        System.out.printf("  Input size: %d%n", inputSize);
        System.out.printf("  Hidden size: %d%n", hiddenSize);
        System.out.printf("  Output size: %d%n", outputSize);
        System.out.printf("  Parameters: %d%n",
            (inputSize + hiddenSize) * hiddenSize + hiddenSize +
            outputSize * hiddenSize + outputSize);
    }

    public static void main(String[] args) {
        System.out.println("=== 循环神经网络 (RNN) 演示 ===\n");

        // 创建RNN: 输入3维, 隐藏层10维, 输出5维
        RNN rnn = new RNN(3, 10, 5);
        rnn.printStructure();

        // 模拟序列数据 (4个时间步)
        double[][] sequence = {
            {1, 0, 0},
            {0, 1, 0},
            {0, 0, 1},
            {1, 0, 0}
        };

        System.out.println("\n处理序列:");
        double[][] outputs = rnn.forward(sequence);

        for (int t = 0; t < sequence.length; t++) {
            System.out.printf("时间步 %d: 输入=%s -> 输出概率=%s%n",
                t,
                java.util.Arrays.toString(sequence[t]),
                formatProbs(outputs[t]));
        }

        // 生成序列
        System.out.println("\n生成序列 (从种子开始):");
        double[] seed = {1, 0, 0};
        int[] generated = rnn.generate(seed, 8);
        System.out.print("生成的序列: ");
        for (int idx : generated) {
            System.out.print(idx + " ");
        }
        System.out.println();

        // 展示RNN的时序特性
        System.out.println("\n=== RNN 时序特性演示 ===\n");
        System.out.println("RNN通过隐藏状态 h(t) 传递信息:");
        System.out.println("h(t) = tanh(Wxh * x(t) + Whh * h(t-1) + bh)");
        System.out.println("y(t) = softmax(Why * h(t) + by)");
    }

    private static String formatProbs(double[] probs) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < probs.length; i++) {
            sb.append(String.format("%.3f", probs[i]));
            if (i < probs.length - 1) sb.append(", ");
        }
        sb.append("]");
        return sb.toString();
    }
}

/**
 * 长短期记忆网络 (LSTM) 实现 - 高级深度学习
 * LSTM是RNN的改进版本，解决了长期依赖问题
 */
package deep_learning.advanced;

import java.util.Random;

public class LSTM {
    private int inputSize;
    private int hiddenSize;
    private int outputSize;

    // LSTM门的权重
    private double[][] Wf, Wi, Wo, Wc;  // 遗忘门、输入门、输出门、候选记忆
    private double[][] Uf, Ui, Uo, Uc;  // 隐藏状态权重
    private double[] bf, bi, bo, bc;     // 偏置

    // 输出层权重
    private double[][] Wy;
    private double[] by;

    private Random random;

    public LSTM(int inputSize, int hiddenSize, int outputSize) {
        this.inputSize = inputSize;
        this.hiddenSize = hiddenSize;
        this.outputSize = outputSize;
        this.random = new Random(42);

        initializeWeights();
    }

    private void initializeWeights() {
        double scale = Math.sqrt(2.0 / hiddenSize);

        // 初始化所有权重矩阵
        Wf = randomMatrix(hiddenSize, inputSize, scale);
        Wi = randomMatrix(hiddenSize, inputSize, scale);
        Wo = randomMatrix(hiddenSize, inputSize, scale);
        Wc = randomMatrix(hiddenSize, inputSize, scale);

        Uf = randomMatrix(hiddenSize, hiddenSize, scale);
        Ui = randomMatrix(hiddenSize, hiddenSize, scale);
        Uo = randomMatrix(hiddenSize, hiddenSize, scale);
        Uc = randomMatrix(hiddenSize, hiddenSize, scale);

        bf = new double[hiddenSize];
        bi = new double[hiddenSize];
        bo = new double[hiddenSize];
        bc = new double[hiddenSize];

        // 初始化遗忘门偏置为1 (帮助学习长期依赖)
        java.util.Arrays.fill(bf, 1.0);

        Wy = randomMatrix(outputSize, hiddenSize, scale);
        by = new double[outputSize];
    }

    private double[][] randomMatrix(int rows, int cols, double scale) {
        double[][] matrix = new double[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = random.nextGaussian() * scale;
            }
        }
        return matrix;
    }

    private double sigmoid(double x) {
        return 1.0 / (1.0 + Math.exp(-x));
    }

    private double tanh(double x) {
        return Math.tanh(x);
    }

    /**
     * LSTM前向传播单步
     * @param x 当前输入
     * @param hPrev 前一隐藏状态
     * @param cPrev 前一细胞状态
     * @return [hNew, cNew, output]
     */
    public double[][] forwardStep(double[] x, double[] hPrev, double[] cPrev) {
        // 遗忘门: f = sigmoid(Wf * x + Uf * hPrev + bf)
        double[] f = new double[hiddenSize];
        for (int i = 0; i < hiddenSize; i++) {
            double sum = bf[i];
            for (int j = 0; j < inputSize; j++) sum += Wf[i][j] * x[j];
            for (int j = 0; j < hiddenSize; j++) sum += Uf[i][j] * hPrev[j];
            f[i] = sigmoid(sum);
        }

        // 输入门: i = sigmoid(Wi * x + Ui * hPrev + bi)
        double[] inputGate = new double[hiddenSize];
        for (int i = 0; i < hiddenSize; i++) {
            double sum = bi[i];
            for (int j = 0; j < inputSize; j++) sum += Wi[i][j] * x[j];
            for (int j = 0; j < hiddenSize; j++) sum += Ui[i][j] * hPrev[j];
            inputGate[i] = sigmoid(sum);
        }

        // 候选记忆: c~ = tanh(Wc * x + Uc * hPrev + bc)
        double[] cTilde = new double[hiddenSize];
        for (int i = 0; i < hiddenSize; i++) {
            double sum = bc[i];
            for (int j = 0; j < inputSize; j++) sum += Wc[i][j] * x[j];
            for (int j = 0; j < hiddenSize; j++) sum += Uc[i][j] * hPrev[j];
            cTilde[i] = tanh(sum);
        }

        // 输出门: o = sigmoid(Wo * x + Uo * hPrev + bo)
        double[] outputGate = new double[hiddenSize];
        for (int i = 0; i < hiddenSize; i++) {
            double sum = bo[i];
            for (int j = 0; j < inputSize; j++) sum += Wo[i][j] * x[j];
            for (int j = 0; j < hiddenSize; j++) sum += Uo[i][j] * hPrev[j];
            outputGate[i] = sigmoid(sum);
        }

        // 新细胞状态: c = f * cPrev + i * c~
        double[] cNew = new double[hiddenSize];
        for (int i = 0; i < hiddenSize; i++) {
            cNew[i] = f[i] * cPrev[i] + inputGate[i] * cTilde[i];
        }

        // 新隐藏状态: h = o * tanh(c)
        double[] hNew = new double[hiddenSize];
        for (int i = 0; i < hiddenSize; i++) {
            hNew[i] = outputGate[i] * tanh(cNew[i]);
        }

        // 输出层
        double[] y = new double[outputSize];
        for (int i = 0; i < outputSize; i++) {
            double sum = by[i];
            for (int j = 0; j < hiddenSize; j++) sum += Wy[i][j] * hNew[j];
            y[i] = sum;
        }

        // Softmax
        double[] probs = softmax(y);

        return new double[][]{hNew, cNew, probs};
    }

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
     * 处理整个序列
     */
    public double[][] forward(double[][] inputs) {
        double[] h = new double[hiddenSize];
        double[] c = new double[hiddenSize];
        double[][] outputs = new double[inputs.length][outputSize];

        for (int t = 0; t < inputs.length; t++) {
            double[][] result = forwardStep(inputs[t], h, c);
            h = result[0];
            c = result[1];
            outputs[t] = result[2];
        }

        return outputs;
    }

    public void printStructure() {
        System.out.println("LSTM Structure:");
        System.out.printf("  Input size: %d%n", inputSize);
        System.out.printf("  Hidden size: %d%n", hiddenSize);
        System.out.printf("  Output size: %d%n", outputSize);

        int lstmParams = 4 * ((inputSize + 1) * hiddenSize + (hiddenSize + 1) * hiddenSize);
        int outputParams = (hiddenSize + 1) * outputSize;
        System.out.printf("  LSTM parameters: %d%n", lstmParams);
        System.out.printf("  Output parameters: %d%n", outputParams);
        System.out.printf("  Total parameters: %d%n", lstmParams + outputParams);
    }

    public static void main(String[] args) {
        System.out.println("=== LSTM 网络演示 ===\n");

        // 创建LSTM
        LSTM lstm = new LSTM(3, 16, 5);
        lstm.printStructure();

        // 序列数据
        double[][] sequence = {
            {1, 0, 0},
            {0, 1, 0},
            {0, 0, 1},
            {1, 0, 0},
            {0, 1, 0}
        };

        System.out.println("\n处理序列:");
        double[][] outputs = lstm.forward(sequence);

        for (int t = 0; t < sequence.length; t++) {
            System.out.printf("t=%d: 输入=%s -> 输出=%s%n",
                t,
                java.util.Arrays.toString(sequence[t]),
                formatProbs(outputs[t]));
        }

        // 展示LSTM的优势
        System.out.println("\n=== LSTM vs RNN ===\n");
        System.out.println("LSTM的关键创新:");
        System.out.println("1. 遗忘门 (Forget Gate): 决定丢弃哪些信息");
        System.out.println("2. 输入门 (Input Gate): 决定存储哪些新信息");
        System.out.println("3. 输出门 (Output Gate): 决定输出哪些信息");
        System.out.println("4. 细胞状态 (Cell State): 长期记忆的载体");
        System.out.println("\n这使得LSTM能够学习长期依赖关系");
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

/**
 * 线性回归实现 - 机器学习
 * 使用梯度下降法训练线性回归模型
 */
package deep_learning.machine_learning;

public class LinearRegression {
    private double[] weights;
    private double bias;
    private double learningRate;
    private int epochs;

    public LinearRegression(double learningRate, int epochs) {
        this.learningRate = learningRate;
        this.epochs = epochs;
    }

    /**
     * 训练模型
     * @param X 特征矩阵 [n_samples][n_features]
     * @param y 目标值
     */
    public void fit(double[][] X, double[] y) {
        int n = X.length;
        int m = X[0].length;

        weights = new double[m];
        bias = 0;

        // 梯度下降
        for (int epoch = 0; epoch < epochs; epoch++) {
            double[] predictions = predict(X);

            // 计算梯度
            double[] dw = new double[m];
            double db = 0;

            for (int i = 0; i < n; i++) {
                double error = predictions[i] - y[i];
                for (int j = 0; j < m; j++) {
                    dw[j] += error * X[i][j];
                }
                db += error;
            }

            // 更新参数
            for (int j = 0; j < m; j++) {
                weights[j] -= learningRate * dw[j] / n;
            }
            bias -= learningRate * db / n;

            // 打印损失
            if (epoch % 100 == 0) {
                double mse = calculateMSE(predictions, y);
                System.out.printf("Epoch %d, MSE: %.6f%n", epoch, mse);
            }
        }
    }

    /**
     * 预测
     */
    public double[] predict(double[][] X) {
        double[] predictions = new double[X.length];
        for (int i = 0; i < X.length; i++) {
            double sum = bias;
            for (int j = 0; j < X[i].length; j++) {
                sum += weights[j] * X[i][j];
            }
            predictions[i] = sum;
        }
        return predictions;
    }

    /**
     * 计算均方误差
     */
    private double calculateMSE(double[] predicted, double[] actual) {
        double sum = 0;
        for (int i = 0; i < predicted.length; i++) {
            sum += Math.pow(predicted[i] - actual[i], 2);
        }
        return sum / predicted.length;
    }

    /**
     * 计算R²分数
     */
    public double r2Score(double[][] X, double[] y) {
        double[] predictions = predict(X);
        double meanY = 0;
        for (double val : y) meanY += val;
        meanY /= y.length;

        double ssRes = 0, ssTot = 0;
        for (int i = 0; i < y.length; i++) {
            ssRes += Math.pow(y[i] - predictions[i], 2);
            ssTot += Math.pow(y[i] - meanY, 2);
        }

        return 1 - ssRes / ssTot;
    }

    /**
     * 打印模型参数
     */
    public void printModel() {
        System.out.println("\n模型参数:");
        for (int i = 0; i < weights.length; i++) {
            System.out.printf("  w%d = %.4f%n", i, weights[i]);
        }
        System.out.printf("  bias = %.4f%n", bias);
    }

    public static void main(String[] args) {
        System.out.println("=== 线性回归演示 ===\n");

        // 生成示例数据: y = 2*x1 + 3*x2 + 1 + noise
        int n = 100;
        double[][] X = new double[n][2];
        double[] y = new double[n];

        java.util.Random rand = new java.util.Random(42);
        for (int i = 0; i < n; i++) {
            X[i][0] = rand.nextDouble() * 10;
            X[i][1] = rand.nextDouble() * 10;
            y[i] = 2 * X[i][0] + 3 * X[i][1] + 1 + rand.nextGaussian();
        }

        // 训练模型
        LinearRegression model = new LinearRegression(0.01, 1000);
        model.fit(X, y);

        // 评估
        model.printModel();
        System.out.printf("R² Score: %.4f%n", model.r2Score(X, y));

        // 预测示例
        System.out.println("\n预测示例:");
        double[][] testX = {{5, 3}, {2, 8}, {7, 1}};
        double[] predictions = model.predict(testX);
        for (int i = 0; i < testX.length; i++) {
            System.out.printf("  x=[%.0f, %.0f] -> y=%.2f (真实: %.2f)%n",
                testX[i][0], testX[i][1], predictions[i],
                2 * testX[i][0] + 3 * testX[i][1] + 1);
        }
    }
}

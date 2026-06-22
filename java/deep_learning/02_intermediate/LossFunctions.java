/**
 * 损失函数集合 - 中级深度学习
 * 演示各种常用的损失函数
 */
package deep_learning.intermediate;

public class LossFunctions {

    /**
     * 均方误差 (MSE) - 回归问题
     * MSE = (1/n) * Σ(y_pred - y_true)^2
     */
    public static double mse(double[] predicted, double[] actual) {
        double sum = 0;
        for (int i = 0; i < predicted.length; i++) {
            sum += Math.pow(predicted[i] - actual[i], 2);
        }
        return sum / predicted.length;
    }

    /**
     * MSE 导数
     */
    public static double[] mseDerivative(double[] predicted, double[] actual) {
        double[] grad = new double[predicted.length];
        for (int i = 0; i < predicted.length; i++) {
            grad[i] = 2 * (predicted[i] - actual[i]) / predicted.length;
        }
        return grad;
    }

    /**
     * 平均绝对误差 (MAE) - 回归问题
     * MAE = (1/n) * Σ|y_pred - y_true|
     */
    public static double mae(double[] predicted, double[] actual) {
        double sum = 0;
        for (int i = 0; i < predicted.length; i++) {
            sum += Math.abs(predicted[i] - actual[i]);
        }
        return sum / predicted.length;
    }

    /**
     * 交叉熵损失 - 二分类问题
     * BCE = -(1/n) * Σ[y*log(p) + (1-y)*log(1-p)]
     */
    public static double binaryCrossEntropy(double[] predicted, double[] actual) {
        double sum = 0;
        double epsilon = 1e-15;  // 防止log(0)
        for (int i = 0; i < predicted.length; i++) {
            double p = Math.max(epsilon, Math.min(1 - epsilon, predicted[i]));
            sum += actual[i] * Math.log(p) + (1 - actual[i]) * Math.log(1 - p);
        }
        return -sum / predicted.length;
    }

    /**
     * 分类交叉熵 - 多分类问题
     * CE = -(1/n) * Σ Σ y_c * log(p_c)
     */
    public static double categoricalCrossEntropy(double[][] predicted, double[][] actual) {
        double sum = 0;
        double epsilon = 1e-15;
        for (int i = 0; i < predicted.length; i++) {
            for (int j = 0; j < predicted[i].length; j++) {
                double p = Math.max(epsilon, predicted[i][j]);
                sum += actual[i][j] * Math.log(p);
            }
        }
        return -sum / predicted.length;
    }

    /**
     * Huber 损失 - 结合 MSE 和 MAE
     */
    public static double huberLoss(double[] predicted, double[] actual, double delta) {
        double sum = 0;
        for (int i = 0; i < predicted.length; i++) {
            double diff = Math.abs(predicted[i] - actual[i]);
            if (diff <= delta) {
                sum += 0.5 * diff * diff;
            } else {
                sum += delta * diff - 0.5 * delta * delta;
            }
        }
        return sum / predicted.length;
    }

    public static void main(String[] args) {
        System.out.println("=== 损失函数演示 ===\n");

        // 回归示例
        double[] predicted = {2.5, 0.0, 2.0, 8.0};
        double[] actual = {3.0, -0.5, 2.0, 7.0};

        System.out.println("回归问题:");
        System.out.println("预测值: " + java.util.Arrays.toString(predicted));
        System.out.println("实际值: " + java.util.Arrays.toString(actual));
        System.out.printf("MSE: %.4f%n", mse(predicted, actual));
        System.out.printf("MAE: %.4f%n", mae(predicted, actual));
        System.out.printf("Huber Loss (δ=1.0): %.4f%n", huberLoss(predicted, actual, 1.0));

        // 二分类示例
        System.out.println("\n二分类问题:");
        double[] predBinary = {0.9, 0.1, 0.8, 0.3};
        double[] actualBinary = {1, 0, 1, 0};
        System.out.println("预测概率: " + java.util.Arrays.toString(predBinary));
        System.out.println("实际标签: " + java.util.Arrays.toString(actualBinary));
        System.out.printf("Binary Cross Entropy: %.4f%n",
            binaryCrossEntropy(predBinary, actualBinary));

        // 多分类示例
        System.out.println("\n多分类问题 (3类):");
        double[][] predMulti = {
            {0.7, 0.2, 0.1},
            {0.1, 0.8, 0.1},
            {0.2, 0.3, 0.5}
        };
        double[][] actualMulti = {
            {1, 0, 0},
            {0, 1, 0},
            {0, 0, 1}
        };
        System.out.printf("Categorical Cross Entropy: %.4f%n",
            categoricalCrossEntropy(predMulti, actualMulti));

        // MSE 梯度演示
        System.out.println("\nMSE 梯度:");
        double[] grad = mseDerivative(predicted, actual);
        System.out.println("梯度: " + java.util.Arrays.toString(grad));
    }
}

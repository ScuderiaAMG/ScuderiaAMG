/**
 * 反向传播算法详细演示 - 中级深度学习
 * 展示反向传播的数学原理和计算过程
 */
package deep_learning.intermediate;

public class BackpropagationDemo {

    /**
     * 简单的两层网络用于演示反向传播
     */
    static class SimpleNetwork {
        // 第一层权重和偏置
        double w1, w2, w3, w4, b1, b2;
        // 第二层权重和偏置
        double w5, w6, b3;

        double learningRate = 0.5;

        public SimpleNetwork() {
            // 初始化权重
            w1 = 0.15; w2 = 0.20; w3 = 0.25; w4 = 0.30;
            w5 = 0.40; w6 = 0.45;
            b1 = 0.35; b2 = 0.35; b3 = 0.60;
        }

        /**
         * Sigmoid 激活函数
         */
        double sigmoid(double x) {
            return 1.0 / (1.0 + Math.exp(-x));
        }

        /**
         * 前向传播 (带中间结果保存)
         */
        double[] forward(double i1, double i2) {
            // 隐藏层
            double h1_input = w1 * i1 + w2 * i2 + b1;
            double h1_output = sigmoid(h1_input);

            double h2_input = w3 * i1 + w4 * i2 + b2;
            double h2_output = sigmoid(h2_input);

            // 输出层
            double o1_input = w5 * h1_output + w6 * h2_output + b3;
            double o1_output = sigmoid(o1_input);

            return new double[]{h1_input, h1_output, h2_input, h2_output,
                               o1_input, o1_output};
        }

        /**
         * 反向传播详细过程
         */
        void trainStep(double i1, double i2, double target) {
            System.out.println("=== 反向传播详细过程 ===");
            System.out.printf("输入: i1=%.1f, i2=%.1f, 目标输出: %.1f%n%n", i1, i2, target);

            // 前向传播
            double[] results = forward(i1, i2);
            double h1_in = results[0], h1_out = results[1];
            double h2_in = results[2], h2_out = results[3];
            double o1_in = results[4], o1_out = results[5];

            System.out.println("【前向传播】");
            System.out.printf("隐藏层 h1: input=%.4f, output=%.4f%n", h1_in, h1_out);
            System.out.printf("隐藏层 h2: input=%.4f, output=%.4f%n", h2_in, h2_out);
            System.out.printf("输出层 o1: input=%.4f, output=%.4f%n%n", o1_in, o1_out);

            // 计算损失 (MSE)
            double loss = 0.5 * Math.pow(target - o1_out, 2);
            System.out.printf("损失 (MSE): %.6f%n%n", loss);

            // 反向传播
            System.out.println("【反向传播】");

            // 输出层梯度
            double dL_do1 = o1_out - target;
            double do1_dnet1 = o1_out * (1 - o1_out);
            double dL_dnet1 = dL_do1 * do1_dnet1;

            System.out.printf("∂L/∂o1 = %.4f%n", dL_do1);
            System.out.printf("∂o1/∂net1 = %.4f%n", do1_dnet1);
            System.out.printf("∂L/∂net1 = %.4f%n%n", dL_dnet1);

            // 更新 w5, w6, b3
            double dw5 = dL_dnet1 * h1_out;
            double dw6 = dL_dnet1 * h2_out;
            double db3 = dL_dnet1;

            System.out.printf("∂L/∂w5 = %.4f, 更新: %.4f -> %.4f%n",
                dw5, w5, w5 - learningRate * dw5);
            System.out.printf("∂L/∂w6 = %.4f, 更新: %.4f -> %.4f%n",
                dw6, w6, w6 - learningRate * dw6);
            System.out.printf("∂L/∂b3 = %.4f, 更新: %.4f -> %.4f%n%n",
                db3, b3, b3 - learningRate * db3);

            // 隐藏层梯度
            double dL_dh1 = dL_dnet1 * w5;
            double dL_dh2 = dL_dnet1 * w6;

            double dh1_dnet_h1 = h1_out * (1 - h1_out);
            double dh2_dnet_h2 = h2_out * (1 - h2_out);

            double dL_dnet_h1 = dL_dh1 * dh1_dnet_h1;
            double dL_dnet_h2 = dL_dh2 * dh2_dnet_h2;

            // 更新 w1-w4, b1, b2
            double dw1 = dL_dnet_h1 * i1;
            double dw2 = dL_dnet_h1 * i2;
            double dw3 = dL_dnet_h2 * i1;
            double dw4 = dL_dnet_h2 * i2;
            double db1 = dL_dnet_h1;
            double db2 = dL_dnet_h2;

            System.out.println("隐藏层梯度:");
            System.out.printf("∂L/∂w1 = %.4f, 更新: %.4f -> %.4f%n", dw1, w1, w1 - learningRate * dw1);
            System.out.printf("∂L/∂w2 = %.4f, 更新: %.4f -> %.4f%n", dw2, w2, w2 - learningRate * dw2);
            System.out.printf("∂L/∂w3 = %.4f, 更新: %.4f -> %.4f%n", dw3, w3, w3 - learningRate * dw3);
            System.out.printf("∂L/∂w4 = %.4f, 更新: %.4f -> %.4f%n", dw4, w4, w4 - learningRate * dw4);
            System.out.printf("∂L/∂b1 = %.4f, 更新: %.4f -> %.4f%n", db1, b1, b1 - learningRate * db1);
            System.out.printf("∂L/∂b2 = %.4f, 更新: %.4f -> %.4f%n%n", db2, b2, b2 - learningRate * db2);

            // 应用更新
            w1 -= learningRate * dw1;
            w2 -= learningRate * dw2;
            w3 -= learningRate * dw3;
            w4 -= learningRate * dw4;
            w5 -= learningRate * dw5;
            w6 -= learningRate * dw6;
            b1 -= learningRate * db1;
            b2 -= learningRate * db2;
            b3 -= learningRate * db3;

            System.out.println("权重已更新！");
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 反向传播算法详细演示 ===\n");

        SimpleNetwork net = new SimpleNetwork();

        // 训练一步
        net.trainStep(0.05, 0.10, 0.01);

        System.out.println("\n训练后的预测:");
        double[] result = net.forward(0.05, 0.10);
        System.out.printf("输入 (0.05, 0.10) -> 输出: %.6f (目标: 0.01)%n", result[5]);
    }
}

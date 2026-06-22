/**
 * 梯度下降算法 - 数学与优化
 * 演示各种梯度下降变体
 */
package deep_learning.math_and_optimization;

import java.util.function.*;

public class GradientDescent {

    /**
     * 基础梯度下降
     * @param f 目标函数
     * @param gradient 梯度函数
     * @param x0 初始点
     * @param learningRate 学习率
     * @param iterations 迭代次数
     * @return 最优解
     */
    public static double[] basicGD(Function<double[], Double> f,
                                   Function<double[], double[]> gradient,
                                   double[] x0, double learningRate,
                                   int iterations) {
        double[] x = x0.clone();

        for (int i = 0; i < iterations; i++) {
            double[] grad = gradient.apply(x);
            for (int j = 0; j < x.length; j++) {
                x[j] -= learningRate * grad[j];
            }

            if (i % 100 == 0) {
                System.out.printf("Iteration %d: f(x) = %.6f%n", i, f.apply(x));
            }
        }

        return x;
    }

    /**
     * 动量梯度下降
     */
    public static double[] momentumGD(Function<double[], Double> f,
                                       Function<double[], double[]> gradient,
                                       double[] x0, double learningRate,
                                       double momentum, int iterations) {
        double[] x = x0.clone();
        double[] velocity = new double[x.length];

        for (int i = 0; i < iterations; i++) {
            double[] grad = gradient.apply(x);
            for (int j = 0; j < x.length; j++) {
                velocity[j] = momentum * velocity[j] - learningRate * grad[j];
                x[j] += velocity[j];
            }

            if (i % 100 == 0) {
                System.out.printf("Iteration %d: f(x) = %.6f%n", i, f.apply(x));
            }
        }

        return x;
    }

    /**
     * AdaGrad
     */
    public static double[] adaGrad(Function<double[], Double> f,
                                    Function<double[], double[]> gradient,
                                    double[] x0, double learningRate,
                                    int iterations) {
        double[] x = x0.clone();
        double[] gradSumSq = new double[x.length];
        double epsilon = 1e-8;

        for (int i = 0; i < iterations; i++) {
            double[] grad = gradient.apply(x);
            for (int j = 0; j < x.length; j++) {
                gradSumSq[j] += grad[j] * grad[j];
                x[j] -= learningRate * grad[j] / (Math.sqrt(gradSumSq[j]) + epsilon);
            }

            if (i % 100 == 0) {
                System.out.printf("Iteration %d: f(x) = %.6f%n", i, f.apply(x));
            }
        }

        return x;
    }

    /**
     * Adam 优化器
     */
    public static double[] adam(Function<double[], Double> f,
                                Function<double[], double[]> gradient,
                                double[] x0, double learningRate,
                                double beta1, double beta2,
                                int iterations) {
        double[] x = x0.clone();
        double[] m = new double[x.length];  // 一阶矩
        double[] v = new double[x.length];  // 二阶矩
        double epsilon = 1e-8;

        for (int i = 1; i <= iterations; i++) {
            double[] grad = gradient.apply(x);
            for (int j = 0; j < x.length; j++) {
                m[j] = beta1 * m[j] + (1 - beta1) * grad[j];
                v[j] = beta2 * v[j] + (1 - beta2) * grad[j] * grad[j];

                double mHat = m[j] / (1 - Math.pow(beta1, i));
                double vHat = v[j] / (1 - Math.pow(beta2, i));

                x[j] -= learningRate * mHat / (Math.sqrt(vHat) + epsilon);
            }

            if (i % 100 == 0) {
                System.out.printf("Iteration %d: f(x) = %.6f%n", i, f.apply(x));
            }
        }

        return x;
    }

    public static void main(String[] args) {
        System.out.println("=== 梯度下降算法演示 ===\n");

        // 目标函数: f(x,y) = (x-3)^2 + (y-2)^2
        // 最小值在 (3, 2)
        Function<double[], Double> f = x ->
            Math.pow(x[0] - 3, 2) + Math.pow(x[1] - 2, 2);

        Function<double[], double[]> gradient = x ->
            new double[]{2 * (x[0] - 3), 2 * (x[1] - 2)};

        double[] x0 = {0, 0};

        // 基础梯度下降
        System.out.println("1. 基础梯度下降:");
        double[] result1 = basicGD(f, gradient, x0, 0.1, 500);
        System.out.printf("结果: (%.4f, %.4f)%n%n", result1[0], result1[1]);

        // 动量梯度下降
        System.out.println("2. 动量梯度下降:");
        double[] result2 = momentumGD(f, gradient, x0, 0.1, 0.9, 500);
        System.out.printf("结果: (%.4f, %.4f)%n%n", result2[0], result2[1]);

        // AdaGrad
        System.out.println("3. AdaGrad:");
        double[] result3 = adaGrad(f, gradient, x0, 1.0, 500);
        System.out.printf("结果: (%.4f, %.4f)%n%n", result3[0], result3[1]);

        // Adam
        System.out.println("4. Adam:");
        double[] result4 = adam(f, gradient, x0, 0.1, 0.9, 0.999, 500);
        System.out.printf("结果: (%.4f, %.4f)%n%n", result4[0], result4[1]);

        // 优化器比较
        System.out.println("=== 优化器特点比较 ===\n");
        System.out.println("SGD: 简单但可能震荡，需要调学习率");
        System.out.println("Momentum: 加入动量，减少震荡");
        System.out.println("AdaGrad: 自适应学习率，适合稀疏梯度");
        System.out.println("Adam: 结合Momentum和RMSProp，最常用");
    }
}

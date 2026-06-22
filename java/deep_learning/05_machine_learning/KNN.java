/**
 * K近邻算法 (KNN) 实现 - 机器学习
 * 简单而有效的分类算法
 */
package deep_learning.machine_learning;

import java.util.*;

public class KNN {
    private int k;
    private double[][] XTrain;
    private int[] yTrain;

    public KNN(int k) {
        this.k = k;
    }

    /**
     * 训练 (存储训练数据)
     */
    public void fit(double[][] X, int[] y) {
        this.XTrain = X;
        this.yTrain = y;
    }

    /**
     * 计算欧氏距离
     */
    private double euclideanDistance(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            sum += Math.pow(a[i] - b[i], 2);
        }
        return Math.sqrt(sum);
    }

    /**
     * 预测单个样本
     */
    public int predict(double[] x) {
        // 计算与所有训练样本的距离
        double[][] distances = new double[XTrain.length][2];
        for (int i = 0; i < XTrain.length; i++) {
            distances[i][0] = euclideanDistance(x, XTrain[i]);
            distances[i][1] = yTrain[i];
        }

        // 按距离排序
        Arrays.sort(distances, (a, b) -> Double.compare(a[0], b[0]));

        // 统计k个最近邻的类别
        Map<Integer, Integer> classCounts = new HashMap<>();
        for (int i = 0; i < k; i++) {
            int label = (int) distances[i][1];
            classCounts.put(label, classCounts.getOrDefault(label, 0) + 1);
        }

        // 返回出现次数最多的类别
        return classCounts.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .get()
                .getKey();
    }

    /**
     * 预测多个样本
     */
    public int[] predict(double[][] X) {
        int[] predictions = new int[X.length];
        for (int i = 0; i < X.length; i++) {
            predictions[i] = predict(X[i]);
        }
        return predictions;
    }

    /**
     * 计算准确率
     */
    public double accuracy(int[] predicted, int[] actual) {
        int correct = 0;
        for (int i = 0; i < predicted.length; i++) {
            if (predicted[i] == actual[i]) correct++;
        }
        return (double) correct / predicted.length;
    }

    /**
     * 生成混淆矩阵
     */
    public int[][] confusionMatrix(int[] predicted, int[] actual, int numClasses) {
        int[][] matrix = new int[numClasses][numClasses];
        for (int i = 0; i < predicted.length; i++) {
            matrix[actual[i]][predicted[i]]++;
        }
        return matrix;
    }

    public static void main(String[] args) {
        System.out.println("=== K近邻算法 (KNN) 演示 ===\n");

        // 生成简单的二维分类数据
        Random rand = new Random(42);
        int n = 100;
        double[][] X = new double[n][2];
        int[] y = new int[n];

        // 类别0: 中心在(2,2)
        // 类别1: 中心在(6,6)
        for (int i = 0; i < n / 2; i++) {
            X[i][0] = 2 + rand.nextGaussian();
            X[i][1] = 2 + rand.nextGaussian();
            y[i] = 0;
        }
        for (int i = n / 2; i < n; i++) {
            X[i][0] = 6 + rand.nextGaussian();
            X[i][1] = 6 + rand.nextGaussian();
            y[i] = 1;
        }

        // 分割训练集和测试集
        int trainSize = 80;
        double[][] XTrain = Arrays.copyOfRange(X, 0, trainSize);
        int[] yTrain = Arrays.copyOfRange(y, 0, trainSize);
        double[][] XTest = Arrays.copyOfRange(X, trainSize, n);
        int[] yTest = Arrays.copyOfRange(y, trainSize, n);

        // 测试不同的k值
        System.out.println("不同k值的准确率:");
        System.out.println("-".repeat(30));

        int bestK = 1;
        double bestAccuracy = 0;

        for (int k = 1; k <= 10; k++) {
            KNN knn = new KNN(k);
            knn.fit(XTrain, yTrain);
            int[] predictions = knn.predict(XTest);
            double acc = knn.accuracy(predictions, yTest);

            System.out.printf("k = %d: %.2f%%%n", k, acc * 100);

            if (acc > bestAccuracy) {
                bestAccuracy = acc;
                bestK = k;
            }
        }

        System.out.printf("%n最佳k值: %d (准确率: %.2f%%)%n%n", bestK, bestAccuracy * 100);

        // 使用最佳k值的详细结果
        KNN bestKNN = new KNN(bestK);
        bestKNN.fit(XTrain, yTrain);
        int[] predictions = bestKNN.predict(XTest);

        // 混淆矩阵
        System.out.println("混淆矩阵:");
        int[][] cm = bestKNN.confusionMatrix(predictions, yTest, 2);
        System.out.println("预测 ->");
        System.out.println("实际 |  0  1");
        System.out.println("-".repeat(15));
        for (int i = 0; i < 2; i++) {
            System.out.printf("  %d  | %d  %d%n", i, cm[i][0], cm[i][1]);
        }

        // 预测新样本
        System.out.println("\n新样本预测:");
        double[][] newSamples = {{2.5, 2.5}, {5.5, 5.5}, {4, 4}};
        int[] newPredictions = bestKNN.predict(newSamples);
        for (int i = 0; i < newSamples.length; i++) {
            System.out.printf("  [%.1f, %.1f] -> 类别 %d%n",
                newSamples[i][0], newSamples[i][1], newPredictions[i]);
        }
    }
}

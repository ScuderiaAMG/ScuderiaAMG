/**
 * 数据预处理工具 - 数据科学
 * 包含数据清洗、标准化、归一化等常用操作
 */
package deep_learning.data_science;

import java.util.*;

public class DataPreprocessing {

    /**
     * Z-Score 标准化
     * 将数据转换为均值为0，标准差为1的分布
     */
    public static double[] zScoreNormalize(double[] data) {
        double mean = calculateMean(data);
        double std = calculateStd(data);

        double[] normalized = new double[data.length];
        for (int i = 0; i < data.length; i++) {
            normalized[i] = (data[i] - mean) / std;
        }
        return normalized;
    }

    /**
     * Min-Max 归一化
     * 将数据缩放到 [0, 1] 范围
     */
    public static double[] minMaxNormalize(double[] data) {
        double min = Double.MAX_VALUE;
        double max = Double.MIN_VALUE;

        for (double val : data) {
            min = Math.min(min, val);
            max = Math.max(max, val);
        }

        double[] normalized = new double[data.length];
        double range = max - min;
        for (int i = 0; i < data.length; i++) {
            normalized[i] = (data[i] - min) / range;
        }
        return normalized;
    }

    /**
     * 计算均值
     */
    public static double calculateMean(double[] data) {
        double sum = 0;
        for (double val : data) {
            sum += val;
        }
        return sum / data.length;
    }

    /**
     * 计算标准差
     */
    public static double calculateStd(double[] data) {
        double mean = calculateMean(data);
        double sumSquaredDiff = 0;
        for (double val : data) {
            sumSquaredDiff += Math.pow(val - mean, 2);
        }
        return Math.sqrt(sumSquaredDiff / data.length);
    }

    /**
     * 计算中位数
     */
    public static double calculateMedian(double[] data) {
        double[] sorted = data.clone();
        Arrays.sort(sorted);
        int n = sorted.length;
        if (n % 2 == 0) {
            return (sorted[n / 2 - 1] + sorted[n / 2]) / 2.0;
        } else {
            return sorted[n / 2];
        }
    }

    /**
     * 独热编码 (One-Hot Encoding)
     * @param labels 类别标签
     * @param numClasses 类别数量
     * @return 独热编码矩阵
     */
    public static int[][] oneHotEncode(int[] labels, int numClasses) {
        int[][] encoded = new int[labels.length][numClasses];
        for (int i = 0; i < labels.length; i++) {
            encoded[i][labels[i]] = 1;
        }
        return encoded;
    }

    /**
     * 标签编码 (Label Encoding)
     * @param labels 字符串标签
     * @return 编码后的整数标签和标签映射
     */
    public static Map<String, Object> labelEncode(String[] labels) {
        Map<String, Integer> labelToIndex = new LinkedHashMap<>();
        int[] encoded = new int[labels.length];

        int index = 0;
        for (int i = 0; i < labels.length; i++) {
            if (!labelToIndex.containsKey(labels[i])) {
                labelToIndex.put(labels[i], index++);
            }
            encoded[i] = labelToIndex.get(labels[i]);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("encoded", encoded);
        result.put("mapping", labelToIndex);
        return result;
    }

    /**
     * 处理缺失值 (用均值填充)
     */
    public static double[] handleMissingValues(double[] data, double missingValue) {
        double[] filled = data.clone();
        double sum = 0;
        int count = 0;

        // 计算非缺失值的均值
        for (double val : data) {
            if (val != missingValue) {
                sum += val;
                count++;
            }
        }
        double mean = count > 0 ? sum / count : 0;

        // 填充缺失值
        for (int i = 0; i < filled.length; i++) {
            if (filled[i] == missingValue) {
                filled[i] = mean;
            }
        }
        return filled;
    }

    /**
     * 数据集分割 (训练集/测试集)
     */
    public static Map<String, double[][]> trainTestSplit(
            double[][] X, double[] y, double testRatio) {
        int n = X.length;
        int testSize = (int) (n * testRatio);
        int trainSize = n - testSize;

        // 随机打乱索引
        int[] indices = new int[n];
        for (int i = 0; i < n; i++) indices[i] = i;
        shuffleArray(indices);

        double[][] XTrain = new double[trainSize][];
        double[][] XTest = new double[testSize][];
        double[] yTrain = new double[trainSize];
        double[] yTest = new double[testSize];

        for (int i = 0; i < trainSize; i++) {
            XTrain[i] = X[indices[i]];
            yTrain[i] = y[indices[i]];
        }
        for (int i = 0; i < testSize; i++) {
            XTest[i] = X[indices[trainSize + i]];
            yTest[i] = y[indices[trainSize + i]];
        }

        Map<String, double[][]> result = new HashMap<>();
        result.put("X_train", XTrain);
        result.put("X_test", XTest);
        result.put("y_train", new double[][]{yTrain});
        result.put("y_test", new double[][]{yTest});
        return result;
    }

    private static void shuffleArray(int[] arr) {
        Random rand = new Random(42);
        for (int i = arr.length - 1; i > 0; i--) {
            int j = rand.nextInt(i + 1);
            int temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 数据预处理演示 ===\n");

        // 原始数据
        double[] data = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
        System.out.println("原始数据: " + Arrays.toString(data));
        System.out.printf("均值: %.2f%n", calculateMean(data));
        System.out.printf("标准差: %.2f%n", calculateStd(data));
        System.out.printf("中位数: %.2f%n%n", calculateMedian(data));

        // Z-Score 标准化
        double[] zNormalized = zScoreNormalize(data);
        System.out.println("Z-Score 标准化: " + Arrays.toString(zNormalized));
        System.out.printf("新均值: %.4f%n", calculateMean(zNormalized));
        System.out.printf("新标准差: %.4f%n%n", calculateStd(zNormalized));

        // Min-Max 归一化
        double[] mmNormalized = minMaxNormalize(data);
        System.out.println("Min-Max 归一化: " + formatArray(mmNormalized));

        // 独热编码
        System.out.println("\n=== 独热编码演示 ===");
        int[] labels = {0, 1, 2, 1, 0};
        int[][] oneHot = oneHotEncode(labels, 3);
        System.out.println("原始标签: " + Arrays.toString(labels));
        System.out.println("独热编码:");
        for (int i = 0; i < labels.length; i++) {
            System.out.printf("  %d -> %s%n", labels[i], Arrays.toString(oneHot[i]));
        }

        // 标签编码
        System.out.println("\n=== 标签编码演示 ===");
        String[] strLabels = {"cat", "dog", "bird", "cat", "dog"};
        Map<String, Object> encoded = labelEncode(strLabels);
        System.out.println("原始标签: " + Arrays.toString(strLabels));
        System.out.println("编码结果: " + Arrays.toString((int[]) encoded.get("encoded")));
        System.out.println("标签映射: " + encoded.get("mapping"));

        // 处理缺失值
        System.out.println("\n=== 缺失值处理 ===");
        double[] dataWithMissing = {1, 2, -999, 4, 5, -999, 7};
        System.out.println("含缺失值数据: " + Arrays.toString(dataWithMissing));
        double[] filled = handleMissingValues(dataWithMissing, -999);
        System.out.println("填充后数据: " + formatArray(filled));
    }

    private static String formatArray(double[] arr) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < arr.length; i++) {
            sb.append(String.format("%.4f", arr[i]));
            if (i < arr.length - 1) sb.append(", ");
        }
        sb.append("]");
        return sb.toString();
    }
}

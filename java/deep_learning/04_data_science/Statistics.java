/**
 * 统计学工具类 - 数据科学
 * 包含描述统计、概率分布、假设检验等
 */
package deep_learning.data_science;

import java.util.*;

public class Statistics {

    /**
     * 计算均值
     */
    public static double mean(double[] data) {
        double sum = 0;
        for (double val : data) sum += val;
        return sum / data.length;
    }

    /**
     * 计算方差
     */
    public static double variance(double[] data) {
        double m = mean(data);
        double sum = 0;
        for (double val : data) {
            sum += Math.pow(val - m, 2);
        }
        return sum / data.length;
    }

    /**
     * 计算标准差
     */
    public static double std(double[] data) {
        return Math.sqrt(variance(data));
    }

    /**
     * 计算协方差
     */
    public static double covariance(double[] x, double[] y) {
        double meanX = mean(x);
        double meanY = mean(y);
        double sum = 0;
        for (int i = 0; i < x.length; i++) {
            sum += (x[i] - meanX) * (y[i] - meanY);
        }
        return sum / x.length;
    }

    /**
     * 计算皮尔逊相关系数
     */
    public static double pearsonCorrelation(double[] x, double[] y) {
        return covariance(x, y) / (std(x) * std(y));
    }

    /**
     * 计算百分位数
     */
    public static double percentile(double[] data, double p) {
        double[] sorted = data.clone();
        Arrays.sort(sorted);
        double index = (p / 100) * (sorted.length - 1);
        int lower = (int) Math.floor(index);
        int upper = (int) Math.ceil(index);
        if (lower == upper) return sorted[lower];
        return sorted[lower] + (index - lower) * (sorted[upper] - sorted[lower]);
    }

    /**
     * 计算四分位距 (IQR)
     */
    public static double iqr(double[] data) {
        return percentile(data, 75) - percentile(data, 25);
    }

    /**
     * 计算偏度
     */
    public static double skewness(double[] data) {
        double m = mean(data);
        double s = std(data);
        double n = data.length;
        double sum = 0;
        for (double val : data) {
            sum += Math.pow((val - m) / s, 3);
        }
        return (n / ((n - 1) * (n - 2))) * sum;
    }

    /**
     * 计算峰度
     */
    public static double kurtosis(double[] data) {
        double m = mean(data);
        double s = std(data);
        double n = data.length;
        double sum = 0;
        for (double val : data) {
            sum += Math.pow((val - m) / s, 4);
        }
        return ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * sum
               - (3 * Math.pow(n - 1, 2)) / ((n - 2) * (n - 3));
    }

    /**
     * 正态分布概率密度函数
     */
    public static double normalPDF(double x, double mu, double sigma) {
        double coefficient = 1.0 / (sigma * Math.sqrt(2 * Math.PI));
        double exponent = -0.5 * Math.pow((x - mu) / sigma, 2);
        return coefficient * Math.exp(exponent);
    }

    /**
     * 正态分布累积分布函数 (近似)
     */
    public static double normalCDF(double x, double mu, double sigma) {
        double z = (x - mu) / sigma;
        return 0.5 * (1 + erf(z / Math.sqrt(2)));
    }

    /**
     * 误差函数 (近似)
     */
    private static double erf(double x) {
        double t = 1.0 / (1.0 + 0.3275911 * Math.abs(x));
        double y = 1.0 - (((((1.061405429 * t - 1.453152027) * t)
                + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t
                * Math.exp(-x * x);
        return x >= 0 ? y : -y;
    }

    /**
     * 描述统计摘要
     */
    public static void descriptiveStats(double[] data, String name) {
        System.out.println("=== " + name + " 描述统计 ===");
        System.out.printf("  样本数: %d%n", data.length);
        System.out.printf("  均值: %.4f%n", mean(data));
        System.out.printf("  标准差: %.4f%n", std(data));
        System.out.printf("  最小值: %.4f%n", Arrays.stream(data).min().orElse(0));
        System.out.printf("  25%%分位: %.4f%n", percentile(data, 25));
        System.out.printf("  中位数: %.4f%n", percentile(data, 50));
        System.out.printf("  75%%分位: %.4f%n", percentile(data, 75));
        System.out.printf("  最大值: %.4f%n", Arrays.stream(data).max().orElse(0));
        System.out.printf("  偏度: %.4f%n", skewness(data));
        System.out.printf("  峰度: %.4f%n", kurtosis(data));
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("=== 统计学工具演示 ===\n");

        // 生成示例数据
        Random rand = new Random(42);
        double[] data = new double[100];
        for (int i = 0; i < 100; i++) {
            data[i] = rand.nextGaussian() * 10 + 50;  // 均值50，标准差10
        }

        // 描述统计
        descriptiveStats(data, "正态分布数据");

        // 相关性分析
        System.out.println("=== 相关性分析 ===");
        double[] x = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
        double[] y = {2, 4, 5, 4, 8, 7, 8, 9, 10, 12};

        System.out.printf("变量X: %s%n", Arrays.toString(x));
        System.out.printf("变量Y: %s%n", Arrays.toString(y));
        System.out.printf("皮尔逊相关系数: %.4f%n", pearsonCorrelation(x, y));
        System.out.printf("协方差: %.4f%n%n", covariance(x, y));

        // 正态分布
        System.out.println("=== 正态分布 N(0,1) ===");
        System.out.println("x\t\tPDF\t\tCDF");
        System.out.println("-".repeat(40));
        for (double val = -3; val <= 3; val += 0.5) {
            System.out.printf("%.1f\t\t%.4f\t\t%.4f%n",
                val, normalPDF(val, 0, 1), normalCDF(val, 0, 1));
        }

        // 箱线图信息
        System.out.println("\n=== 箱线图信息 ===");
        double q1 = percentile(data, 25);
        double q2 = percentile(data, 50);
        double q3 = percentile(data, 75);
        double iqr = iqr(data);
        double lowerFence = q1 - 1.5 * iqr;
        double upperFence = q3 + 1.5 * iqr;

        System.out.printf("Q1: %.2f%n", q1);
        System.out.printf("Q2 (中位数): %.2f%n", q2);
        System.out.printf("Q3: %.2f%n", q3);
        System.out.printf("IQR: %.2f%n", iqr);
        System.out.printf("下限: %.2f%n", lowerFence);
        System.out.printf("上限: %.2f%n", upperFence);
    }
}

/**
 * 卷积神经网络 (CNN) 基础实现 - 高级深度学习
 * 演示卷积层、池化层的基本操作
 */
package deep_learning.advanced;

public class CNN {

    /**
     * 2D卷积操作
     * @param input 输入矩阵
     * @param kernel 卷积核
     * @param stride 步长
     * @param padding 填充
     * @return 卷积结果
     */
    public static double[][] convolve2D(double[][] input, double[][] kernel,
                                         int stride, int padding) {
        int inputRows = input.length;
        int inputCols = input[0].length;
        int kernelRows = kernel.length;
        int kernelCols = kernel[0].length;

        // 计算输出尺寸
        int outputRows = (inputRows - kernelRows + 2 * padding) / stride + 1;
        int outputCols = (inputCols - kernelCols + 2 * padding) / stride + 1;

        double[][] output = new double[outputRows][outputCols];

        // 带填充的输入
        double[][] paddedInput = addPadding(input, padding);

        // 执行卷积
        for (int i = 0; i < outputRows; i++) {
            for (int j = 0; j < outputCols; j++) {
                double sum = 0;
                for (int ki = 0; ki < kernelRows; ki++) {
                    for (int kj = 0; kj < kernelCols; kj++) {
                        int row = i * stride + ki;
                        int col = j * stride + kj;
                        sum += paddedInput[row][col] * kernel[ki][kj];
                    }
                }
                output[i][j] = sum;
            }
        }

        return output;
    }

    /**
     * 添加零填充
     */
    private static double[][] addPadding(double[][] input, int padding) {
        if (padding == 0) return input;

        int rows = input.length;
        int cols = input[0].length;
        double[][] padded = new double[rows + 2 * padding][cols + 2 * padding];

        for (int i = 0; i < rows; i++) {
            System.arraycopy(input[i], 0, padded[i + padding], padding, cols);
        }

        return padded;
    }

    /**
     * 最大池化
     * @param input 输入矩阵
     * @param poolSize 池化窗口大小
     * @param stride 步长
     * @return 池化结果
     */
    public static double[][] maxPooling(double[][] input, int poolSize, int stride) {
        int rows = input.length;
        int cols = input[0].length;
        int outRows = (rows - poolSize) / stride + 1;
        int outCols = (cols - poolSize) / stride + 1;

        double[][] output = new double[outRows][outCols];

        for (int i = 0; i < outRows; i++) {
            for (int j = 0; j < outCols; j++) {
                double max = Double.NEGATIVE_INFINITY;
                for (int pi = 0; pi < poolSize; pi++) {
                    for (int pj = 0; pj < poolSize; pj++) {
                        int row = i * stride + pi;
                        int col = j * stride + pj;
                        max = Math.max(max, input[row][col]);
                    }
                }
                output[i][j] = max;
            }
        }

        return output;
    }

    /**
     * 平均池化
     */
    public static double[][] averagePooling(double[][] input, int poolSize, int stride) {
        int rows = input.length;
        int cols = input[0].length;
        int outRows = (rows - poolSize) / stride + 1;
        int outCols = (cols - poolSize) / stride + 1;

        double[][] output = new double[outRows][outCols];

        for (int i = 0; i < outRows; i++) {
            for (int j = 0; j < outCols; j++) {
                double sum = 0;
                for (int pi = 0; pi < poolSize; pi++) {
                    for (int pj = 0; pj < poolSize; pj++) {
                        sum += input[i * stride + pi][j * stride + pj];
                    }
                }
                output[i][j] = sum / (poolSize * poolSize);
            }
        }

        return output;
    }

    /**
     * ReLU 激活
     */
    public static double[][] relu(double[][] input) {
        int rows = input.length;
        int cols = input[0].length;
        double[][] output = new double[rows][cols];

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                output[i][j] = Math.max(0, input[i][j]);
            }
        }

        return output;
    }

    /**
     * 打印矩阵
     */
    public static void printMatrix(double[][] matrix, String name) {
        System.out.println(name + ":");
        for (double[] row : matrix) {
            System.out.print("[ ");
            for (double val : row) {
                System.out.printf("%6.2f ", val);
            }
            System.out.println("]");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("=== 卷积神经网络 (CNN) 操作演示 ===\n");

        // 输入图像 (5x5)
        double[][] image = {
            {1, 2, 3, 4, 5},
            {6, 7, 8, 9, 10},
            {11, 12, 13, 14, 15},
            {16, 17, 18, 19, 20},
            {21, 22, 23, 24, 25}
        };
        printMatrix(image, "输入图像 (5x5)");

        // 卷积核 (3x3) - 边缘检测
        double[][] edgeKernel = {
            {-1, -1, -1},
            {-1,  8, -1},
            {-1, -1, -1}
        };
        printMatrix(edgeKernel, "边缘检测卷积核 (3x3)");

        // 卷积操作
        double[][] convResult = convolve2D(image, edgeKernel, 1, 0);
        printMatrix(convResult, "卷积结果 (3x3)");

        // 带填充的卷积
        double[][] convPadded = convolve2D(image, edgeKernel, 1, 1);
        printMatrix(convPadded, "带填充的卷积结果 (5x5)");

        // ReLU 激活
        double[][] reluResult = relu(convResult);
        printMatrix(reluResult, "ReLU 激活后");

        // 最大池化
        double[][] maxPooled = maxPooling(image, 2, 2);
        printMatrix(maxPooled, "最大池化 (2x2, stride=2)");

        // 平均池化
        double[][] avgPooled = averagePooling(image, 2, 2);
        printMatrix(avgPooled, "平均池化 (2x2, stride=2)");

        // 演示多通道卷积
        System.out.println("=== 多通道卷积演示 ===\n");

        // 3通道输入 (模拟RGB图像)
        double[][] channel1 = {{1, 2}, {3, 4}};
        double[][] channel2 = {{5, 6}, {7, 8}};
        double[][] channel3 = {{9, 10}, {11, 12}};

        double[][] kernel1 = {{1, 0}, {0, 1}};
        double[][] kernel2 = {{0, 1}, {1, 0}};
        double[][] kernel3 = {{1, 1}, {0, 0}};

        // 多通道卷积 (逐通道卷积后求和)
        double[][] result1 = convolve2D(channel1, kernel1, 1, 0);
        double[][] result2 = convolve2D(channel2, kernel2, 1, 0);
        double[][] result3 = convolve2D(channel3, kernel3, 1, 0);

        // 合并结果
        double[][] merged = new double[result1.length][result1[0].length];
        for (int i = 0; i < merged.length; i++) {
            for (int j = 0; j < merged[0].length; j++) {
                merged[i][j] = result1[i][j] + result2[i][j] + result3[i][j];
            }
        }

        printMatrix(channel1, "通道1");
        printMatrix(channel2, "通道2");
        printMatrix(channel3, "通道3");
        printMatrix(merged, "多通道卷积结果");
    }
}

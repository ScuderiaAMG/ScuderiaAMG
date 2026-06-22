/**
 * 图像处理基础 - 计算机视觉
 * 演示图像的基本操作和滤波
 */
package deep_learning.computer_vision;

public class ImageProcessing {

    /**
     * 灰度转换
     * @param rgb RGB像素值 [height][width][3]
     * @return 灰度值 [height][width]
     */
    public static int[][] toGrayscale(int[][][] rgb) {
        int height = rgb.length;
        int width = rgb[0].length;
        int[][] gray = new int[height][width];

        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                // 加权平均法
                gray[i][j] = (int) (0.299 * rgb[i][j][0] +
                                   0.587 * rgb[i][j][1] +
                                   0.114 * rgb[i][j][2]);
            }
        }
        return gray;
    }

    /**
     * 二值化
     */
    public static int[][] threshold(int[][] gray, int threshold) {
        int height = gray.length;
        int width = gray[0].length;
        int[][] binary = new int[height][width];

        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                binary[i][j] = gray[i][j] > threshold ? 255 : 0;
            }
        }
        return binary;
    }

    /**
     * 图像卷积
     */
    public static double[][] convolve(double[][] image, double[][] kernel) {
        int imgH = image.length;
        int imgW = image[0].length;
        int kerH = kernel.length;
        int kerW = kernel[0].length;
        int padH = kerH / 2;
        int padW = kerW / 2;

        double[][] output = new double[imgH][imgW];

        for (int i = 0; i < imgH; i++) {
            for (int j = 0; j < imgW; j++) {
                double sum = 0;
                for (int ki = 0; ki < kerH; ki++) {
                    for (int kj = 0; kj < kerW; kj++) {
                        int row = i + ki - padH;
                        int col = j + kj - padW;
                        if (row >= 0 && row < imgH && col >= 0 && col < imgW) {
                            sum += image[row][col] * kernel[ki][kj];
                        }
                    }
                }
                output[i][j] = sum;
            }
        }
        return output;
    }

    /**
     * 均值滤波 (模糊)
     */
    public static double[][] averageFilter(double[][] image, int size) {
        double[][] kernel = new double[size][size];
        double val = 1.0 / (size * size);
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                kernel[i][j] = val;
            }
        }
        return convolve(image, kernel);
    }

    /**
     * 高斯滤波
     */
    public static double[][] gaussianFilter(double[][] image, int size, double sigma) {
        double[][] kernel = new double[size][size];
        double sum = 0;
        int center = size / 2;

        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                double x = i - center;
                double y = j - center;
                kernel[i][j] = Math.exp(-(x * x + y * y) / (2 * sigma * sigma));
                sum += kernel[i][j];
            }
        }

        // 归一化
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                kernel[i][j] /= sum;
            }
        }

        return convolve(image, kernel);
    }

    /**
     * Sobel边缘检测
     */
    public static double[][] sobelEdgeDetection(double[][] image) {
        double[][] sobelX = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
        double[][] sobelY = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

        double[][] gx = convolve(image, sobelX);
        double[][] gy = convolve(image, sobelY);

        int height = image.length;
        int width = image[0].length;
        double[][] magnitude = new double[height][width];

        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                magnitude[i][j] = Math.sqrt(gx[i][j] * gx[i][j] + gy[i][j] * gy[i][j]);
            }
        }

        return magnitude;
    }

    /**
     * 图像旋转 (90度)
     */
    public static int[][] rotate90(int[][] image) {
        int height = image.length;
        int width = image[0].length;
        int[][] rotated = new int[width][height];

        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                rotated[j][height - 1 - i] = image[i][j];
            }
        }
        return rotated;
    }

    /**
     * 图像缩放 (最近邻)
     */
    public static int[][] resize(int[][] image, int newHeight, int newWidth) {
        int height = image.length;
        int width = image[0].length;
        int[][] resized = new int[newHeight][newWidth];

        double scaleY = (double) height / newHeight;
        double scaleX = (double) width / newWidth;

        for (int i = 0; i < newHeight; i++) {
            for (int j = 0; j < newWidth; j++) {
                int srcY = Math.min((int) (i * scaleY), height - 1);
                int srcX = Math.min((int) (j * scaleX), width - 1);
                resized[i][j] = image[srcY][srcX];
            }
        }
        return resized;
    }

    /**
     * 打印矩阵 (简化)
     */
    public static void printMatrix(double[][] matrix, String name) {
        System.out.println(name + " (" + matrix.length + "x" + matrix[0].length + "):");
        int maxPrint = Math.min(5, matrix.length);
        for (int i = 0; i < maxPrint; i++) {
            System.out.print("  [");
            for (int j = 0; j < Math.min(5, matrix[i].length); j++) {
                System.out.printf("%6.1f", matrix[i][j]);
                if (j < Math.min(4, matrix[i].length - 1)) System.out.print(", ");
            }
            if (matrix[i].length > 5) System.out.print(", ...");
            System.out.println("]");
        }
        if (matrix.length > 5) System.out.println("  ...");
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("=== 图像处理演示 ===\n");

        // 创建测试图像 (8x8)
        double[][] image = {
            {10, 10, 10, 10, 10, 10, 10, 10},
            {10, 20, 20, 20, 20, 20, 20, 10},
            {10, 20, 30, 30, 30, 30, 20, 10},
            {10, 20, 30, 40, 40, 30, 20, 10},
            {10, 20, 30, 40, 40, 30, 20, 10},
            {10, 20, 30, 30, 30, 30, 20, 10},
            {10, 20, 20, 20, 20, 20, 20, 10},
            {10, 10, 10, 10, 10, 10, 10, 10}
        };

        printMatrix(image, "原始图像");

        // 均值滤波
        double[][] blurred = averageFilter(image, 3);
        printMatrix(blurred, "均值滤波 (3x3)");

        // 高斯滤波
        double[][] gaussian = gaussianFilter(image, 3, 1.0);
        printMatrix(gaussian, "高斯滤波 (3x3, σ=1.0)");

        // 边缘检测
        double[][] edges = sobelEdgeDetection(image);
        printMatrix(edges, "Sobel边缘检测");

        // 卷积核演示
        System.out.println("常用卷积核:");
        System.out.println("  锐化:  [[0,-1,0], [-1,5,-1], [0,-1,0]]");
        System.out.println("  浮雕:  [[-2,-1,0], [-1,1,1], [0,1,2]]");
        System.out.println("  边缘:  [[-1,-1,-1], [-1,8,-1], [-1,-1,-1]]");
    }
}

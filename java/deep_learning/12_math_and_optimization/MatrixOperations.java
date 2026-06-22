/**
 * 矩阵运算库 - 数学与优化
 * 包含矩阵基本运算和线性代数操作
 */
package deep_learning.math_and_optimization;

public class MatrixOperations {
    private double[][] data;
    private int rows, cols;

    public MatrixOperations(double[][] data) {
        this.data = data;
        this.rows = data.length;
        this.cols = data[0].length;
    }

    public MatrixOperations(int rows, int cols) {
        this.rows = rows;
        this.cols = cols;
        this.data = new double[rows][cols];
    }

    /**
     * 矩阵加法
     */
    public MatrixOperations add(MatrixOperations other) {
        if (rows != other.rows || cols != other.cols) {
            throw new IllegalArgumentException("Matrix dimensions must match");
        }

        double[][] result = new double[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result[i][j] = data[i][j] + other.data[i][j];
            }
        }
        return new MatrixOperations(result);
    }

    /**
     * 矩阵减法
     */
    public MatrixOperations subtract(MatrixOperations other) {
        if (rows != other.rows || cols != other.cols) {
            throw new IllegalArgumentException("Matrix dimensions must match");
        }

        double[][] result = new double[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result[i][j] = data[i][j] - other.data[i][j];
            }
        }
        return new MatrixOperations(result);
    }

    /**
     * 矩阵乘法
     */
    public MatrixOperations multiply(MatrixOperations other) {
        if (cols != other.rows) {
            throw new IllegalArgumentException(
                "Columns of A must equal rows of B");
        }

        double[][] result = new double[rows][other.cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < other.cols; j++) {
                for (int k = 0; k < cols; k++) {
                    result[i][j] += data[i][k] * other.data[k][j];
                }
            }
        }
        return new MatrixOperations(result);
    }

    /**
     * 标量乘法
     */
    public MatrixOperations scalarMultiply(double scalar) {
        double[][] result = new double[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result[i][j] = data[i][j] * scalar;
            }
        }
        return new MatrixOperations(result);
    }

    /**
     * 转置
     */
    public MatrixOperations transpose() {
        double[][] result = new double[cols][rows];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result[j][i] = data[i][j];
            }
        }
        return new MatrixOperations(result);
    }

    /**
     * 计算行列式 (仅方阵)
     */
    public double determinant() {
        if (rows != cols) {
            throw new IllegalArgumentException("Matrix must be square");
        }
        return computeDeterminant(data);
    }

    private double computeDeterminant(double[][] matrix) {
        int n = matrix.length;
        if (n == 1) return matrix[0][0];
        if (n == 2) {
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0];
        }

        double det = 0;
        for (int j = 0; j < n; j++) {
            det += Math.pow(-1, j) * matrix[0][j] *
                   computeDeterminant(getMinor(matrix, 0, j));
        }
        return det;
    }

    private double[][] getMinor(double[][] matrix, int row, int col) {
        int n = matrix.length;
        double[][] minor = new double[n - 1][n - 1];
        int r = 0;
        for (int i = 0; i < n; i++) {
            if (i == row) continue;
            int c = 0;
            for (int j = 0; j < n; j++) {
                if (j == col) continue;
                minor[r][c] = matrix[i][j];
                c++;
            }
            r++;
        }
        return minor;
    }

    /**
     * 逆矩阵 (使用伴随矩阵法)
     */
    public MatrixOperations inverse() {
        double det = determinant();
        if (Math.abs(det) < 1e-10) {
            throw new IllegalArgumentException("Matrix is singular");
        }

        int n = rows;
        double[][] adjugate = new double[n][n];

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                double[][] minor = getMinor(data, i, j);
                adjugate[j][i] = Math.pow(-1, i + j) * computeDeterminant(minor);
            }
        }

        return new MatrixOperations(adjugate).scalarMultiply(1.0 / det);
    }

    /**
     * 矩阵元素-wise乘法 (Hadamard积)
     */
    public MatrixOperations elementMultiply(MatrixOperations other) {
        double[][] result = new double[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result[i][j] = data[i][j] * other.data[i][j];
            }
        }
        return new MatrixOperations(result);
    }

    /**
     * 应用函数到每个元素
     */
    public MatrixOperations apply(UnaryOperator op) {
        double[][] result = new double[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result[i][j] = op.apply(data[i][j]);
            }
        }
        return new MatrixOperations(result);
    }

    interface UnaryOperator {
        double apply(double x);
    }

    /**
     * 获取元素
     */
    public double get(int i, int j) {
        return data[i][j];
    }

    /**
     * 设置元素
     */
    public void set(int i, int j, double value) {
        data[i][j] = value;
    }

    /**
     * 获取形状
     */
    public int[] shape() {
        return new int[]{rows, cols};
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < rows; i++) {
            sb.append("[");
            for (int j = 0; j < cols; j++) {
                sb.append(String.format("%8.4f", data[i][j]));
                if (j < cols - 1) sb.append(", ");
            }
            sb.append("]\n");
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        System.out.println("=== 矩阵运算演示 ===\n");

        // 创建矩阵
        double[][] aData = {{1, 2}, {3, 4}};
        double[][] bData = {{5, 6}, {7, 8}};

        MatrixOperations A = new MatrixOperations(aData);
        MatrixOperations B = new MatrixOperations(bData);

        System.out.println("矩阵 A:");
        System.out.println(A);
        System.out.println("矩阵 B:");
        System.out.println(B);

        // 矩阵加法
        System.out.println("A + B:");
        System.out.println(A.add(B));

        // 矩阵乘法
        System.out.println("A * B:");
        System.out.println(A.multiply(B));

        // 转置
        System.out.println("A转置:");
        System.out.println(A.transpose());

        // 行列式
        System.out.printf("det(A) = %.2f%n", A.determinant());
        System.out.printf("det(B) = %.2f%n", B.determinant());

        // 逆矩阵
        System.out.println("A的逆矩阵:");
        MatrixOperations AInv = A.inverse();
        System.out.println(AInv);

        // 验证: A * A^(-1) = I
        System.out.println("A * A^(-1) (应为单位矩阵):");
        System.out.println(A.multiply(AInv));

        // 元素-wise操作
        System.out.println("A .* B (Hadamard积):");
        System.out.println(A.elementMultiply(B));

        // 应用ReLU
        System.out.println("ReLU应用于矩阵 [[-1, 2], [-3, 4]]:");
        MatrixOperations m = new MatrixOperations(new double[][]{{-1, 2}, {-3, 4}});
        System.out.println(m.apply(x -> Math.max(0, x)));
    }
}

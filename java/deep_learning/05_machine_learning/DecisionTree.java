/**
 * 决策树实现 - 机器学习
 * 使用ID3算法 (基于信息增益)
 */
package deep_learning.machine_learning;

import java.util.*;

public class DecisionTree {
    private Node root;
    private int maxDepth;

    /**
     * 树节点
     */
    static class Node {
        int featureIndex;    // 分裂特征索引
        double threshold;    // 分裂阈值
        int label;           // 叶节点的标签
        Node left;           // 左子树 (<= threshold)
        Node right;          // 右子树 (> threshold)
        boolean isLeaf;

        Node(int label) {
            this.label = label;
            this.isLeaf = true;
        }

        Node(int featureIndex, double threshold) {
            this.featureIndex = featureIndex;
            this.threshold = threshold;
            this.isLeaf = false;
        }
    }

    public DecisionTree(int maxDepth) {
        this.maxDepth = maxDepth;
    }

    /**
     * 计算熵
     */
    private double entropy(int[] labels) {
        Map<Integer, Integer> counts = new HashMap<>();
        for (int label : labels) {
            counts.put(label, counts.getOrDefault(label, 0) + 1);
        }

        double entropy = 0;
        int n = labels.length;
        for (int count : counts.values()) {
            double p = (double) count / n;
            if (p > 0) {
                entropy -= p * Math.log(p) / Math.log(2);
            }
        }
        return entropy;
    }

    /**
     * 计算信息增益
     */
    private double informationGain(double[][] X, int[] y, int featureIndex, double threshold) {
        int[] leftLabels, rightLabels;
        List<Integer> leftIdx = new ArrayList<>();
        List<Integer> rightIdx = new ArrayList<>();

        for (int i = 0; i < X.length; i++) {
            if (X[i][featureIndex] <= threshold) {
                leftIdx.add(i);
            } else {
                rightIdx.add(i);
            }
        }

        if (leftIdx.isEmpty() || rightIdx.isEmpty()) return 0;

        leftLabels = new int[leftIdx.size()];
        rightLabels = new int[rightIdx.size()];

        for (int i = 0; i < leftIdx.size(); i++) {
            leftLabels[i] = y[leftIdx.get(i)];
        }
        for (int i = 0; i < rightIdx.size(); i++) {
            rightLabels[i] = y[rightIdx.get(i)];
        }

        double parentEntropy = entropy(y);
        double leftEntropy = entropy(leftLabels);
        double rightEntropy = entropy(rightLabels);

        double leftWeight = (double) leftLabels.length / y.length;
        double rightWeight = (double) rightLabels.length / y.length;

        return parentEntropy - leftWeight * leftEntropy - rightWeight * rightEntropy;
    }

    /**
     * 找到最佳分裂点
     */
    private int[] findBestSplit(double[][] X, int[] y) {
        double bestGain = -1;
        int bestFeature = -1;
        double bestThreshold = 0;

        for (int feature = 0; feature < X[0].length; feature++) {
            // 获取该特征的所有唯一值
            Set<Double> thresholds = new TreeSet<>();
            for (double[] sample : X) {
                thresholds.add(sample[feature]);
            }

            for (double threshold : thresholds) {
                double gain = informationGain(X, y, feature, threshold);
                if (gain > bestGain) {
                    bestGain = gain;
                    bestFeature = feature;
                    bestThreshold = threshold;
                }
            }
        }

        return new int[]{bestFeature, (int) bestThreshold, (int) (bestGain * 1000)};
    }

    /**
     * 获取多数类
     */
    private int majorityClass(int[] labels) {
        Map<Integer, Integer> counts = new HashMap<>();
        for (int label : labels) {
            counts.put(label, counts.getOrDefault(label, 0) + 1);
        }
        return counts.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .get()
                .getKey();
    }

    /**
     * 递归构建树
     */
    private Node buildTree(double[][] X, int[] y, int depth) {
        // 终止条件
        if (depth >= maxDepth || entropy(y) == 0) {
            return new Node(majorityClass(y));
        }

        int[] bestSplit = findBestSplit(X, y);
        int featureIndex = bestSplit[0];
        double threshold = bestSplit[1];

        if (featureIndex == -1) {
            return new Node(majorityClass(y));
        }

        // 分割数据
        List<double[]> leftX = new ArrayList<>();
        List<double[]> rightX = new ArrayList<>();
        List<Integer> leftY = new ArrayList<>();
        List<Integer> rightY = new ArrayList<>();

        for (int i = 0; i < X.length; i++) {
            if (X[i][featureIndex] <= threshold) {
                leftX.add(X[i]);
                leftY.add(y[i]);
            } else {
                rightX.add(X[i]);
                rightY.add(y[i]);
            }
        }

        // 递归构建子树
        Node node = new Node(featureIndex, threshold);
        node.left = buildTree(leftX.toArray(new double[0][]),
                             leftY.stream().mapToInt(Integer::intValue).toArray(), depth + 1);
        node.right = buildTree(rightX.toArray(new double[0][]),
                              rightY.stream().mapToInt(Integer::intValue).toArray(), depth + 1);

        return node;
    }

    /**
     * 训练模型
     */
    public void fit(double[][] X, int[] y) {
        root = buildTree(X, y, 0);
    }

    /**
     * 预测单个样本
     */
    public int predict(double[] x) {
        Node node = root;
        while (!node.isLeaf) {
            if (x[node.featureIndex] <= node.threshold) {
                node = node.left;
            } else {
                node = node.right;
            }
        }
        return node.label;
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
     * 打印树结构
     */
    public void printTree() {
        printNode(root, 0);
    }

    private void printNode(Node node, int depth) {
        String indent = "  ".repeat(depth);
        if (node.isLeaf) {
            System.out.println(indent + "Leaf: class " + node.label);
        } else {
            System.out.println(indent + "Feature " + node.featureIndex +
                             " <= " + node.threshold);
            printNode(node.left, depth + 1);
            System.out.println(indent + "Feature " + node.featureIndex +
                             " > " + node.threshold);
            printNode(node.right, depth + 1);
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 决策树演示 ===\n");

        // 生成简单的分类数据
        double[][] X = {
            {1, 1}, {1, 2}, {2, 1}, {2, 2},  // 类别0
            {5, 5}, {5, 6}, {6, 5}, {6, 6},  // 类别1
            {1, 5}, {1, 6}, {2, 5}, {2, 6},  // 类别2
        };
        int[] y = {0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2};

        // 训练决策树
        DecisionTree tree = new DecisionTree(3);
        tree.fit(X, y);

        // 打印树结构
        System.out.println("决策树结构:");
        tree.printTree();

        // 预测
        System.out.println("\n预测结果:");
        double[][] testX = {{1.5, 1.5}, {5.5, 5.5}, {1.5, 5.5}, {3, 3}};
        int[] predictions = tree.predict(testX);

        for (int i = 0; i < testX.length; i++) {
            System.out.printf("  [%.1f, %.1f] -> 类别 %d%n",
                testX[i][0], testX[i][1], predictions[i]);
        }

        // 计算训练准确率
        int[] trainPred = tree.predict(X);
        int correct = 0;
        for (int i = 0; i < y.length; i++) {
            if (trainPred[i] == y[i]) correct++;
        }
        System.out.printf("%n训练准确率: %.2f%%%n", (double) correct / y.length * 100);
    }
}

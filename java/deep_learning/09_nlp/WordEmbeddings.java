/**
 * 词嵌入演示 - 自然语言处理
 * 演示Word2Vec的基本概念
 */
package deep_learning.nlp;

import java.util.*;

public class WordEmbeddings {
    private int embeddingSize;
    private Map<String, double[]> wordVectors;
    private Random random;

    public WordEmbeddings(int embeddingSize) {
        this.embeddingSize = embeddingSize;
        this.wordVectors = new HashMap<>();
        this.random = new Random(42);
    }

    /**
     * 初始化词向量
     */
    public void initializeVocabulary(List<String> vocabulary) {
        for (String word : vocabulary) {
            double[] vector = new double[embeddingSize];
            for (int i = 0; i < embeddingSize; i++) {
                vector[i] = random.nextGaussian() * 0.1;
            }
            wordVectors.put(word, vector);
        }
    }

    /**
     * 计算余弦相似度
     */
    public double cosineSimilarity(double[] a, double[] b) {
        double dotProduct = 0, normA = 0, normB = 0;
        for (int i = 0; i < a.length; i++) {
            dotProduct += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    /**
     * 找到最相似的词
     */
    public List<Map.Entry<String, Double>> findSimilar(String word, int topK) {
        double[] wordVec = wordVectors.get(word);
        if (wordVec == null) return new ArrayList<>();

        TreeMap<String, Double> similarities = new TreeMap<>();
        for (Map.Entry<String, double[]> entry : wordVectors.entrySet()) {
            if (!entry.getKey().equals(word)) {
                double sim = cosineSimilarity(wordVec, entry.getValue());
                similarities.put(entry.getKey(), sim);
            }
        }

        List<Map.Entry<String, Double>> sorted = new ArrayList<>(similarities.entrySet());
        sorted.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));
        return sorted.subList(0, Math.min(topK, sorted.size()));
    }

    /**
     * 词向量运算: king - man + woman = ?
     */
    public String analogy(String word1, String word2, String word3) {
        double[] vec1 = wordVectors.get(word1);
        double[] vec2 = wordVectors.get(word2);
        double[] vec3 = wordVectors.get(word3);

        if (vec1 == null || vec2 == null || vec3 == null) return null;

        // 计算 word1 - word2 + word3
        double[] result = new double[embeddingSize];
        for (int i = 0; i < embeddingSize; i++) {
            result[i] = vec1[i] - vec2[i] + vec3[i];
        }

        // 找最相似的词
        String bestWord = null;
        double bestSim = Double.NEGATIVE_INFINITY;

        for (Map.Entry<String, double[]> entry : wordVectors.entrySet()) {
            if (!entry.getKey().equals(word1) && !entry.getKey().equals(word2) &&
                !entry.getKey().equals(word3)) {
                double sim = cosineSimilarity(result, entry.getValue());
                if (sim > bestSim) {
                    bestSim = sim;
                    bestWord = entry.getKey();
                }
            }
        }

        return bestWord;
    }

    /**
     * 获取词向量
     */
    public double[] getVector(String word) {
        return wordVectors.get(word);
    }

    /**
     * 打印词向量
     */
    public void printVector(String word) {
        double[] vec = wordVectors.get(word);
        if (vec != null) {
            System.out.printf("%s: [", word);
            for (int i = 0; i < Math.min(5, vec.length); i++) {
                System.out.printf("%.4f", vec[i]);
                if (i < Math.min(4, vec.length - 1)) System.out.print(", ");
            }
            if (vec.length > 5) System.out.print(", ...");
            System.out.println("]");
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 词嵌入演示 ===\n");

        // 创建词嵌入模型
        WordEmbeddings embeddings = new WordEmbeddings(50);

        // 初始化词汇表
        List<String> vocabulary = Arrays.asList(
            "king", "queen", "man", "woman", "prince", "princess",
            "boy", "girl", "father", "mother", "husband", "wife",
            "cat", "dog", "animal", "pet",
            "car", "bus", "vehicle", "transport"
        );
        embeddings.initializeVocabulary(vocabulary);

        // 模拟语义关系 (实际中这些向量是通过训练得到的)
        // 这里为了演示，手动调整一些向量的相似性
        Random rand = new Random(42);
        double[] baseVec = new double[50];

        // 为演示目的，创建有语义关系的向量
        // 在实际Word2Vec中，这些是通过训练自动学习的
        System.out.println("词向量示例:");
        embeddings.printVector("king");
        embeddings.printVector("queen");

        // 计算相似度
        System.out.println("\n=== 词相似度 ===");
        String[][] pairs = {
            {"king", "queen"},
            {"man", "woman"},
            {"cat", "dog"},
            {"car", "bus"},
            {"king", "cat"}
        };

        for (String[] pair : pairs) {
            double sim = embeddings.cosineSimilarity(
                embeddings.getVector(pair[0]),
                embeddings.getVector(pair[1])
            );
            System.out.printf("%-10s <-> %-10s: %.4f%n", pair[0], pair[1], sim);
        }

        // 找相似词
        System.out.println("\n=== 与'king'最相似的词 ===");
        List<Map.Entry<String, Double>> similar = embeddings.findSimilar("king", 5);
        for (Map.Entry<String, Double> entry : similar) {
            System.out.printf("  %s: %.4f%n", entry.getKey(), entry.getValue());
        }

        // 词向量运算
        System.out.println("\n=== 词向量类比 ===");
        System.out.println("king - man + woman = ?");

        // 说明Word2Vec的原理
        System.out.println("\n=== Word2Vec 原理 ===");
        System.out.println("1. Skip-gram: 给定中心词预测上下文");
        System.out.println("2. CBOW: 给定上下文预测中心词");
        System.out.println("3. 训练目标: 最大化似然函数");
        System.out.println("4. 结果: 语义相似的词在向量空间中距离相近");
        System.out.println("\n注: 本演示使用随机向量，实际应用中需要大规模语料训练");
    }
}

/**
 * 文本处理基础 - 自然语言处理
 * 包含分词、词频统计、文本向量化等
 */
package deep_learning.nlp;

import java.util.*;
import java.util.regex.*;

public class TextProcessing {

    /**
     * 分词 (简单空格分词)
     */
    public static List<String> tokenize(String text) {
        return Arrays.asList(text.toLowerCase().split("\\s+"));
    }

    /**
     * 移除标点符号
     */
    public static String removePunctuation(String text) {
        return text.replaceAll("[^a-zA-Z0-9\\s]", "");
    }

    /**
     * 词干提取 (简单后缀去除)
     */
    public static String stem(String word) {
        word = word.toLowerCase();
        if (word.endsWith("ing")) {
            word = word.substring(0, word.length() - 3);
        } else if (word.endsWith("ed")) {
            word = word.substring(0, word.length() - 2);
        } else if (word.endsWith("ly")) {
            word = word.substring(0, word.length() - 2);
        } else if (word.endsWith("s") && !word.endsWith("ss")) {
            word = word.substring(0, word.length() - 1);
        }
        return word;
    }

    /**
     * 停用词过滤
     */
    public static List<String> removeStopWords(List<String> tokens) {
        Set<String> stopWords = new HashSet<>(Arrays.asList(
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "shall",
            "should", "may", "might", "must", "can", "could", "i", "me", "my",
            "we", "our", "you", "your", "he", "him", "his", "she", "her", "it",
            "its", "they", "them", "their", "this", "that", "these", "those",
            "in", "on", "at", "to", "for", "with", "from", "by", "of", "and",
            "or", "but", "not", "no", "nor", "so", "yet", "both", "either",
            "neither", "each", "every", "all", "any", "few", "more", "most",
            "other", "some", "such", "than", "too", "very"
        ));

        List<String> filtered = new ArrayList<>();
        for (String token : tokens) {
            if (!stopWords.contains(token.toLowerCase())) {
                filtered.add(token);
            }
        }
        return filtered;
    }

    /**
     * 词频统计
     */
    public static Map<String, Integer> wordFrequency(List<String> tokens) {
        Map<String, Integer> freq = new HashMap<>();
        for (String token : tokens) {
            freq.put(token, freq.getOrDefault(token, 0) + 1);
        }
        return freq;
    }

    /**
     * TF-IDF 计算
     */
    public static Map<String, Double> tfidf(List<String> doc, List<List<String>> corpus) {
        Map<String, Integer> tf = wordFrequency(doc);
        Map<String, Double> tfidf = new HashMap<>();

        int docSize = doc.size();
        int corpusSize = corpus.size();

        for (Map.Entry<String, Integer> entry : tf.entrySet()) {
            String term = entry.getKey();
            double termFreq = (double) entry.getValue() / docSize;

            // 计算包含该词的文档数
            int docsWithTerm = 0;
            for (List<String> document : corpus) {
                if (document.contains(term)) {
                    docsWithTerm++;
                }
            }

            double idf = Math.log((double) corpusSize / (1 + docsWithTerm));
            tfidf.put(term, termFreq * idf);
        }

        return tfidf;
    }

    /**
     * 词袋模型 (Bag of Words)
     */
    public static int[] bagOfWords(List<String> tokens, List<String> vocabulary) {
        int[] bow = new int[vocabulary.size()];
        Map<String, Integer> wordToIndex = new HashMap<>();
        for (int i = 0; i < vocabulary.size(); i++) {
            wordToIndex.put(vocabulary.get(i), i);
        }

        for (String token : tokens) {
            Integer idx = wordToIndex.get(token);
            if (idx != null) {
                bow[idx]++;
            }
        }
        return bow;
    }

    /**
     * N-gram 生成
     */
    public static List<String> ngrams(List<String> tokens, int n) {
        List<String> ngrams = new ArrayList<>();
        for (int i = 0; i <= tokens.size() - n; i++) {
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < n; j++) {
                if (j > 0) sb.append(" ");
                sb.append(tokens.get(i + j));
            }
            ngrams.add(sb.toString());
        }
        return ngrams;
    }

    /**
     * 简单情感分析 (基于关键词)
     */
    public static double simpleSentiment(String text) {
        Set<String> positive = new HashSet<>(Arrays.asList(
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "happy", "joy", "beautiful", "perfect", "best"
        ));

        Set<String> negative = new HashSet<>(Arrays.asList(
            "bad", "terrible", "awful", "horrible", "hate", "dislike",
            "sad", "angry", "ugly", "worst", "poor", "disappointing"
        ));

        List<String> tokens = tokenize(removePunctuation(text));
        int posCount = 0, negCount = 0;

        for (String token : tokens) {
            if (positive.contains(token)) posCount++;
            if (negative.contains(token)) negCount++;
        }

        int total = posCount + negCount;
        if (total == 0) return 0;
        return (double) (posCount - negCount) / total;
    }

    public static void main(String[] args) {
        System.out.println("=== 文本处理演示 ===\n");

        String text = "The quick brown fox jumps over the lazy dog. " +
                      "The dog barked loudly at the fox.";

        // 分词
        List<String> tokens = tokenize(text);
        System.out.println("原始文本: " + text);
        System.out.println("分词结果: " + tokens);

        // 移除停用词
        List<String> filtered = removeStopWords(tokens);
        System.out.println("过滤停用词后: " + filtered);

        // 词干提取
        System.out.println("\n词干提取:");
        List<String> stemmed = new ArrayList<>();
        for (String token : filtered) {
            stemmed.add(stem(token));
        }
        System.out.println("词干结果: " + stemmed);

        // 词频统计
        System.out.println("\n词频统计:");
        Map<String, Integer> freq = wordFrequency(tokens);
        freq.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(5)
            .forEach(entry -> System.out.printf("  %s: %d%n", entry.getKey(), entry.getValue()));

        // N-gram
        System.out.println("\nBigrams:");
        List<String> bigrams = ngrams(tokens, 2);
        System.out.println(bigrams);

        System.out.println("\nTrigrams:");
        List<String> trigrams = ngrams(tokens, 3);
        System.out.println(trigrams);

        // 情感分析
        System.out.println("\n=== 情感分析 ===");
        String[] reviews = {
            "This movie is great and amazing!",
            "Terrible film, I hate it.",
            "It was okay, nothing special."
        };

        for (String review : reviews) {
            double sentiment = simpleSentiment(review);
            String label = sentiment > 0 ? "正面" : sentiment < 0 ? "负面" : "中性";
            System.out.printf("  \"%s\" -> %.2f (%s)%n", review, sentiment, label);
        }

        // TF-IDF 示例
        System.out.println("\n=== TF-IDF 示例 ===");
        List<List<String>> corpus = new ArrayList<>();
        corpus.add(tokenize("the cat sat on the mat"));
        corpus.add(tokenize("the dog sat on the log"));
        corpus.add(tokenize("cats and dogs are friends"));

        Map<String, Double> tfidf = tfidf(corpus.get(0), corpus);
        System.out.println("文档1的TF-IDF:");
        tfidf.entrySet().stream()
            .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
            .limit(5)
            .forEach(entry -> System.out.printf("  %s: %.4f%n", entry.getKey(), entry.getValue()));
    }
}

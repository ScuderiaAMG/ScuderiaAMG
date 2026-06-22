/**
 * Q-Learning 算法实现 - 强化学习
 * 经典的无模型强化学习算法
 */
package deep_learning.reinforcement_learning;

import java.util.Random;

public class QLearning {
    private int stateSize;
    private int actionSize;
    private double[][] qTable;
    private double learningRate;
    private double discountFactor;
    private double explorationRate;
    private double explorationDecay;
    private Random random;

    public QLearning(int stateSize, int actionSize, double learningRate,
                     double discountFactor, double explorationRate) {
        this.stateSize = stateSize;
        this.actionSize = actionSize;
        this.learningRate = learningRate;
        this.discountFactor = discountFactor;
        this.explorationRate = explorationRate;
        this.explorationDecay = 0.995;
        this.random = new Random(42);

        // 初始化Q表
        qTable = new double[stateSize][actionSize];
    }

    /**
     * 选择动作 (ε-贪婪策略)
     */
    public int chooseAction(int state) {
        if (random.nextDouble() < explorationRate) {
            // 探索: 随机选择动作
            return random.nextInt(actionSize);
        } else {
            // 利用: 选择Q值最大的动作
            int bestAction = 0;
            for (int a = 1; a < actionSize; a++) {
                if (qTable[state][a] > qTable[state][bestAction]) {
                    bestAction = a;
                }
            }
            return bestAction;
        }
    }

    /**
     * 更新Q值
     * Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
     */
    public void update(int state, int action, double reward, int nextState) {
        double maxNextQ = Double.NEGATIVE_INFINITY;
        for (int a = 0; a < actionSize; a++) {
            maxNextQ = Math.max(maxNextQ, qTable[nextState][a]);
        }

        double currentQ = qTable[state][action];
        double newQ = currentQ + learningRate *
                     (reward + discountFactor * maxNextQ - currentQ);
        qTable[state][action] = newQ;
    }

    /**
     * 衰减探索率
     */
    public void decayExploration() {
        explorationRate *= explorationDecay;
        explorationRate = Math.max(0.01, explorationRate);
    }

    /**
     * 打印Q表
     */
    public void printQTable() {
        System.out.println("Q-Table:");
        System.out.print("State\t");
        for (int a = 0; a < actionSize; a++) {
            System.out.printf("Action%d\t", a);
        }
        System.out.println();

        for (int s = 0; s < stateSize; s++) {
            System.out.printf("%d\t", s);
            for (int a = 0; a < actionSize; a++) {
                System.out.printf("%.2f\t", qTable[s][a]);
            }
            System.out.println();
        }
    }

    /**
     * 打印最优策略
     */
    public void printPolicy() {
        String[] actions = {"↑", "↓", "←", "→"};
        System.out.println("最优策略:");
        for (int s = 0; s < stateSize; s++) {
            int bestAction = 0;
            for (int a = 1; a < actionSize; a++) {
                if (qTable[s][a] > qTable[s][bestAction]) {
                    bestAction = a;
                }
            }
            System.out.printf("状态 %d: %s%n", s, actions[bestAction]);
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Q-Learning 算法演示 ===\n");
        System.out.println("网格世界: 4x4, 目标到达右下角");
        System.out.println("动作: 上(0), 下(1), 左(2), 右(3)\n");

        // 网格世界设置
        int gridSize = 4;
        int stateSize = gridSize * gridSize;
        int actionSize = 4;  // 上下左右
        int goalState = stateSize - 1;  // 右下角

        // 创建Q-Learning智能体
        QLearning agent = new QLearning(stateSize, actionSize, 0.1, 0.99, 1.0);

        // 训练
        int episodes = 1000;
        int maxSteps = 100;

        System.out.println("训练中...");
        for (int episode = 0; episode < episodes; episode++) {
            int state = 0;  // 从左上角开始
            int totalReward = 0;

            for (int step = 0; step < maxSteps; step++) {
                int action = agent.chooseAction(state);

                // 执行动作
                int nextState = executeAction(state, action, gridSize);
                double reward = getReward(nextState, goalState);

                // 更新Q值
                agent.update(state, action, reward, nextState);

                totalReward += reward;
                state = nextState;

                if (state == goalState) break;
            }

            agent.decayExploration();

            if (episode % 100 == 0) {
                System.out.printf("Episode %d, Total Reward: %.1f, Exploration: %.3f%n",
                    episode, totalReward, agent.explorationRate);
            }
        }

        // 打印结果
        System.out.println("\n训练完成!");
        agent.printQTable();
        System.out.println();
        agent.printPolicy();

        // 演示最优路径
        System.out.println("\n最优路径演示:");
        int state = 0;
        int steps = 0;
        String[] arrows = {"↑", "↓", "←", "→"};

        while (state != goalState && steps < 20) {
            int bestAction = 0;
            for (int a = 1; a < actionSize; a++) {
                if (agent.qTable[state][a] > agent.qTable[state][bestAction]) {
                    bestAction = a;
                }
            }
            System.out.printf("状态 %d -> %s -> ", state, arrows[bestAction]);
            state = executeAction(state, bestAction, gridSize);
            steps++;
        }
        System.out.printf("状态 %d (目标!)", state);
        System.out.printf("%n总步数: %d%n", steps);
    }

    /**
     * 执行动作，返回新状态
     */
    private static int executeAction(int state, int action, int gridSize) {
        int row = state / gridSize;
        int col = state % gridSize;

        switch (action) {
            case 0: row = Math.max(0, row - 1); break;      // 上
            case 1: row = Math.min(gridSize - 1, row + 1); break;  // 下
            case 2: col = Math.max(0, col - 1); break;      // 左
            case 3: col = Math.min(gridSize - 1, col + 1); break;  // 右
        }

        return row * gridSize + col;
    }

    /**
     * 获取奖励
     */
    private static double getReward(int state, int goalState) {
        if (state == goalState) return 100;  // 到达目标
        return -1;  // 每步小惩罚
    }
}

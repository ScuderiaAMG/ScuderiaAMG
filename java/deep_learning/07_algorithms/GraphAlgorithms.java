/**
 * 图算法实现 - 算法
 * 包含BFS、DFS、Dijkstra等经典图算法
 */
package deep_learning.algorithms;

import java.util.*;

public class GraphAlgorithms {
    private int vertices;
    private List<List<int[]>> adjacencyList;

    public GraphAlgorithms(int vertices) {
        this.vertices = vertices;
        this.adjacencyList = new ArrayList<>();
        for (int i = 0; i < vertices; i++) {
            adjacencyList.add(new ArrayList<>());
        }
    }

    /**
     * 添加边
     */
    public void addEdge(int source, int dest, int weight) {
        adjacencyList.get(source).add(new int[]{dest, weight});
        adjacencyList.get(dest).add(new int[]{source, weight});  // 无向图
    }

    /**
     * 广度优先搜索 (BFS)
     */
    public List<Integer> bfs(int start) {
        List<Integer> result = new ArrayList<>();
        boolean[] visited = new boolean[vertices];
        Queue<Integer> queue = new LinkedList<>();

        visited[start] = true;
        queue.offer(start);

        while (!queue.isEmpty()) {
            int vertex = queue.poll();
            result.add(vertex);

            for (int[] neighbor : adjacencyList.get(vertex)) {
                if (!visited[neighbor[0]]) {
                    visited[neighbor[0]] = true;
                    queue.offer(neighbor[0]);
                }
            }
        }

        return result;
    }

    /**
     * 深度优先搜索 (DFS)
     */
    public List<Integer> dfs(int start) {
        List<Integer> result = new ArrayList<>();
        boolean[] visited = new boolean[vertices];
        dfsHelper(start, visited, result);
        return result;
    }

    private void dfsHelper(int vertex, boolean[] visited, List<Integer> result) {
        visited[vertex] = true;
        result.add(vertex);

        for (int[] neighbor : adjacencyList.get(vertex)) {
            if (!visited[neighbor[0]]) {
                dfsHelper(neighbor[0], visited, result);
            }
        }
    }

    /**
     * Dijkstra 最短路径算法
     */
    public int[] dijkstra(int start) {
        int[] distances = new int[vertices];
        Arrays.fill(distances, Integer.MAX_VALUE);
        distances[start] = 0;

        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
        pq.offer(new int[]{start, 0});

        boolean[] visited = new boolean[vertices];

        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int vertex = current[0];
            int distance = current[1];

            if (visited[vertex]) continue;
            visited[vertex] = true;

            for (int[] neighbor : adjacencyList.get(vertex)) {
                int nextVertex = neighbor[0];
                int weight = neighbor[1];

                if (!visited[nextVertex] &&
                    distances[vertex] + weight < distances[nextVertex]) {
                    distances[nextVertex] = distances[vertex] + weight;
                    pq.offer(new int[]{nextVertex, distances[nextVertex]});
                }
            }
        }

        return distances;
    }

    /**
     * 检测环 (DFS)
     */
    public boolean hasCycle() {
        boolean[] visited = new boolean[vertices];
        boolean[] recursionStack = new boolean[vertices];

        for (int i = 0; i < vertices; i++) {
            if (hasCycleDFS(i, visited, recursionStack)) {
                return true;
            }
        }
        return false;
    }

    private boolean hasCycleDFS(int vertex, boolean[] visited, boolean[] recursionStack) {
        if (recursionStack[vertex]) return true;
        if (visited[vertex]) return false;

        visited[vertex] = true;
        recursionStack[vertex] = true;

        for (int[] neighbor : adjacencyList.get(vertex)) {
            if (hasCycleDFS(neighbor[0], visited, recursionStack)) {
                return true;
            }
        }

        recursionStack[vertex] = false;
        return false;
    }

    /**
     * 拓扑排序 (Kahn's Algorithm)
     */
    public List<Integer> topologicalSort() {
        int[] inDegree = new int[vertices];

        // 计算入度
        for (List<int[]> neighbors : adjacencyList) {
            for (int[] neighbor : neighbors) {
                inDegree[neighbor[0]]++;
            }
        }

        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < vertices; i++) {
            if (inDegree[i] == 0) {
                queue.offer(i);
            }
        }

        List<Integer> result = new ArrayList<>();
        while (!queue.isEmpty()) {
            int vertex = queue.poll();
            result.add(vertex);

            for (int[] neighbor : adjacencyList.get(vertex)) {
                inDegree[neighbor[0]]--;
                if (inDegree[neighbor[0]] == 0) {
                    queue.offer(neighbor[0]);
                }
            }
        }

        return result.size() == vertices ? result : new ArrayList<>();
    }

    /**
     * 打印图
     */
    public void printGraph() {
        System.out.println("邻接表:");
        for (int i = 0; i < vertices; i++) {
            System.out.printf("  %d -> ", i);
            for (int[] neighbor : adjacencyList.get(i)) {
                System.out.printf("(%d, %d) ", neighbor[0], neighbor[1]);
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        System.out.println("=== 图算法演示 ===\n");

        // 创建图
        GraphAlgorithms graph = new GraphAlgorithms(6);
        graph.addEdge(0, 1, 4);
        graph.addEdge(0, 2, 2);
        graph.addEdge(1, 2, 1);
        graph.addEdge(1, 3, 5);
        graph.addEdge(2, 3, 8);
        graph.addEdge(2, 4, 10);
        graph.addEdge(3, 4, 2);
        graph.addEdge(3, 5, 6);
        graph.addEdge(4, 5, 3);

        graph.printGraph();

        // BFS
        System.out.println("\nBFS (从顶点0): " + graph.bfs(0));

        // DFS
        System.out.println("DFS (从顶点0): " + graph.dfs(0));

        // Dijkstra
        System.out.println("\nDijkstra 最短路径 (从顶点0):");
        int[] distances = graph.dijkstra(0);
        for (int i = 0; i < distances.length; i++) {
            System.out.printf("  到顶点%d的最短距离: %d%n", i, distances[i]);
        }

        // 环检测
        System.out.println("\n图中是否有环: " + graph.hasCycle());

        // 拓扑排序 (需要有向无环图)
        GraphAlgorithms dag = new GraphAlgorithms(6);
        dag.addEdge(5, 2, 1);
        dag.addEdge(5, 0, 1);
        dag.addEdge(4, 0, 1);
        dag.addEdge(4, 1, 1);
        dag.addEdge(2, 3, 1);
        dag.addEdge(3, 1, 1);

        System.out.println("\nDAG 拓扑排序: " + dag.topologicalSort());
    }
}

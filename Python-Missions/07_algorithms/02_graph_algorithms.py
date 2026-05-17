#!/usr/bin/env python3
"""
图算法全集 —— 完整 Python 实现
涵盖：图的表示（邻接矩阵/邻接表/边列表）、BFS/DFS 及其应用、
      拓扑排序/Kahn算法、Dijkstra/Bellman-Ford/Floyd-Warshall/Johnson、
      Prim/Kruskal 最小生成树、强连通分量 (Kosaraju/Tarjan)、
      二分图匹配 (匈牙利算法)、网络流 (Ford-Fulkerson/Edmonds-Karp)、
      欧拉路径 (Hierholzer)、A* 搜索
"""

from collections import deque, defaultdict
import heapq
import math
from typing import Any, Iterator


# ============================================================
# §1  图的表示
# ============================================================

class Graph:
    """通用图类 —— 支持有向/无向、加权/无权。"""

    def __init__(self, directed: bool = False, weighted: bool = False) -> None:
        self.directed = directed
        self.weighted = weighted
        self.adj: dict[int, list[int | tuple[int, float]]] = defaultdict(list)
        self.vertices: set[int] = set()

    def add_vertex(self, v: int) -> None:
        self.vertices.add(v)

    def add_edge(self, u: int, v: int, weight: float = 1.0) -> None:
        self.vertices.add(u)
        self.vertices.add(v)
        if self.weighted:
            self.adj[u].append((v, weight))
            if not self.directed:
                self.adj[v].append((u, weight))
        else:
            self.adj[u].append(v)                # type: ignore[arg-type]
            if not self.directed:
                self.adj[v].append(u)            # type: ignore[arg-type]

    def neighbors(self, v: int) -> list[int] | list[tuple[int, float]]:
        return self.adj.get(v, [])

    def __len__(self) -> int:
        return len(self.vertices)

    @staticmethod
    def from_edges(edges: list[tuple[int, int]] | list[tuple[int, int, float]],
                   directed: bool = False, weighted: bool = False) -> "Graph":
        g = Graph(directed, weighted)
        for edge in edges:
            if len(edge) == 3:
                u, v, w = edge  # type: ignore[misc]
                g.add_edge(u, v, w)  # type: ignore[arg-type]
            else:
                u, v = edge  # type: ignore[misc]
                g.add_edge(u, v)  # type: ignore[arg-type]
        return g


# ============================================================
# §2  BFS (广度优先搜索)
# ============================================================

def bfs(graph: Graph, start: int) -> dict[int, int]:
    """BFS —— 返回从 start 到各节点的最短距离（无权图）。"""
    dist: dict[int, int] = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for edge in graph.neighbors(u):
            v = edge if isinstance(edge, int) else edge[0]
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def bfs_path(graph: Graph, start: int, end: int) -> list[int] | None:
    """BFS 找最短路径。"""
    parent: dict[int, int] = {}
    q = deque([start])
    visited = {start}

    while q:
        u = q.popleft()
        if u == end:
            path = [end]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return path[::-1]
        for edge in graph.neighbors(u):
            v = edge if isinstance(edge, int) else edge[0]
            if v not in visited:
                visited.add(v)
                parent[v] = u
                q.append(v)
    return None


def bfs_connected_components(graph: Graph) -> list[set[int]]:
    """BFS 找连通分量。"""
    visited: set[int] = set()
    components: list[set[int]] = []

    for v in graph.vertices:
        if v not in visited:
            comp: set[int] = set()
            q = deque([v])
            visited.add(v)
            while q:
                u = q.popleft()
                comp.add(u)
                for edge in graph.neighbors(u):
                    nxt = edge if isinstance(edge, int) else edge[0]
                    if nxt not in visited:
                        visited.add(nxt)
                        q.append(nxt)
            components.append(comp)
    return components


def bfs_bipartite_check(graph: Graph) -> bool:
    """BFS 检查二分图。"""
    color: dict[int, int] = {}
    for start in graph.vertices:
        if start not in color:
            q = deque([start])
            color[start] = 0
            while q:
                u = q.popleft()
                for edge in graph.neighbors(u):
                    v = edge if isinstance(edge, int) else edge[0]
                    if v not in color:
                        color[v] = 1 - color[u]
                        q.append(v)
                    elif color[v] == color[u]:
                        return False
    return True


# ============================================================
# §3  DFS (深度优先搜索)
# ============================================================

def dfs_iterative(graph: Graph, start: int) -> list[int]:
    """DFS 迭代版。"""
    visited: set[int] = set()
    order: list[int] = []
    stack = [start]

    while stack:
        u = stack.pop()
        if u not in visited:
            visited.add(u)
            order.append(u)
            for edge in reversed(graph.neighbors(u)):
                v = edge if isinstance(edge, int) else edge[0]
                if v not in visited:
                    stack.append(v)
    return order


def dfs_recursive(graph: Graph) -> tuple[list[int], dict[int, int], dict[int, int]]:
    """
    DFS 递归版 —— 返回 (访问顺序, 发现时间, 完成时间)。
    """
    visited: set[int] = set()
    order: list[int] = []
    discovery: dict[int, int] = {}
    finish: dict[int, int] = {}
    time = 0

    def dfs_visit(u: int) -> None:
        nonlocal time
        visited.add(u)
        order.append(u)
        time += 1
        discovery[u] = time

        for edge in graph.neighbors(u):
            v = edge if isinstance(edge, int) else edge[0]
            if v not in visited:
                dfs_visit(v)

        time += 1
        finish[u] = time

    for v in sorted(graph.vertices):
        if v not in visited:
            dfs_visit(v)

    return order, discovery, finish


def dfs_cycle_detection(graph: Graph) -> bool:
    """DFS 检测有向图中的环。"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[int, int] = {v: WHITE for v in graph.vertices}

    def dfs(v: int) -> bool:
        color[v] = GRAY
        for edge in graph.neighbors(v):
            u = edge if isinstance(edge, int) else edge[0]
            if color[u] == GRAY:
                return True
            if color[u] == WHITE and dfs(u):
                return True
        color[v] = BLACK
        return False

    for v in graph.vertices:
        if color[v] == WHITE:
            if dfs(v):
                return True
    return False


def dfs_topological_sort(graph: Graph) -> list[int]:
    """DFS 拓扑排序 —— 仅适用于 DAG。"""
    visited: set[int] = set()
    order: list[int] = []

    def dfs(v: int) -> None:
        visited.add(v)
        for edge in graph.neighbors(v):
            u = edge if isinstance(edge, int) else edge[0]
            if u not in visited:
                dfs(u)
        order.append(v)

    for v in sorted(graph.vertices):
        if v not in visited:
            dfs(v)

    return order[::-1]


# ============================================================
# §4  拓扑排序 (Kahn 算法)
# ============================================================

def kahn_topological_sort(graph: Graph) -> list[int] | None:
    """Kahn 算法 (基于入度) —— 返回排序列表或 None (有环时)。"""
    in_degree: dict[int, int] = {v: 0 for v in graph.vertices}

    for u in graph.vertices:
        for edge in graph.neighbors(u):
            v = edge if isinstance(edge, int) else edge[0]
            in_degree[v] += 1

    q = deque([v for v, d in in_degree.items() if d == 0])
    result: list[int] = []

    while q:
        u = q.popleft()
        result.append(u)
        for edge in graph.neighbors(u):
            v = edge if isinstance(edge, int) else edge[0]
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)

    return result if len(result) == len(graph.vertices) else None


# ============================================================
# §5  最短路径算法
# ============================================================

def dijkstra(graph: Graph, start: int) -> dict[int, float]:
    """Dijkstra 算法 —— O((V+E) log V)，仅适用于非负权图。"""
    dist: dict[int, float] = {v: float("inf") for v in graph.vertices}
    dist[start] = 0
    pq: list[tuple[float, int]] = [(0, start)]
    visited: set[int] = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        for edge in graph.neighbors(u):
            if isinstance(edge, int):
                v, w = edge, 1.0
            else:
                v, w = edge
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))

    return dist


def dijkstra_path(graph: Graph, start: int, end: int) -> tuple[list[int] | None, float]:
    """Dijkstra 并记录路径。"""
    dist: dict[int, float] = {v: float("inf") for v in graph.vertices}
    dist[start] = 0
    parent: dict[int, int] = {}
    pq = [(0, start)]
    visited: set[int] = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if u == end:
            break

        for edge in graph.neighbors(u):
            if isinstance(edge, int):
                v, w = edge, 1.0
            else:
                v, w = edge
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))

    if end not in parent and start != end:
        return None, float("inf")

    path = [end]
    while path[-1] != start:
        path.append(parent[path[-1]])
    return path[::-1], dist[end]


def bellman_ford(graph: Graph, start: int) -> dict[int, float] | None:
    """Bellman-Ford —— O(VE)，可处理负权边，检测负环。"""
    dist = {v: float("inf") for v in graph.vertices}
    dist[start] = 0

    edges: list[tuple[int, int, float]] = []
    for u in graph.vertices:
        for edge in graph.neighbors(u):
            if isinstance(edge, int):
                edges.append((u, edge, 1.0))
            else:
                edges.append((u, edge[0], edge[1]))

    V = len(graph.vertices)
    for _ in range(V - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break

    # 检测负环
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None

    return dist


def floyd_warshall(graph: Graph) -> dict[tuple[int, int], float]:
    """Floyd-Warshall —— O(V³)，全源最短路径。"""
    vertices = sorted(graph.vertices)
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    INF = float("inf")

    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0

    for u in graph.vertices:
        for edge in graph.neighbors(u):
            if isinstance(edge, int):
                v, w = edge, 1.0
            else:
                v, w = edge
            dist[idx[u]][idx[v]] = w

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return {(vertices[i], vertices[j]): dist[i][j]
            for i in range(n) for j in range(n)}


def johnson(graph: Graph) -> dict[tuple[int, int], float] | None:
    """Johnson 算法 —— O(V² log V + VE)，全源最短路径，可处理负权。"""
    # 添加虚拟节点
    g = Graph(directed=True, weighted=True)
    for v in graph.vertices:
        g.add_vertex(v)
    for u in graph.vertices:
        for edge in graph.neighbors(u):
            if isinstance(edge, int):
                g.add_edge(u, edge, 1.0)
            else:
                g.add_edge(u, edge[0], edge[1])
    dummy = max(graph.vertices) + 1 if graph.vertices else 0
    for v in graph.vertices:
        g.add_edge(dummy, v, 0)

    h = bellman_ford(g, dummy)
    if h is None:
        return None

    # 重新赋权并运行 Dijkstra
    all_pairs: dict[tuple[int, int], float] = {}
    for u in graph.vertices:
        d = dijkstra(g, u)
        for v in graph.vertices:
            all_pairs[(u, v)] = d[v] + h[v] - h[u]

    return all_pairs


# ============================================================
# §6  最小生成树
# ============================================================

def prim_mst(graph: Graph) -> tuple[list[tuple[int, int, float]], float]:
    """Prim 算法 —— O(E log V)，返回 (MST边列表, 总权重)。"""
    if not graph.vertices:
        return [], 0.0
    start = next(iter(graph.vertices))
    visited: set[int] = set()
    mst_edges: list[tuple[int, int, float]] = []
    total_weight = 0.0

    pq: list[tuple[float, int, int, int]] = [(0, start, start, -1)]

    while pq and len(visited) < len(graph.vertices):
        w, u, v, parent = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)
        if parent >= 0:
            mst_edges.append((parent, v, w))
        total_weight += w

        for edge in graph.neighbors(v):
            nxt = edge if isinstance(edge, int) else edge[0]
            weight = 1.0 if isinstance(edge, int) else edge[1]
            if nxt not in visited:
                heapq.heappush(pq, (weight, v, nxt, v))

    return mst_edges, total_weight


class DisjointSet:
    """并查集 —— 用于 Kruskal 算法。"""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            self.parent[px] = py
        elif self.rank[px] > self.rank[py]:
            self.parent[py] = px
        else:
            self.parent[py] = px
            self.rank[px] += 1
        return True


def kruskal_mst(graph: Graph) -> tuple[list[tuple[int, int, float]], float]:
    """Kruskal 算法 —— O(E log E)。"""
    edges: list[tuple[float, int, int]] = []
    for u in graph.vertices:
        for edge in graph.neighbors(u):
            if isinstance(edge, int):
                v, w = edge, 1.0
            else:
                v, w = edge
            if u < v or graph.directed:
                edges.append((w, u, v))

    edges.sort(key=lambda x: x[0])

    # 顶点到并查集索引的映射
    verts = sorted(graph.vertices)
    v2i = {v: i for i, v in enumerate(verts)}
    dsu = DisjointSet(len(verts))

    mst: list[tuple[int, int, float]] = []
    total = 0.0
    for w, u, v in edges:
        if dsu.union(v2i[u], v2i[v]):
            mst.append((u, v, w))
            total += w
            if len(mst) == len(verts) - 1:
                break

    return mst, total


# ============================================================
# §7  强连通分量
# ============================================================

def kosaraju_scc(graph: Graph) -> list[set[int]]:
    """Kosaraju 算法 —— 求有向图的所有强连通分量。"""
    visited: set[int] = set()
    finish_order: list[int] = []

    def dfs1(v: int) -> None:
        visited.add(v)
        for edge in graph.neighbors(v):
            u = edge if isinstance(edge, int) else edge[0]
            if u not in visited:
                dfs1(u)
        finish_order.append(v)

    for v in graph.vertices:
        if v not in visited:
            dfs1(v)

    # 构建反向图
    rev = Graph(directed=True)
    for v in graph.vertices:
        rev.add_vertex(v)
    for u in graph.vertices:
        for edge in graph.neighbors(u):
            v = edge if isinstance(edge, int) else edge[0]
            rev.add_edge(v, u)

    visited.clear()
    sccs: list[set[int]] = []

    def dfs2(v: int, comp: set[int]) -> None:
        visited.add(v)
        comp.add(v)
        for edge in rev.neighbors(v):
            u = edge if isinstance(edge, int) else edge[0]
            if u not in visited:
                dfs2(u, comp)

    for v in reversed(finish_order):
        if v not in visited:
            comp: set[int] = set()
            dfs2(v, comp)
            sccs.append(comp)

    return sccs


def tarjan_scc(graph: Graph) -> list[set[int]]:
    """Tarjan 算法 —— 单次 DFS 求 SCC。"""
    index_counter = 0
    indices: dict[int, int] = {}
    lowlink: dict[int, int] = {}
    on_stack: set[int] = set()
    stack: list[int] = []
    sccs: list[set[int]] = []

    def strongconnect(v: int) -> None:
        nonlocal index_counter
        indices[v] = index_counter
        lowlink[v] = index_counter
        index_counter += 1
        stack.append(v)
        on_stack.add(v)

        for edge in graph.neighbors(v):
            w = edge if isinstance(edge, int) else edge[0]
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            comp: set[int] = set()
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.add(w)
                if w == v:
                    break
            sccs.append(comp)

    for v in graph.vertices:
        if v not in indices:
            strongconnect(v)

    return sccs


# ============================================================
# §8  网络流
# ============================================================

class FlowGraph:
    """支持网络流的残差图。"""

    def __init__(self, n: int) -> None:
        self.n = n
        self.adj: list[list[int]] = [[] for _ in range(n)]
        self.capacity: dict[tuple[int, int], float] = {}
        self.flow: dict[tuple[int, int], float] = defaultdict(float)

    def add_edge(self, u: int, v: int, cap: float) -> None:
        self.adj[u].append(v)
        self.adj[v].append(u)
        self.capacity[(u, v)] = cap
        self.capacity[(v, u)] = 0


def edmonds_karp(graph: FlowGraph, source: int, sink: int) -> float:
    """Edmonds-Karp (BFS 增广) —— O(VE²)。"""
    total_flow = 0.0

    while True:
        parent: dict[int, int] = {}
        q = deque([source])
        visited = {source}

        while q:
            u = q.popleft()
            if u == sink:
                break
            for v in graph.adj[u]:
                if v not in visited:
                    residual = graph.capacity.get((u, v), 0) - graph.flow[(u, v)]
                    if residual > 0:
                        visited.add(v)
                        parent[v] = u
                        q.append(v)

        if sink not in parent:
            break

        # 找瓶颈容量
        bottleneck = float("inf")
        v = sink
        while v != source:
            u = parent[v]
            residual = graph.capacity.get((u, v), 0) - graph.flow[(u, v)]
            bottleneck = min(bottleneck, residual)
            v = u

        # 增广
        v = sink
        while v != source:
            u = parent[v]
            graph.flow[(u, v)] += bottleneck
            graph.flow[(v, u)] -= bottleneck
            v = u

        total_flow += bottleneck

    return total_flow


def dinic_max_flow(graph: FlowGraph, source: int, sink: int) -> float:
    """Dinic 算法 —— O(V²E)。"""
    total_flow = 0.0

    def bfs_level() -> list[int]:
        level = [-1] * graph.n
        q = deque([source])
        level[source] = 0
        while q:
            u = q.popleft()
            for v in graph.adj[u]:
                if level[v] == -1 and graph.capacity.get((u, v), 0) - graph.flow[(u, v)] > 0:
                    level[v] = level[u] + 1
                    q.append(v)
        return level

    def dfs(u: int, pushed: float, level: list[int], ptr: list[int]) -> float:
        if u == sink:
            return pushed
        while ptr[u] < len(graph.adj[u]):
            v = graph.adj[u][ptr[u]]
            if level[v] == level[u] + 1:
                residual = graph.capacity.get((u, v), 0) - graph.flow[(u, v)]
                if residual > 0:
                    tr = dfs(v, min(pushed, residual), level, ptr)
                    if tr > 0:
                        graph.flow[(u, v)] += tr
                        graph.flow[(v, u)] -= tr
                        return tr
            ptr[u] += 1
        return 0.0

    while True:
        level = bfs_level()
        if level[sink] == -1:
            break
        ptr = [0] * graph.n
        while True:
            pushed = dfs(source, float("inf"), level, ptr)
            if pushed == 0:
                break
            total_flow += pushed

    return total_flow


# ============================================================
# §9  其他重要算法
# ============================================================

def hierholzer_eulerian_path(graph: Graph) -> list[int] | None:
    """Hierholzer 算法 —— 求无向图的欧拉路径/回路。"""
    if not graph.vertices:
        return []
    # 检查度数
    odd_vertices = []
    for v in graph.vertices:
        deg = len(graph.neighbors(v))
        if deg % 2 == 1:
            odd_vertices.append(v)
    if len(odd_vertices) not in (0, 2):
        return None

    start = odd_vertices[0] if odd_vertices else next(iter(graph.vertices))

    # Hierholzer 算法
    adj_copy: dict[int, list[int]] = {}
    for v in graph.vertices:
        adj_copy[v] = []
        for edge in graph.neighbors(v):
            adj_copy[v].append(edge if isinstance(edge, int) else edge[0])

    stack = [start]
    circuit: list[int] = []

    while stack:
        v = stack[-1]
        if adj_copy[v]:
            u = adj_copy[v].pop()
            adj_copy[u].remove(v)
            stack.append(u)
        else:
            circuit.append(stack.pop())

    return circuit


def hungarian_bipartite_matching(n: int, m: int,
                                  edges: list[tuple[int, int]]) -> int:
    """匈牙利算法 —— 求二分图最大匹配，O(VE)。"""
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)

    match_r = [-1] * m

    def dfs(u: int, seen: list[bool]) -> bool:
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                if match_r[v] == -1 or dfs(match_r[v], seen):
                    match_r[v] = u
                    return True
        return False

    result = 0
    for u in range(n):
        seen = [False] * m
        if dfs(u, seen):
            result += 1
    return result


def a_star(graph: Graph, start: int, goal: int,
           heuristic: dict[int, float]) -> list[int] | None:
    """A* 搜索 —— 使用启发式函数的最短路径搜索。"""
    open_set: list[tuple[float, int]] = [(heuristic.get(start, 0), start)]
    came_from: dict[int, int] = {}
    g_score: dict[int, float] = {v: float("inf") for v in graph.vertices}
    g_score[start] = 0
    visited: set[int] = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(came_from[path[-1]])
            return path[::-1]

        for edge in graph.neighbors(current):
            if isinstance(edge, int):
                neighbor, weight = edge, 1.0
            else:
                neighbor, weight = edge
            tentative_g = g_score[current] + weight
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic.get(neighbor, 0)
                heapq.heappush(open_set, (f, neighbor))

    return None


# ============================================================
# §10  演示
# ============================================================

def demo_graph_algorithms() -> None:
    print("=" * 60)
    print("图算法全集演示")
    print("=" * 60)

    # 构建示例图
    g = Graph(directed=False, weighted=True)
    edges = [(0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 11),
             (2, 3, 7), (2, 5, 4), (2, 8, 2), (3, 4, 9),
             (3, 5, 14), (4, 5, 10), (5, 6, 2), (6, 7, 1),
             (6, 8, 6), (7, 8, 7)]
    for u, v, w in edges:
        g.add_edge(u, v, w)

    print(f"图: {len(g.vertices)} 个顶点, {len(edges)} 条边")

    # BFS
    dist_bfs = bfs(g, 0)
    print(f"BFS(0) 距离: {dict(sorted(dist_bfs.items()))}")

    # DFS
    dfs_order, _, _ = dfs_recursive(g)
    print(f"DFS 顺序: {dfs_order}")

    # Dijkstra
    d_dist = dijkstra(g, 0)
    print(f"Dijkstra(0): {dict(sorted(d_dist.items()))}")

    # Dijkstra path
    path, path_dist = dijkstra_path(g, 0, 4)
    print(f"Dijkstra path 0->4: {path} (distance={path_dist})")

    # MST
    mst_edges, mst_weight = prim_mst(g)
    print(f"Prim MST 权重: {mst_weight}, 边: {mst_edges}")
    k_edges, k_weight = kruskal_mst(g)
    print(f"Kruskal MST 权重: {k_weight}")

    # DAG 拓扑排序
    dag = Graph(directed=True)
    for u, v in [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]:
        dag.add_edge(u, v)
    topo_dfs = dfs_topological_sort(dag)
    topo_kahn = kahn_topological_sort(dag)
    print(f"\n拓扑排序 (DFS):  {topo_dfs}")
    print(f"拓扑排序 (Kahn): {topo_kahn}")

    # SCC
    scc_graph = Graph(directed=True)
    for u, v in [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]:
        scc_graph.add_edge(u, v)
    kos_sccs = kosaraju_scc(scc_graph)
    tar_sccs = tarjan_scc(scc_graph)
    print(f"\nSCC (Kosaraju): {[sorted(s) for s in kos_sccs]}")
    print(f"SCC (Tarjan):   {[sorted(s) for s in tar_sccs]}")

    # 网络流
    fg = FlowGraph(6)
    for u, v, c in [(0, 1, 16), (0, 2, 13), (1, 2, 10), (1, 3, 12),
                     (2, 1, 4), (2, 4, 14), (3, 2, 9), (3, 5, 20),
                     (4, 3, 7), (4, 5, 4)]:
        fg.add_edge(u, v, c)
    flow = edmonds_karp(fg, 0, 5)
    print(f"\n最大流 (Edmonds-Karp): {flow}")

    fg2 = FlowGraph(6)
    for u, v, c in [(0, 1, 16), (0, 2, 13), (1, 2, 10), (1, 3, 12),
                     (2, 1, 4), (2, 4, 14), (3, 2, 9), (3, 5, 20),
                     (4, 3, 7), (4, 5, 4)]:
        fg2.add_edge(u, v, c)
    flow2 = dinic_max_flow(fg2, 0, 5)
    print(f"最大流 (Dinic): {flow2}")

    # 二分图
    bipartite = Graph()
    for u, v in [(0, 3), (0, 4), (1, 3), (1, 5), (2, 4)]:
        bipartite.add_edge(u, v)
    is_bip = bfs_bipartite_check(bipartite)
    print(f"\n二分图检查: {is_bip}")

    # 匈牙利算法
    match_count = hungarian_bipartite_matching(3, 3,
                                                [(0, 0), (0, 1), (1, 0), (1, 2), (2, 1)])
    print(f"匈牙利算法 最大匹配: {match_count}")

    # A*
    grid_graph = Graph(weighted=True)
    heuristic = {0: 10, 1: 8, 2: 5, 3: 7, 4: 3, 5: 0}
    for u, v, w in [(0, 1, 2), (0, 3, 3), (1, 2, 4), (1, 4, 1),
                     (2, 5, 2), (3, 4, 5), (4, 5, 3)]:
        grid_graph.add_edge(u, v, w)
    a_path = a_star(grid_graph, 0, 5, heuristic)
    print(f"\nA* 搜索 0->5: {a_path}")


if __name__ == "__main__":
    demo_graph_algorithms()
    print("\n✅ 图算法篇执行完毕!")

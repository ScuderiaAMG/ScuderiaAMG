#!/usr/bin/env python3
"""
Python 高级 —— 并发编程
涵盖：threading、multiprocessing、concurrent.futures、asyncio
每个部分都附带可运行的完整示例
"""

import threading
import multiprocessing
import concurrent.futures
import asyncio
import time
import random
import math
import queue
from typing import Any, Callable, Iterable, Iterator


# ============================================================
# §1  threading — 多线程
# ============================================================

class Counter:
    """线程不安全的计数器（演示竞态条件）。"""

    def __init__(self) -> None:
        self.value = 0

    def increment(self, n: int = 100000) -> None:
        for _ in range(n):
            self.value += 1


class SafeCounter:
    """线程安全的计数器（使用 Lock）。"""

    def __init__(self) -> None:
        self.value = 0
        self.lock = threading.Lock()

    def increment(self, n: int = 100000) -> None:
        for _ in range(n):
            with self.lock:
                self.value += 1  # 临界区

    def increment_atomic(self, n: int = 100000) -> None:
        """使用原子加法避免每次迭代加锁的开销。"""
        local = 0
        for _ in range(n):
            local += 1
        with self.lock:
            self.value += local


def demo_threading_basics() -> None:
    print("=" * 60)
    print("§1  threading — 多线程")
    print("=" * 60)

    # 竞态条件演示
    c_unsafe = Counter()
    threads = [
        threading.Thread(target=c_unsafe.increment, args=(50000,))
        for _ in range(4)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"不安全计数器 (期望 200000): {c_unsafe.value}")

    # 安全版本
    c_safe = SafeCounter()
    threads = [
        threading.Thread(target=c_safe.increment, args=(50000,))
        for _ in range(4)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"安全计数器   (期望 200000): {c_safe.value}")


# ============================================================
# §2  threading 同步原语
# ============================================================

def demo_threading_primitives() -> None:
    print("\n" + "=" * 60)
    print("§2  threading 同步原语")
    print("=" * 60)

    # ---- Lock 与 RLock ----
    rlock = threading.RLock()

    def recursive_func(depth: int) -> None:
        with rlock:
            if depth > 0:
                recursive_func(depth - 1)
    recursive_func(3)                            # RLock 允许同一线程重入
    print("RLock 重入成功 (深度 3)")

    # ---- Semaphore ----
    semaphore = threading.Semaphore(2)           # 最多 2 个线程同时访问
    active = 0
    active_lock = threading.Lock()

    def limited_access(worker_id: int) -> None:
        nonlocal active
        with semaphore:
            with active_lock:
                active += 1
                print(f"  Worker {worker_id} 获得许可 (active={active})")
            time.sleep(0.1)
            with active_lock:
                active -= 1

    threads = [threading.Thread(target=limited_access, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # ---- Event ----
    event = threading.Event()
    results_data: list[str] = []

    def waiter(name: str) -> None:
        print(f"  {name} 等待事件...")
        event.wait()
        results_data.append(name)

    def setter() -> None:
        time.sleep(0.1)
        print(f"  触发事件!")
        event.set()

    t1 = threading.Thread(target=waiter, args=("A",))
    t2 = threading.Thread(target=waiter, args=("B",))
    t3 = threading.Thread(target=setter)
    for t in [t1, t2, t3]:
        t.start()
    for t in [t1, t2, t3]:
        t.join()
    print(f"  被唤醒: {results_data}")

    # ---- Condition ----
    cond = threading.Condition()
    items: list[int] = []

    def producer() -> None:
        for i in range(5):
            with cond:
                items.append(i)
                print(f"  生产: {i}")
                cond.notify()
            time.sleep(0.05)

    def consumer() -> None:
        consumed: list[int] = []
        while len(consumed) < 5:
            with cond:
                while not items:
                    cond.wait()
                val = items.pop(0)
                consumed.append(val)
                print(f"  消费: {val}")
        print(f"  消费完毕: {consumed}")

    tp = threading.Thread(target=producer)
    tc = threading.Thread(target=consumer)
    tc.start()
    tp.start()
    tp.join()
    tc.join()

    # ---- Barrier ----
    barrier = threading.Barrier(3, action=lambda: print("  所有线程到达屏障!"))

    def racer(idx: int) -> None:
        print(f"  选手 {idx} 到达")
        barrier.wait()
        print(f"  选手 {idx} 继续")

    threads = [threading.Thread(target=racer, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ============================================================
# §3  线程池 (concurrent.futures.ThreadPoolExecutor)
# ============================================================

def slow_task(task_id: int, duration: float = 0.1) -> dict[str, Any]:
    """模拟 I/O 密集型任务（线程池适用）。"""
    time.sleep(duration)
    return {"task_id": task_id, "result": task_id ** 2, "thread": threading.current_thread().name}


def demo_thread_pool() -> None:
    print("\n" + "=" * 60)
    print("§3  ThreadPoolExecutor")
    print("=" * 60)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="Worker") as executor:
        # submit — 单个提交
        futures = [executor.submit(slow_task, i, random.uniform(0.05, 0.2))
                   for i in range(10)]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(f"  submit 完成: {result}")

    # map — 批量提交（保持顺序）
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(slow_task, range(5), [0.05] * 5)
        print("\nmap 结果:")
        for r in results:
            print(f"  {r}")


# ============================================================
# §4  multiprocessing — 多进程
# ============================================================

def cpu_bound_task(n: int) -> int:
    """CPU 密集型任务（多进程适用）。"""
    return sum(math.factorial(i % 10 + 1) for i in range(n * 1000))


def demo_multiprocessing() -> None:
    print("\n" + "=" * 60)
    print("§4  multiprocessing — 多进程")
    print("=" * 60)

    inputs = [10, 15, 20, 25]

    # 串行
    t0 = time.perf_counter()
    serial_results = [cpu_bound_task(n) for n in inputs]
    serial_time = time.perf_counter() - t0
    print(f"串行时间: {serial_time*1000:.1f} ms")

    # 多进程 — Process 类
    processes: list[multiprocessing.Process] = []
    for n in inputs:
        p = multiprocessing.Process(target=cpu_bound_task, args=(n,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

    # 进程池
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        t0 = time.perf_counter()
        parallel_results = list(executor.map(cpu_bound_task, inputs))
        parallel_time = time.perf_counter() - t0
    print(f"并行时间: {parallel_time*1000:.1f} ms, speedup={serial_time/parallel_time:.2f}x")

    # 进程间通信：Queue
    def producer(q: multiprocessing.Queue[tuple[int, str]]) -> None:
        for i in range(5):
            q.put((i, f"msg_{i}"))
        q.put((-1, "DONE"))                      # 哨兵

    def consumer(q: multiprocessing.Queue[tuple[int, str]]) -> None:
        while True:
            idx, msg = q.get()
            if idx == -1:
                break
            print(f"  Queue 收到: ({idx}, {msg})")

    q: multiprocessing.Queue[tuple[int, str]] = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=producer, args=(q,))
    p2 = multiprocessing.Process(target=consumer, args=(q,))
    p2.start()
    p1.start()
    p1.join()
    p2.join()

    # 共享内存 Value / Array
    shared_counter = multiprocessing.Value("i", 0)   # 有符号 int
    shared_array = multiprocessing.Array("d", [0.0, 0.0, 0.0])  # double 数组

    def increment_shared(val: Any, arr: Any) -> None:
        for _ in range(1000):
            with val.get_lock():
                val.value += 1

    processes = [multiprocessing.Process(target=increment_shared,
                                          args=(shared_counter, shared_array))
                 for _ in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print(f"共享 Value 结果 (期望 4000): {shared_counter.value}")


# ============================================================
# §5  asyncio — 异步编程
# ============================================================

async def async_task(name: str, delay: float) -> str:
    """模拟异步 I/O 操作。"""
    await asyncio.sleep(delay)
    return f"Task({name}) done in {delay:.2f}s"


async def coroutine_demo() -> None:
    """演示基本的 await / create_task / gather。"""
    # 串行等待
    t0 = time.perf_counter()
    r1 = await async_task("serial-1", 0.1)
    r2 = await async_task("serial-2", 0.1)
    print(f"串行: {(time.perf_counter()-t0)*1000:.0f}ms -> {r1}, {r2}")

    # 并发 gather
    t0 = time.perf_counter()
    results = await asyncio.gather(
        async_task("gather-1", 0.1),
        async_task("gather-2", 0.1),
        async_task("gather-3", 0.1),
    )
    print(f"gather: {(time.perf_counter()-t0)*1000:.0f}ms -> {results}")

    # create_task + await
    t0 = time.perf_counter()
    tasks = [asyncio.create_task(async_task(f"task-{i}", 0.1)) for i in range(5)]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    first = list(done)[0]
    print(f"FIRST_COMPLETED: {await first}")

    # 取消剩余
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    print(f"取消 {len(pending)} 个任务")

    # as_completed
    tasks2 = [async_task(f"iter-{i}", random.uniform(0.05, 0.2)) for i in range(5)]
    for coro in asyncio.as_completed(tasks2):
        result = await coro
        print(f"  as_completed: {result}")

    # TaskGroup (Python 3.11+)
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(async_task("tg-1", 0.05))
        t2 = tg.create_task(async_task("tg-2", 0.08))
    print(f"TaskGroup 完成: {t1.result()}, {t2.result()}")


# ============================================================
# §6  asyncio 进阶 — 队列、事件、同步原语
# ============================================================

async def producer_consumer_demo() -> None:
    """asyncio.Queue 实现异步生产者-消费者。"""
    q: asyncio.Queue[int] = asyncio.Queue(maxsize=3)

    async def producer() -> None:
        for i in range(10):
            await q.put(i)
            print(f"  生产 {i}")
            await asyncio.sleep(0.02)

    async def consumer(name: str) -> None:
        while True:
            try:
                val = await asyncio.wait_for(q.get(), timeout=0.3)
                print(f"  消费者 {name}: {val}")
                await asyncio.sleep(0.05)
                q.task_done()
            except asyncio.TimeoutError:
                print(f"  消费者 {name} 超时退出")
                break

    prod = asyncio.create_task(producer())
    consumers = [asyncio.create_task(consumer(f"C{i}")) for i in range(3)]
    await prod
    await asyncio.gather(*consumers)


async def async_server_simulation() -> None:
    """模拟异步 HTTP 服务器处理请求。"""
    async def handle_request(client_id: int) -> str:
        # 模拟数据库查询
        await asyncio.sleep(random.uniform(0.03, 0.12))
        return f"Response for client {client_id}"

    requests = [handle_request(i) for i in range(20)]
    t0 = time.perf_counter()
    responses = await asyncio.gather(*requests)
    elapsed = time.perf_counter() - t0
    print(f"处理 {len(requests)} 个请求耗时: {elapsed*1000:.1f} ms")
    print(f"  示例响应: {responses[0]}")


def demo_asyncio() -> None:
    print("\n" + "=" * 60)
    print("§5-6  asyncio 异步编程")
    print("=" * 60)

    print("\n--- 基础 ---")
    asyncio.run(coroutine_demo())

    print("\n--- Producer-Consumer ---")
    asyncio.run(producer_consumer_demo())

    print("\n--- 模拟服务器 ---")
    asyncio.run(async_server_simulation())


# ============================================================
# §7  asyncio + 线程混合
# ============================================================

def sync_blocking_io(duration: float) -> str:
    """模拟阻塞 I/O（如传统的文件读取、数据库驱动）。"""
    time.sleep(duration)
    return f"sync result ({duration}s)"


async def async_with_thread_pool() -> None:
    """使用 run_in_executor 在线程池中运行阻塞代码。"""
    loop = asyncio.get_running_loop()

    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks = [
            loop.run_in_executor(pool, sync_blocking_io, 0.1)
            for _ in range(6)
        ]
        results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - t0
    print(f"run_in_executor 并行 6 x 0.1s: {elapsed*1000:.0f} ms (期望 ~100ms)")
    print(f"  结果: {results[:3]}...")


def demo_async_thread_hybrid() -> None:
    print("\n" + "=" * 60)
    print("§7  asyncio + Thread 混合")
    print("=" * 60)
    asyncio.run(async_with_thread_pool())


# ============================================================
# §8  并发模式总结
# ============================================================

def demo_comparison() -> None:
    print("\n" + "=" * 60)
    print("§8  并发模式对比")
    print("=" * 60)

    num_tasks = 8

    # 串行
    t0 = time.perf_counter()
    for _ in range(num_tasks):
        time.sleep(0.05)
    serial = time.perf_counter() - t0

    # 线程池 (I/O-bound)
    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_tasks) as ex:
        list(ex.map(lambda _: time.sleep(0.05), range(num_tasks)))
    thread_pool = time.perf_counter() - t0

    # 进程池 (CPU-bound)
    def burn(iterations: int) -> None:
        sum(i ** 2 for i in range(iterations))
    t0 = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as ex:
        list(ex.map(burn, [5000] * num_tasks))
    proc_pool = time.perf_counter() - t0

    # asyncio
    async def run():
        t0 = time.perf_counter()
        await asyncio.gather(*[asyncio.sleep(0.05) for _ in range(num_tasks)])
        return time.perf_counter() - t0

    async_time = asyncio.run(run())

    print(f"{'模式':<20} {'耗时(ms)':>10} {'适用场景'}")
    print(f"{'serial':<20} {serial*1000:>10.1f} 任何场景")
    print(f"{'thread pool':<20} {thread_pool*1000:>10.1f} I/O 密集型")
    print(f"{'process pool':<20} {proc_pool*1000:>10.1f} CPU 密集型")
    print(f"{'asyncio':<20} {async_time*1000:>10.1f} 高并发 I/O")


if __name__ == "__main__":
    demo_threading_basics()
    demo_threading_primitives()
    demo_thread_pool()
    demo_multiprocessing()
    demo_asyncio()
    demo_async_thread_hybrid()
    demo_comparison()
    print("\n✅ 并发编程篇全部执行完毕!")

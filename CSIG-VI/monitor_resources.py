import psutil
import gpustat
import time
import threading

class ResourceMonitor:
    def __init__(self, interval=60):
        self.interval = interval
        self.monitoring = False
        
    def get_system_stats(self):
        """获取系统资源统计"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / (1024**3),
            'disk_percent': disk.percent,
        }
        
        return stats
    
    def get_gpu_stats(self):
        """获取GPU统计"""
        try:
            gpu_stats = gpustat.GPUStatCollection.new_query()
            stats = []
            for gpu in gpu_stats:
                stats.append({
                    'gpu_id': gpu.index,
                    'gpu_utilization': gpu.utilization,
                    'memory_used_mb': gpu.memory_used,
                    'memory_total_mb': gpu.memory_total,
                    'temperature': gpu.temperature
                })
            return stats
        except:
            return []
    
    def monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            system_stats = self.get_system_stats()
            gpu_stats = self.get_gpu_stats()
            
            print(f"\n=== 资源监控 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
            print(f"CPU使用率: {system_stats['cpu_percent']}%")
            print(f"内存使用: {system_stats['memory_used_gb']:.1f} GB ({system_stats['memory_percent']}%)")
            
            for gpu in gpu_stats:
                print(f"GPU{gpu['gpu_id']}: 使用率 {gpu['gpu_utilization']}%, "
                      f"显存 {gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB, "
                      f"温度 {gpu['temperature']}°C")
            
            time.sleep(self.interval)
    
    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False

# 使用示例
if __name__ == "__main__":
    monitor = ResourceMonitor(interval=30)  # 每30秒监控一次
    monitor.start_monitoring()
    
    # 主程序运行期间保持监控
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
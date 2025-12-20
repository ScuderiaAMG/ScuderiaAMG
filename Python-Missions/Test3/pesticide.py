class PesticideManager:
    def __init__(self):
        self.available_chemicals = {
            "杀虫剂": {"effectiveness": 0.8, "cost": 10, "environment_impact": 0.7},
            "杀菌剂": {"effectiveness": 0.9, "cost": 12, "environment_impact": 0.6},
            "除草剂": {"effectiveness": 0.7, "cost": 8, "environment_impact": 0.8},
            "生长调节剂": {"effectiveness": 0.5, "cost": 15, "environment_impact": 0.4}
        }
    
    def create_custom_mix(self):
        # 在实际应用中，这里会有更复杂的逻辑
        # 现在只是返回一个随机配置
        import random
        chemicals = random.sample(list(self.available_chemicals.keys()), 2)
        return {
            "chemicals": chemicals,
            "effectiveness": sum(self.available_chemicals[c]["effectiveness"] for c in chemicals) / 2,
            "cost": sum(self.available_chemicals[c]["cost"] for c in chemicals),
            "environment_impact": sum(self.available_chemicals[c]["environment_impact"] for c in chemicals) / 2
        }
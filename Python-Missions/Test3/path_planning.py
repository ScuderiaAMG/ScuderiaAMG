class PathPlanner:
    def __init__(self):
        pass
    
    def plan_path(self, field):
        # 简单的路径规划：覆盖整个农田的网格路径
        path = []
        spacing = 30
        direction = 1  # 1表示向右，-1表示向左
        
        for y in range(field.y + 20, field.y + field.height - 20, spacing):
            if direction == 1:
                for x in range(field.x + 20, field.x + field.width - 20, spacing):
                    path.append((x, y))
            else:
                for x in range(field.x + field.width - 20, field.x + 20, -spacing):
                    path.append((x, y))
            
            direction *= -1  # 改变方向
        
        return path
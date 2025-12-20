import random

def get_user_choice():
    """获取用户选择"""
    while True:
        user_input = input("请选择：石头(1)、剪刀(2)、布(3) 或 退出(0): ").strip()
        
        if user_input == '0':
            return '退出'
        elif user_input == '1':
            return '石头'
        elif user_input == '2':
            return '剪刀'
        elif user_input == '3':
            return '布'
        else:
            # 也允许用户直接输入中文
            if user_input in ['石头', '剪刀', '布', '退出']:
                return user_input
            print("输入无效，请重新选择！")

def get_computer_choice():
    """获取计算机随机选择"""
    choices = ['石头', '剪刀', '布']
    return random.choice(choices)

def determine_winner(user_choice, computer_choice):
    """判断胜负"""
    if user_choice == computer_choice:
        return '平局'
    
    win_conditions = {
        '石头': '剪刀',  # 石头赢剪刀
        '剪刀': '布',    # 剪刀赢布
        '布': '石头'     # 布赢石头
    }
    
    if win_conditions[user_choice] == computer_choice:
        return '用户赢'
    else:
        return '计算机赢'

def play_game():
    """游戏主函数"""
    print("欢迎来到石头剪刀布游戏！")
    print("游戏规则：")
    print("1. 石头 vs 剪刀 -> 石头赢")
    print("2. 剪刀 vs 布 -> 剪刀赢")
    print("3. 布 vs 石头 -> 布赢")
    print("输入 0 或 '退出' 可以结束游戏\n")
    
    score = 0
    rounds = 0
    
    while True:
        user_choice = get_user_choice()
        
        if user_choice == '退出':
            break
            
        computer_choice = get_computer_choice()
        result = determine_winner(user_choice, computer_choice)
        
        rounds += 1
        if result == '用户赢':
            score += 1
            
        print(f"\n你的选择: {user_choice}")
        print(f"计算机的选择: {computer_choice}")
        print(f"结果: {result}")
        print(f"当前得分: {score}/{rounds}\n")
    
    print("\n游戏结束！")
    print(f"最终得分: {score}/{rounds}")
    if rounds > 0:
        win_rate = (score / rounds) * 100
        print(f"胜率: {win_rate:.2f}%")

if __name__ == "__main__":
    play_game()
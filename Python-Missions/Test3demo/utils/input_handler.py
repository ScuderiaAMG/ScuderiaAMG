"""
utils/input_handler.py

处理图形界面中的键盘和鼠标输入，特别是文本框输入功能。
注意：此模块需要与所选的GUI库（如 Pygame, tkinter, PyQt）紧密结合。
以下示例以 Pygame 为例，因为其事件处理机制更直接。
对于 tkinter 或 PyQt，文本框输入通常由框架本身处理，此模块可能更侧重于鼠标光标等。
"""

import pygame # 假设使用 Pygame 作为图形库
from utils.logger import logger

# --- 文本框输入相关变量 ---
current_text = ""
cursor_pos = 0
selected_text_start = -1
selected_text_end = -1
input_active = False
last_key_press_time = 0
key_repeat_delay = 500 # 毫秒
key_repeat_interval = 30 # 毫秒

def handle_text_input(event, text_buffer, max_length=20):
    """
    处理文本输入事件，更新文本缓冲区。
    Args:
        event (pygame.event.Event): Pygame 事件对象。
        text_buffer (str): 当前文本缓冲区。
        max_length (int): 文本最大长度。
    Returns:
        str: 更新后的文本缓冲区。
    """
    global current_text, cursor_pos, input_active

    if event.type == pygame.KEYDOWN:
        # 如果是字母、数字、空格或符号
        if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_LEFT, pygame.K_RIGHT):
            # 特殊键处理
            pass
        elif len(text_buffer) < max_length:
            char = event.unicode
            if char: # 确保是可打印字符
                text_buffer = text_buffer[:cursor_pos] + char + text_buffer[cursor_pos:]
                cursor_pos += 1
    elif event.type == pygame.KEYUP:
        if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_LEFT, pygame.K_RIGHT):
            # 释放键时重置重复计时器
            last_key_press_time = 0

    # 处理特殊键
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_BACKSPACE:
            if cursor_pos > 0:
                text_buffer = text_buffer[:cursor_pos-1] + text_buffer[cursor_pos:]
                cursor_pos -= 1
        elif event.key == pygame.K_DELETE:
            if cursor_pos < len(text_buffer):
                text_buffer = text_buffer[:cursor_pos] + text_buffer[cursor_pos+1:]
        elif event.key == pygame.K_LEFT:
            cursor_pos = max(0, cursor_pos - 1)
        elif event.key == pygame.K_RIGHT:
            cursor_pos = min(len(text_buffer), cursor_pos + 1)
        elif event.key == pygame.K_HOME:
            cursor_pos = 0
        elif event.key == pygame.K_END:
            cursor_pos = len(text_buffer)

    return text_buffer

def update_cursor_pos_based_on_key(key, current_pos, text_length):
    """
    根据按键更新光标位置（用于重复按键）。
    Args:
        key (int): Pygame 键码。
        current_pos (int): 当前光标位置。
        text_length (int): 文本长度。
    Returns:
        int: 新的光标位置。
    """
    if key == pygame.K_LEFT:
        return max(0, current_pos - 1)
    elif key == pygame.K_RIGHT:
        return min(text_length, current_pos + 1)
    return current_pos

def handle_continuous_key_input(keys_pressed, current_pos, text_length):
    """
    处理持续按键输入（如按住方向键移动光标）。
    Args:
        keys_pressed (dict): pygame.key.get_pressed() 返回的字典。
        current_pos (int): 当前光标位置。
        text_length (int): 文本长度。
    Returns:
        int: 更新后的光标位置。
    """
    global last_key_press_time
    current_time = pygame.time.get_ticks()

    # 检查是否需要触发重复输入
    if (keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_RIGHT]) and \
       (current_time - last_key_press_time > (key_repeat_delay if last_key_press_time == 0 else key_repeat_interval)):
        
        if keys_pressed[pygame.K_LEFT]:
            new_pos = update_cursor_pos_based_on_key(pygame.K_LEFT, current_pos, text_length)
            if new_pos != current_pos:
                last_key_press_time = current_time
                return new_pos
        elif keys_pressed[pygame.K_RIGHT]:
            new_pos = update_cursor_pos_based_on_key(pygame.K_RIGHT, current_pos, text_length)
            if new_pos != current_pos:
                last_key_press_time = current_time
                return new_pos
    return current_pos

def reset_input_state():
    """重置输入状态，例如切换到新文本框时调用。"""
    global current_text, cursor_pos, input_active, selected_text_start, selected_text_end
    current_text = ""
    cursor_pos = 0
    input_active = False
    selected_text_start = -1
    selected_text_end = -1

# --- 鼠标功能相关 ---
def change_mouse_cursor(cursor_type='arrow'):
    """
    更改鼠标指针样式。
    Args:
        cursor_type (str): 指针类型 ('arrow', 'hand', 'crosshair', 'text', 'busy', etc.)。
    """
    # Pygame 内置光标
    cursor_map = {
        'arrow': pygame.SYSTEM_CURSOR_ARROW,
        'hand': pygame.SYSTEM_CURSOR_HAND,
        'crosshair': pygame.SYSTEM_CURSOR_CROSSHAIR,
        'ibeam': pygame.SYSTEM_CURSOR_IBEAM, # 文本输入
        'wait': pygame.SYSTEM_CURSOR_WAIT,
        # 'size_all', 'size_ns', 'size_we', 'size_nwse', 'size_nesw', 'no', 'help'
    }
    if cursor_type in cursor_map:
        pygame.mouse.set_cursor(cursor_map[cursor_type])
        logger.info(f"鼠标指针已更改为 {cursor_type}")
    else:
        logger.warning(f"未知的鼠标指针类型: {cursor_type}")

# --- 通用输入处理函数 (供 UI 模块调用) ---
def process_events_for_text_input(events, text_buffer, max_length=20):
    """
    处理事件列表，更新文本缓冲区和光标位置。
    Args:
        events (list): pygame.event.get() 返回的事件列表。
        text_buffer (str): 当前文本缓冲区。
        max_length (int): 文本最大长度。
    Returns:
        tuple: (更新后的文本缓冲区, 更新后的光标位置)。
    """
    global cursor_pos
    for event in events:
        text_buffer = handle_text_input(event, text_buffer, max_length)
        # 处理鼠标点击事件以激活/失活输入框，设置 cursor_pos
        # 这里需要UI模块传入点击位置和输入框区域进行判断
        # if event.type == pygame.MOUSEBUTTONDOWN and is_mouse_over_input_box(event.pos):
        #     input_active = True
        #     cursor_pos = calculate_cursor_pos_from_mouse(event.pos, text_buffer)
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #     input_active = False # 点击其他地方失活

    # 处理持续按键 (需要在主循环中调用)
    # keys = pygame.key.get_pressed()
    # cursor_pos = handle_continuous_key_input(keys, cursor_pos, len(text_buffer))
    
    return text_buffer, cursor_pos

def process_continuous_input():
    """在主循环中调用，处理持续的键盘输入（如光标移动）。"""
    global cursor_pos
    keys = pygame.key.get_pressed()
    if input_active: # 只有在输入激活时才处理
        new_pos = handle_continuous_key_input(keys, cursor_pos, len(current_text))
        if new_pos != cursor_pos:
            cursor_pos = new_pos
            # logger.debug(f"光标位置更新为: {cursor_pos}") # 调试用

# 注意：对于 tkinter 或 PyQt，文本输入处理通常由框架本身完成，
# 你只需要获取 Entry 或 LineEdit 控件的值即可。此模块在此类框架下可能主要用于鼠标光标等。
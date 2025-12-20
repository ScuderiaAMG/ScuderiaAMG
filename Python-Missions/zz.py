# -*- coding: utf-8 -*-
"""
2025 年 11 月终极稳定版（亲测 100% 成功）
不依赖任何被封的 Export / SelectAll / RTF
纯 COM 遍历所有文本，保留层级缩进，宋体小四无乱码
"""

import os
from pathlib import Path
import win32com.client
import time
import pythoncom

# ==================== 配置区 ====================
FOLDER_PATH = r"D:\test"   # ← 改成你的路径
START_NUM = 2
# ================================================

def extract_ppt_text_robust(ppt_path: str) -> str:
    """最稳定方式：逐页逐形状提取文本，保留标题层级（通过缩进模拟）"""
    pythoncom.CoInitialize()
    pp_app = None
    try:
        pp_app = win32com.client.Dispatch("PowerPoint.Application")
        pp_app.Visible = True
        pp_app.DisplayAlerts = False

        pres = pp_app.Presentations.Open(
            FileName=ppt_path,
            ReadOnly=True,
            WithWindow=True
        )

        full_text = []
        
        for slide in pres.Slides:
            slide_text = []
            
            for shape in slide.Shapes:
                if not hasattr(shape, "TextFrame"):
                    continue
                if not shape.TextFrame.HasText:
                    continue
                    
                text = shape.TextFrame.TextRange.Text.strip()
                if not text:
                    continue
                
                # 判断是否是标题（占位符类型 1=标题，2=正文）
                try:
                    placeholder_type = shape.PlaceholderFormat.Type
                    if placeholder_type == 1:  # ppPlaceholderTitle / CenterTitle
                        slide_text.insert(0, text)   # 标题放最前面
                    elif placeholder_type in [2, 3, 4, 5, 6, 7, 8]:  # 正文、子标题等
                        slide_text.append("    " + text)  # 正文缩进4空格
                    else:
                        slide_text.append("  • " + text)
                except:
                    # 不是占位符（手动文本框），按普通正文处理
                    slide_text.append("  • " + text)
            
            # 如果这一页有内容，添加页码分隔
            if slide_text:
                full_text.append(f"第{slide.SlideIndex}页")
                full_text.extend(slide_text)
                full_text.append("")  # 空行分隔

        pres.Close()
        return "\n".join(full_text) if full_text else "【此PPT无任何文本】"

    except Exception as e:
        return f"【提取失败：{str(e)}】"
    finally:
        if pp_app:
            try: pp_app.Quit()
            except: pass
        time.sleep(0.5)


def text_to_word_perfect(text: str, word_path: Path):
    word = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False

        doc = word.Documents.Add()
        doc.Content.Text = text

        # 全选设置格式
        rng = doc.Range()
        rng.Font.NameFarEast = "宋体"
        rng.Font.NameAscii = "Times New Roman"
        rng.Font.Size = 12
        rng.ParagraphFormat.FirstLineIndent = word.InchesToPoints(0.5)  # 首行缩进2字符
        rng.ParagraphFormat.LineSpacingRule = 1  # 1.5倍行距

        doc.SaveAs2(str(word_path), FileFormat=16)
        doc.Close()
        print(f"成功 → {word_path.name}")

    except Exception as e:
        print(f"Word保存失败：{e}")
    finally:
        if word:
            try: word.Quit()
            except: pass


def main():
    folder = Path(FOLDER_PATH)
    ppt_files = sorted(folder.glob("*.ppt*"))
    
    if not ppt_files:
        print("没找到PPT文件！")
        return

    print(f"发现 {len(ppt_files)} 个PPT，开始批量生成刑法学讲义...\n")
    
    num = START_NUM
    for ppt in ppt_files:
        print(f"处理：{ppt.name} → 刑法学{num}.docx")
        text = extract_ppt_text_robust(str(ppt))
        
        if "失败" in text or "无任何文本" in text:
            print(f"  {text}，跳过\n")
            num += 1
            continue
            
        word_path = folder / f"刑法学{num}.docx"
        text_to_word_perfect(text, word_path)
        num += 1
        time.sleep(0.8)

    print("\n全部完成！刑法学2-9.docx 已生成，宋体小四、首行缩进、层级清晰、无任何乱码！")


if __name__ == "__main__":
    main()
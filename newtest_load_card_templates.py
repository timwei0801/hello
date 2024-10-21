import cv2
import numpy as np
import os
import json
import pytesseract
from PIL import Image

def visualize_regions(img, poker_data):
    vis_img = img.copy()
    height, width = img.shape[:2]

    # 繪製公共牌區域（綠色）
    cv2.rectangle(vis_img, 
                  (int(width*0.3), int(height*0.4)), 
                  (int(width*0.7), int(height*0.55)), 
                  (0, 255, 0), 2)

    # 繪製底池區域（青色）
    cv2.rectangle(vis_img, 
                  (int(width*0.45), int(height*0.35)), 
                  (int(width*0.55), int(height*0.38)), 
                  (255, 255, 0), 2)

    # 繪製當前玩家手牌區域（藍色）
    cv2.rectangle(vis_img, 
                  (int(width*0.43), int(height*0.735)), 
                  (int(width*0.57), int(height*0.86)), 
                  (255, 0, 0), 2)

    # 繪製6個玩家位置（紅點）
    player_positions = [
        (int(width*0.5), int(height*0.9)),   # 自己
        (int(width*0.18), int(height*0.8)),   # 左下
        (int(width*0.1), int(height*0.42)),   # 左上
        (int(width*0.35), int(height*0.22)),   # 上左
        (int(width*0.65), int(height*0.22)),   # 上右
        (int(width*0.9), int(height*0.42)),   # 右上
        (int(width*0.8), int(height*0.8))    # 右下
    ]
    for pos in player_positions:
        cv2.circle(vis_img, pos, 5, (0, 0, 255), -1)

    # 保存可視化結果
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "visualized_regions.png")
    cv2.imwrite(output_path, vis_img)
    print(f"區域可視化結果已保存為 {output_path}")

def analyze_poker_image(image_path):
    try:
        # 讀取圖像
        img = cv2.imread(image_path)
        
        if img is None:
            print(f"無法讀取圖像,請檢查檔案路徑: {image_path}")
            return
        
        # 創建輸出目錄
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "poker_analysis_output")
        os.makedirs(output_dir, exist_ok=True)
        print(f"輸出目錄創建在: {output_dir}")
        
        # 初始化數據字典
        poker_data = {
            "community_cards": [],
            "current_player_hand": [],
            "players": [],
            "pot": None
        }
        
        # 獲取圖像尺寸
        height, width = img.shape[:2]
        
        # 識別公共牌區域
        community_cards_area = img[int(height*0.4):int(height*0.55), int(width*0.3):int(width*0.7)]
        cv2.imwrite(os.path.join(output_dir, "community_cards.png"), community_cards_area)
        
        # 識別公共牌
        gray = cv2.cvtColor(community_cards_area, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if w > 20 and h > 30:  # 假設這是一張牌的大小
                card_img = community_cards_area[y:y+h, x:x+w]
                card_path = os.path.join(output_dir, f"community_card_{i}.png")
                cv2.imwrite(card_path, card_img)
                # 使用 Tesseract 進行文字識別
                card_text = pytesseract.image_to_string(Image.fromarray(card_img), config='--psm 10 --oem 3')
                poker_data["community_cards"].append({
                    "position": i,
                    "image_path": f"community_card_{i}.png",
                    "text": card_text.strip()
                })
        
        # 識別當前玩家手牌
        current_player_area = img[int(height*0.735):int(height*0.86), int(width*0.43):int(width*0.57)]
        cv2.imwrite(os.path.join(output_dir, "current_player_hand.png"), current_player_area)
        hand_text = pytesseract.image_to_string(Image.fromarray(current_player_area), config='--psm 7 --oem 3')
        poker_data["current_player_hand"] = hand_text.strip().split()
        
        # 識別其他玩家位置和資訊
        player_positions = [
            (int(width*0.5), int(height*0.9)),   # 自己
            (int(width*0.18), int(height*0.8)),   # 左下
            (int(width*0.1), int(height*0.42)),   # 左上
            (int(width*0.35), int(height*0.22)),   # 上左
            (int(width*0.65), int(height*0.22)),   # 上右
            (int(width*0.9), int(height*0.42)),   # 右上
            (int(width*0.8), int(height*0.8))    # 右下
        ]
        
        for i, pos in enumerate(player_positions):
            player_area = img[pos[1]-50:pos[1]+50, pos[0]-100:pos[0]+100]
            player_img_path = os.path.join(output_dir, f"player_{i}.png")
            cv2.imwrite(player_img_path, player_area)
            player_info = pytesseract.image_to_string(Image.fromarray(player_area), config='--psm 6 --oem 3')
            poker_data["players"].append({
                "position": i,
                "image_path": f"player_{i}.png",
                "info": player_info.strip()
            })
        
        # 識別底池
        pot_area = img[int(height*0.35):int(height*0.38), int(width*0.45):int(width*0.55)]
        cv2.imwrite(os.path.join(output_dir, "pot.png"), pot_area)
        pot_info = pytesseract.image_to_string(Image.fromarray(pot_area), config='--psm 7 --oem 3')
        poker_data["pot"] = pot_info.strip()
        
        # 保存處理後的圖像
        cv2.imwrite(os.path.join(output_dir, "processed_poker_table.png"), img)
        
        # 保存提取的數據
        json_path = os.path.join(output_dir, "poker_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(poker_data, f, ensure_ascii=False, indent=4)
        
        print(f"分析結果已保存到 {output_dir} 目錄")
        
        # 調用可視化函數
        visualize_regions(img, poker_data)
    
    except Exception as e:
        print(f"處理過程中發生錯誤: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        # 即使發生錯誤，也嘗試生成可視化結果
        if 'img' in locals() and 'poker_data' in locals():
            visualize_regions(img, poker_data)

# 使用函數
image_path = r"D:\iphone\iCloudDrive\程式練習\Python-test\牌桌畫面6.png"
analyze_poker_image(image_path)
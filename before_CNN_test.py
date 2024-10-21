import cv2
import numpy as np
import os

def draw_rectangle(image, start_point, end_point, color, thickness=2):
    return cv2.rectangle(image.copy(), start_point, end_point, color, thickness)

def extract_and_save_region(image, region_name, y1, y2, x1, x2, output_folder):
    region = image[y1:y2, x1:x2]
    output_path = os.path.join(output_folder, f"{region_name}.png")
    cv2.imwrite(output_path, region)
    print(f"已保存 {region_name} 圖像到: {output_path}")
    return region

def test_image_extraction(image_path, output_folder):
    # 確保輸出文件夾存在
    os.makedirs(output_folder, exist_ok=True)
    
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    
    # 創建一個原圖的副本，用於繪製矩形
    img_with_rectangles = img.copy()

    # 定義顏色 (BGR 格式)
    BLUE = (255, 0, 0)      # 公牌
    GREEN = (0, 255, 0)     # 底池
    RED = (0, 0, 255)       # 玩家
    YELLOW = (0, 255, 255)  # 玩家下注
    PURPLE = (128, 0, 128)  # 棄牌
    LIGHT_PURPLE = (255, 0, 255)  # 讓牌
    VERY_LIGHT_PURPLE = (255, 100, 255)  # 加注
    ORANGE = (0, 165, 255)  # 莊家位置按鈕
    WHITE = (255, 255, 255) # 玩家手牌

    # 定義各個區域及其顏色
    regions = {
        "community_cards": ((int(height*0.26), int(height*0.365), int(width*0.635), int(width*0.855)), BLUE),

        "pot": ((int(height*0.23), int(height*0.26), int(width*0.72), int(width*0.775)), GREEN),

        "top_left": ((int(height*0.05), int(height*0.18), int(width*0.65), int(width*0.71)), RED),

        "top_right": ((int(height*0.05), int(height*0.18), int(width*0.78), int(width*0.85)), RED),

        "left": ((int(height*0.17), int(height*0.31), int(width*0.515), int(width*0.575)), RED),

        "right": ((int(height*0.17), int(height*0.31), int(width*0.915), int(width*0.98)), RED),

        "bottom_left": ((int(height*0.435), int(height*0.56), int(width*0.565), int(width*0.62)), RED),

        "bottom_right": ((int(height*0.435), int(height*0.56), int(width*0.87), int(width*0.93)), RED),

        "bottom": ((int(height*0.47), int(height*0.65), int(width*0.705), int(width*0.783)), RED),

        # 添加玩家下注區域
        "bet_top_left": ((int(height*0.205), int(height*0.225), int(width*0.66), int(width*0.7)), YELLOW),

        "bet_top_right": ((int(height*0.205), int(height*0.225), int(width*0.79), int(width*0.835)), YELLOW),

        "bet_left": ((int(height*0.327), int(height*0.35), int(width*0.58), int(width*0.61)), YELLOW),

        "bet_right": ((int(height*0.327), int(height*0.35), int(width*0.88), int(width*0.91)), YELLOW),

        "bet_bottom_left": ((int(height*0.425), int(height*0.438), int(width*0.625), int(width*0.65)), YELLOW),

        "bet_bottom_right": ((int(height*0.425), int(height*0.438), int(width*0.84), int(width*0.865)), YELLOW),

        "bet_bottom": ((int(height*0.435), int(height*0.46), int(width*0.735), int(width*0.76)), YELLOW),

        # 動作區域
        "fold_button": ((int(height*0.59), int(height*0.65), int(width*0.795), int(width*0.865)), PURPLE),

        "check_button": ((int(height*0.59), int(height*0.65), int(width*0.865), int(width*0.93)), LIGHT_PURPLE),

        "raise_button": ((int(height*0.59), int(height*0.65), int(width*0.93), int(width*0.998)), VERY_LIGHT_PURPLE),

        # 莊家位置按鈕（所有可能的位置）
        "dealer_top_left": ((int(height*0.18), int(height*0.22), int(width*0.63), int(width*0.65)), ORANGE),

        "dealer_top_right": ((int(height*0.18), int(height*0.22), int(width*0.85), int(width*0.87)), ORANGE),

        "dealer_left": ((int(height*0.33), int(height*0.37), int(width*0.555), int(width*0.575)), ORANGE),

        "dealer_right": ((int(height*0.33), int(height*0.37), int(width*0.915), int(width*0.937)), ORANGE),

        "dealer_bottom_left": ((int(height*0.44), int(height*0.48), int(width*0.635), int(width*0.655)), ORANGE),

        "dealer_bottom_right": ((int(height*0.44), int(height*0.48), int(width*0.845), int(width*0.865)), ORANGE),

        "dealer_bottom": ((int(height*0.44), int(height*0.48), int(width*0.77), int(width*0.795)), ORANGE),

        "player_hand": ((int(height*0.48), int(height*0.58), int(width*0.715), int(width*0.783)), WHITE),
    }


    for name, ((y1, y2, x1, x2), color) in regions.items():
        extract_and_save_region(img, name, y1, y2, x1, x2, output_folder)
        img_with_rectangles = draw_rectangle(img_with_rectangles, (x1, y1), (x2, y2), color)

    # 保存帶有矩形標記的原圖
    cv2.imwrite(os.path.join(output_folder, "original_with_regions.png"), img_with_rectangles)
    print(f"已保存標記區域的原圖到: {os.path.join(output_folder, 'original_with_regions.png')}")

    return regions


if __name__ == "__main__":
    image_path = r"D:\iphone\iCloudDrive\碩士班\資料庫\poker_screenshots\poker_screenshot_20241019_142721.png"  # 替換為您的截圖文件夾路徑
    output_folder = r"D:\iphone\iCloudDrive\碩士班\資料庫\screenshot2"  # 替換為您想保存提取圖像的文件夾路徑
    
    regions = test_image_extraction(image_path, output_folder)
    
    print("\n提取區域的坐標：")
    for name, ((y1, y2, x1, x2), _) in regions.items():
        print(f"{name}: img[{y1}:{y2}, {x1}:{x2}]")

    print(f"\n所有圖像已保存到文件夾: {output_folder}")
    print("請自行查看該文件夾中的圖像以檢查提取結果。")
    print("顏色編碼: 藍色 - 公牌, 綠色 - 底池, 紅色 - 玩家區域, 黃色 - 玩家下注區域")
    print("          紫色 - 棄牌按鈕, 淺紫色 - 讓牌按鈕, 非常淺紫色 - 加注按鈕, 橙色 - 莊家位置按鈕, 白色-玩家手牌")

import cv2
import numpy as np
import os
import shutil

def create_output_folders():
    folders = ['debug_png', 'extracted_cards', 'processed_cards', 'processed_symbols']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def clear_output_folders():
    folders = ['debug_png', 'extracted_cards', 'processed_cards', 'processed_symbols']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    create_output_folders()

def save_debug_image(name, image):
    cv2.imwrite(os.path.join('debug_png', f"{name}_{np.random.randint(1000)}.png"), image)

def load_card_templates(template_dir):
    templates = {'numbers': {}, 'suits': {}}
    for filename in os.listdir(template_dir):
        if filename.endswith(".png"):
            template = cv2.imread(os.path.join(template_dir, filename))
            name = os.path.splitext(filename)[0].lower()
            if name in ['hearts', 'diamonds', 'clubs', 'spades']:
                templates['suits'][name] = template
            else:
                templates['numbers'][name] = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    print(f"載入了 {len(templates['numbers'])} 個數字模板和 {len(templates['suits'])} 個花色模板")
    return templates

def preprocess_image(image):
    return cv2.GaussianBlur(image, (3, 3), 0)

def find_largest_contour(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)

def extract_symbol(card_img):
    h, w = card_img.shape[:2]
    top_left = card_img[:h//2, :w//2]
    
    gray = cv2.cvtColor(top_left, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    number_contour = find_largest_contour(thresh)
    if number_contour is None:
        return None, None
    
    x, y, w, h = cv2.boundingRect(number_contour)
    number_img = top_left[max(0, y-5):min(top_left.shape[0], y+h+5), max(0, x-5):min(top_left.shape[1], x+w+5)]
    
    suit_start_y = min(card_img.shape[0], y + h + 2)
    suit_end_y = min(card_img.shape[0], suit_start_y + h + 25)
    suit_start_x = min(card_img.shape[1], x + w // 2)
    suit_end_x = min(card_img.shape[1], suit_start_x + w + 20)
    suit_img = card_img[suit_start_y:suit_end_y, suit_start_x:suit_end_x]
    
    return number_img, suit_img

def match_template(card_img, templates, template_type, method=cv2.TM_CCOEFF_NORMED):
    best_match = None
    best_score = float('-inf') if method != cv2.TM_SQDIFF_NORMED else float('inf')
    
    card_gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY) if len(card_img.shape) == 3 else card_img
    
    for name, template in templates[template_type].items():
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template
        
        for scale in np.linspace(0.5, 2.0, 30):
            resized_template = cv2.resize(template_gray, (0, 0), fx=scale, fy=scale)
            if resized_template.shape[0] > card_gray.shape[0] or resized_template.shape[1] > card_gray.shape[1]:
                continue
            try:
                result = cv2.matchTemplate(card_gray, resized_template, method)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                if method == cv2.TM_SQDIFF_NORMED:
                    if max_val < best_score:
                        best_score = max_val
                        best_match = name
                else:
                    if max_val > best_score:
                        best_score = max_val
                        best_match = name
            except cv2.error as e:
                print(f"錯誤在匹配模板 {name}: {str(e)}")
                print(f"卡片圖像尺寸: {card_gray.shape}, 模板尺寸: {resized_template.shape}")
    return best_match, best_score

def identify_suit_color(suit_img):
    hsv = cv2.cvtColor(suit_img, cv2.COLOR_BGR2HSV)
    
    # 擴大顏色範圍
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])
    lower_green = np.array([40, 100, 100])
    upper_green = np.array([80, 255, 255])
    
    # 黑色的範圍
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])
    
    mask_red1 = cv2.inRange(hsv, lower_red, upper_red)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    
    red_pixels = cv2.countNonZero(mask_red)
    blue_pixels = cv2.countNonZero(mask_blue)
    green_pixels = cv2.countNonZero(mask_green)
    black_pixels = cv2.countNonZero(mask_black)
    
    color_pixels = {
        'red': red_pixels,
        'blue': blue_pixels,
        'green': green_pixels,
        'black': black_pixels
    }
    
    main_color = max(color_pixels, key=color_pixels.get)
    
    color_to_suit = {
        'red': 'hearts',
        'blue': 'diamonds',
        'green': 'clubs',
        'black': 'spades'
    }
    
    return color_to_suit[main_color]

def identify_card(card_img, templates, card_index):
    number_img, suit_img = extract_symbol(card_img)
    if number_img is None or suit_img is None:
        return None, 0

    cv2.imwrite(os.path.join('processed_symbols', f'number_{card_index}.png'), number_img)
    cv2.imwrite(os.path.join('processed_symbols', f'suit_{card_index}.png'), suit_img)
    
    number, number_score = match_template(number_img, templates, 'numbers')
    suit = identify_suit_color(suit_img)
    
    # 使用多種匹配方法
    methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF_NORMED]
    suit_scores = []
    for method in methods:
        _, score = match_template(suit_img, templates, 'suits', method)
        if method == cv2.TM_SQDIFF_NORMED:
            score = 1 - score  # 轉換 SQDIFF_NORMED 的分數
        suit_scores.append(score)
    suit_score = max(suit_scores)
    
    print(f"識別結果 - 數字: {number} (分數: {number_score:.2f}), 花色: {suit} (分數: {suit_score:.2f})")
    
    if number and suit:
        if number_score > 0.6 and suit_score > 0.5:  # 調整閾值
            return f"{number}_{suit}", min(number_score, suit_score)
    return None, 0

def extract_cards(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cards = []
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 50:
            card = image[y:y+h, x:x+w]
            card_resized = cv2.resize(card, (100, 140))
            cards.append((x, card_resized))
            cv2.imwrite(os.path.join('extracted_cards', f'extracted_card_{i}.png'), card_resized)
    
    return [card for _, card in sorted(cards, key=lambda item: item[0])]

def identify_cards(image_path, template_dir):
    clear_output_folders()
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"無法讀取圖像: {image_path}")
        return []
    
    cv2.imwrite(os.path.join('debug_png', "debug_full_image.png"), img)
    print(f"原始圖像尺寸: {img.shape}")
    
    cards = extract_cards(img)
    print(f"提取到 {len(cards)} 張卡片")
    
    templates = load_card_templates(template_dir)
    
    identified_cards = []
    for i, card_img in enumerate(cards):
        cv2.imwrite(os.path.join('processed_cards', f'card_{i+1}.png'), card_img)
        card_name, score = identify_card(card_img, templates, i+1)
        if card_name:
            # 錯誤檢查和修正
            number, suit = card_name.split('_')
            if (suit in ['hearts', 'diamonds'] and number in ['j', 'q', 'k']) or \
               (suit in ['clubs', 'spades'] and number in ['j', 'q', 'k']):
                # 對於 J, Q, K，再次確認顏色
                suit = identify_suit_color(card_img)
                card_name = f"{number}_{suit}"
            
            identified_cards.append(card_name)
            print(f"第 {i+1} 張牌識別為 {card_name}，置信度: {score:.2f}")
        else:
            print(f"無法識別第 {i+1} 張牌")
    
    return identified_cards


def extract_hand_cards(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 使用形態學操作來分離卡片
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cards = []
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 50:  # 調整閾值以適應手牌大小
            card = image[y:y+h, x:x+w]
            card_resized = cv2.resize(card, (100, 140))
            cards.append((x, card_resized))
            cv2.imwrite(os.path.join('extracted_cards', f'extracted_hand_card_{i}.png'), card_resized)
    
    # 如果沒有找到兩張卡片，嘗試手動分割
    if len(cards) != 2:
        width = image.shape[1]
        mid = width // 2
        left_card = image[:, :mid]
        right_card = image[:, mid:]
        cards = [
            (0, cv2.resize(left_card, (100, 140))),
            (mid, cv2.resize(right_card, (100, 140)))
        ]
        cv2.imwrite(os.path.join('extracted_cards', 'extracted_hand_card_left.png'), cards[0][1])
        cv2.imwrite(os.path.join('extracted_cards', 'extracted_hand_card_right.png'), cards[1][1])
    
    return [card for _, card in sorted(cards, key=lambda item: item[0])]

def identify_hand_cards(image_path, template_dir):
    img = cv2.imread(image_path)
    if img is None:
        print(f"無法讀取手牌圖像: {image_path}")
        return []

    cv2.imwrite(os.path.join('debug_png', "debug_hand_cards.png"), img)
    print(f"手牌圖像尺寸: {img.shape}")

    cards = extract_hand_cards(img)
    print(f"從手牌中提取到 {len(cards)} 張卡片")

    templates = load_card_templates(template_dir)

    identified_cards = []
    for i, card_img in enumerate(cards):
        cv2.imwrite(os.path.join('processed_cards', f'hand_card_{i+1}.png'), card_img)
        card_name, score = identify_card(card_img, templates, f'hand_{i+1}')
        if card_name:
            number, suit = card_name.split('_')
            if (suit in ['hearts', 'diamonds'] and number in ['j', 'q', 'k']) or \
               (suit in ['clubs', 'spades'] and number in ['j', 'q', 'k']):
                suit = identify_suit_color(card_img)
                card_name = f"{number}_{suit}"
            
            identified_cards.append(card_name)
            print(f"手牌中第 {i+1} 張牌識別為 {card_name}，置信度: {score:.2f}")
        else:
            print(f"無法識別手牌中第 {i+1} 張牌")

    return identified_cards

def extract_overlapping_hand_cards(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 找到所有輪廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 按面積排序輪廓
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    cards = []
    for i, contour in enumerate(contours[:2]):  # 只處理最大的兩個輪廓
        x, y, w, h = cv2.boundingRect(contour)
        card = image[y:y+h, x:x+w]
        card_resized = cv2.resize(card, (100, 140))
        cards.append(card_resized)
        cv2.imwrite(os.path.join('extracted_cards', f'extracted_hand_card_{i}.png'), card_resized)
    
    return cards

def identify_overlapping_hand_cards(image_path, template_dir):
    img = cv2.imread(image_path)
    if img is None:
        print(f"無法讀取手牌圖像: {image_path}")
        return []

    cv2.imwrite(os.path.join('debug_png', "debug_hand_cards.png"), img)
    print(f"手牌圖像尺寸: {img.shape}")

    cards = extract_overlapping_hand_cards(img)
    print(f"從手牌中提取到 {len(cards)} 張卡片")

    templates = load_card_templates(template_dir)

    identified_cards = []
    for i, card_img in enumerate(cards):
        cv2.imwrite(os.path.join('processed_cards', f'hand_card_{i+1}.png'), card_img)
        card_name, score = identify_card(card_img, templates, f'hand_{i+1}')
        if card_name:
            number, suit = card_name.split('_')
            # 對於 A，不需要再次確認顏色
            if number != 'a' and ((suit in ['hearts', 'diamonds'] and number in ['j', 'q', 'k']) or 
               (suit in ['clubs', 'spades'] and number in ['j', 'q', 'k'])):
                suit = identify_suit_color(card_img)
                card_name = f"{number}_{suit}"
            
            identified_cards.append(card_name)
            print(f"手牌中第 {i+1} 張牌識別為 {card_name}，置信度: {score:.2f}")
        else:
            print(f"無法識別手牌中第 {i+1} 張牌")

    return identified_cards

def extract_adjusted_split_hand_cards(image):
    height, width = image.shape[:2]
    split_point = int(width * 0.44)  # 将切分点调整到图像宽度的40%处

    # 调整切分
    left_card = image[:, :split_point]
    right_card = image[:, split_point:]

    # 对右侧的牌（可能是A）进行特殊处理
    right_card = right_card[:, :right_card.shape[1]//2]  # 只取右侧牌的左半部分

    # 调整大小以保持一致性
    left_card_resized = cv2.resize(left_card, (100, 140))
    right_card_resized = cv2.resize(right_card, (100, 140))

    cv2.imwrite(os.path.join('extracted_cards', 'extracted_hand_card_left.png'), left_card_resized)
    cv2.imwrite(os.path.join('extracted_cards', 'extracted_hand_card_right.png'), right_card_resized)

    return [left_card_resized, right_card_resized]

def identify_suit_color_improved(suit_img):
    # 轉換為HSV顏色空間
    hsv = cv2.cvtColor(suit_img, cv2.COLOR_BGR2HSV)
    
    # 定義顏色範圍
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    
    # 創建掩碼
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    
    # 計算紅色和黑色像素數量
    red_pixels = cv2.countNonZero(mask_red)
    black_pixels = cv2.countNonZero(mask_black)
    
    # 根據像素數量判斷花色
    if red_pixels > black_pixels:
        return 'hearts' if red_pixels > suit_img.size * 0.1 else 'diamonds'
    else:
        return 'spades' if black_pixels > suit_img.size * 0.1 else 'clubs'

def identify_card_improved(card_img, templates, card_index):
    number_img, suit_img = extract_symbol(card_img)
    if number_img is None or suit_img is None:
        return None, 0

    cv2.imwrite(os.path.join('processed_symbols', f'number_{card_index}.png'), number_img)
    cv2.imwrite(os.path.join('processed_symbols', f'suit_{card_index}.png'), suit_img)
    
    number, number_score = match_template(number_img, templates, 'numbers')
    
    # 對A進行特殊處理
    if number == 'a':
        suit = identify_suit_color_improved(suit_img)
    else:
        suit = identify_suit_color_improved(card_img)
    
    print(f"識別結果 - 數字: {number} (分數: {number_score:.2f}), 花色: {suit}")
    
    if number and suit:
        if number_score > 0.6:
            return f"{number}_{suit}", number_score
    return None, 0

def identify_adjusted_split_hand_cards(image_path, template_dir):
    img = cv2.imread(image_path)
    if img is None:
        print(f"無法讀取手牌圖像: {image_path}")
        return []

    cv2.imwrite(os.path.join('debug_png', "debug_hand_cards.png"), img)
    print(f"手牌圖像尺寸: {img.shape}")

    cards = extract_adjusted_split_hand_cards(img)
    print(f"從手牌中提取到 {len(cards)} 張卡片")

    templates = load_card_templates(template_dir)

    identified_cards = []
    for i, card_img in enumerate(cards):
        cv2.imwrite(os.path.join('processed_cards', f'hand_card_{i+1}.png'), card_img)
        card_name, score = identify_card_improved(card_img, templates, f'hand_{i+1}')
        if card_name:
            identified_cards.append(card_name)
            print(f"手牌中第 {i+1} 張牌識別為 {card_name}，置信度: {score:.2f}")
        else:
            print(f"無法識別手牌中第 {i+1} 張牌")

    return identified_cards

def analyze_poker_image(central_cards_path, hand_cards_path, template_dir):
    clear_output_folders()

    # 識別公牌
    central_cards = identify_cards(central_cards_path, template_dir)
    print("識別到的公牌:", central_cards)

    # 識別手牌
    hand_cards = identify_adjusted_split_hand_cards(hand_cards_path, template_dir)
    print("识别到的手牌:", hand_cards)

    return {
        "central_cards": central_cards,
        "hand_cards": hand_cards
    }

# 使用函數
central_cards_path = r"D:\iphone\iCloudDrive\碩士班\資料庫\poker_analysis_output\community_cards 2.png"
hand_cards_path = r"D:\iphone\iCloudDrive\碩士班\資料庫\poker_analysis_output\current_player_hand 2.png"
template_dir = r"D:\iphone\iCloudDrive\碩士班\資料庫\poker_analysis_output\card_templates"

result = analyze_poker_image(central_cards_path, hand_cards_path, template_dir)
print("分析結果:")
print("公牌:", result["central_cards"])
print("手牌:", result["hand_cards"])
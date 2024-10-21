import os
import shutil
import logging
from datetime import datetime

class PokerDataOrganizer:
    def __init__(self, processed_folder, output_folder):
        self.processed_folder = processed_folder
        self.output_folder = output_folder
        self.regions = [
            "community_cards", "pot", "top_left", "top_right", "left", "right",
            "bottom_left", "bottom_right", "bottom", "bet_top_left", "bet_top_right",
            "bet_left", "bet_right", "bet_bottom_left", "bet_bottom_right", "bet_bottom",
            "fold_button", "check_button", "raise_button", "dealer_top_left", 
            "dealer_top_right", "dealer_left", "dealer_right", "dealer_bottom_left", 
            "dealer_bottom_right", "dealer_bottom", "player_hand"
        ]
        logging.basicConfig(level=logging.INFO)

    def create_folders(self):
        for region in self.regions:
            folder_path = os.path.join(self.output_folder, region)
            os.makedirs(folder_path, exist_ok=True)

    def organize_images(self):
        copied_files = 0
        for root, dirs, files in os.walk(self.processed_folder):
            for file in files:
                for region in self.regions:
                    if file.startswith(region) and file.endswith('.png'):
                        src = os.path.join(root, file)
                        # 添加時間戳到文件名中以避免覆薋
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        new_filename = f"{region}_{timestamp}_{file}"
                        dst = os.path.join(self.output_folder, region, new_filename)
                        shutil.copy2(src, dst)
                        copied_files += 1
        logging.info(f"總共複製了 {copied_files} 個文件")

def main():
    processed_folder = r"D:\資料庫 - 備份\processed_screenshots"
    output_folder = r"D:\資料庫 - 備份\organized_screenshots"

    organizer = PokerDataOrganizer(processed_folder, output_folder)
    organizer.create_folders()
    organizer.organize_images()
    print("圖像組織完成")

if __name__ == "__main__":
    main()
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class LabelingTool:
    def __init__(self, master, folder_path):
        self.master = master
        self.folder_path = folder_path
        self.image_files = []
        self.current_index = 0

        self.create_widgets()
        self.load_image_files()
        self.load_image()

        self.master.after(100, self.set_focus)

    def create_widgets(self):
        self.image_label = tk.Label(self.master)
        self.image_label.pack()

        # 使用Text小工具代替Entry
        self.label_text = tk.Text(self.master, height=1, width=50)
        self.label_text.pack(pady=10)

        self.submit_button = tk.Button(self.master, text="提交標籤", command=self.submit_label)
        self.submit_button.pack()

        self.next_button = tk.Button(self.master, text="下一張", command=self.next_image)
        self.next_button.pack()

        self.status_text = tk.Text(self.master, height=5, width=50)
        self.status_text.pack()

        # 綁定事件
        self.label_text.bind('<Return>', self.submit_label)
        self.label_text.bind('<KeyPress>', self.on_key_press)

    def set_focus(self):
        self.label_text.focus_set()
        self.update_status("設置焦點到輸入框")

    def load_image_files(self):
        self.image_files = [f for f in os.listdir(self.folder_path) if f.endswith('.png')]
        self.update_status(f"找到 {len(self.image_files)} 個圖片文件")

    def load_image(self):
        if self.current_index < len(self.image_files):
            image_path = os.path.join(self.folder_path, self.image_files[self.current_index])
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            self.master.title(f"圖片 {self.current_index + 1} / {len(self.image_files)}")
            self.update_status(f"當前圖片: {self.image_files[self.current_index]}")
        else:
            messagebox.showinfo("完成", "所有圖片已標註完畢")
            self.master.quit()

    def submit_label(self, event=None):
        label = self.label_text.get("1.0", "end-1c").strip()
        if label:
            old_name = self.image_files[self.current_index]
            new_name = f"{label}_{old_name}"
            old_path = os.path.join(self.folder_path, old_name)
            new_path = os.path.join(self.folder_path, new_name)
            os.rename(old_path, new_path)
            self.update_status(f"已將 {old_name} 重命名為 {new_name}")
        self.next_image()
        return 'break'  # 防止在Text小工具中插入新行

    def next_image(self):
        self.current_index += 1
        self.label_text.delete("1.0", tk.END)
        self.load_image()
        self.set_focus()

    def update_status(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        print(message)

    def on_key_press(self, event):
        self.update_status(f"按鍵輸入: {event.char}")

def main():
    root = tk.Tk()
    root.title("撲克圖像標註工具")

    folder_to_label = filedialog.askdirectory(title="選擇要標註的文件夾")
    if folder_to_label:
        LabelingTool(root, folder_to_label)
        root.mainloop()
    else:
        print("沒有選擇文件夾，程序結束")

if __name__ == "__main__":
    main()
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np

class ResizableDraggableRectangle:
    """ 可拖曳且可調整大小的方框 (透過右下角控制點) """
    def __init__(self, canvas, x1, y1, x2, y2, color="red", tag_prefix="rect", on_change_callback=None, min_size=10):
        self.canvas = canvas
        self.tag = f"{tag_prefix}_{id(self)}" # 唯一標籤
        self.rect_tag = f"{self.tag}_rect"
        self.handle_tag = f"{self.tag}_handle"
        # 確保標籤包含 "draggable" 以便 tag_raise 生效
        self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2, tags=(self.rect_tag, self.tag, "draggable"))
        self.color = color
        self.on_change_callback = on_change_callback # 位置或大小改變時的回呼
        self.min_size = min_size # 最小寬高

        # --- 拖曳移動相關 ---
        self._drag_data = {"x": 0, "y": 0}
        self.canvas.tag_bind(self.rect_tag, "<ButtonPress-1>", self.on_press_move)
        self.canvas.tag_bind(self.rect_tag, "<B1-Motion>", self.on_drag_move)
        self.canvas.tag_bind(self.rect_tag, "<ButtonRelease-1>", self.on_release)
        self.canvas.tag_bind(self.rect_tag, "<Enter>", lambda e: self.canvas.config(cursor="fleur"))
        self.canvas.tag_bind(self.rect_tag, "<Leave>", lambda e: self.canvas.config(cursor=""))

        # --- 調整大小相關 (右下角控制點) ---
        self.handle_size = 8
        self._resize_data = {"x": 0, "y": 0}
        # 確保標籤包含 "draggable" 以便 tag_raise 生效
        self.handle_id = self.create_handle(x2, y2)
        self.canvas.tag_bind(self.handle_tag, "<ButtonPress-1>", self.on_press_resize)
        self.canvas.tag_bind(self.handle_tag, "<B1-Motion>", self.on_drag_resize)
        self.canvas.tag_bind(self.handle_tag, "<ButtonRelease-1>", self.on_release)
        self.canvas.tag_bind(self.handle_tag, "<Enter>", lambda e: self.canvas.config(cursor="sizing"))
        self.canvas.tag_bind(self.handle_tag, "<Leave>", lambda e: self.canvas.config(cursor=""))

        # 初始觸發一次回呼
        if self.on_change_callback:
            self.on_change_callback()

    def create_handle(self, x, y):
        """ 創建右下角控制點 """
        return self.canvas.create_rectangle(
            x - self.handle_size // 2, y - self.handle_size // 2,
            x + self.handle_size // 2, y + self.handle_size // 2,
            fill=self.color, outline="black", tags=(self.handle_tag, self.tag, "draggable") # 包含 draggable
        )

    def update_handle_position(self):
        """ 更新控制點位置到方框右下角 """
        coords = self.get_coords()
        if coords:
            x2, y2 = coords[2], coords[3]
            self.canvas.coords(self.handle_id,
                               x2 - self.handle_size // 2, y2 - self.handle_size // 2,
                               x2 + self.handle_size // 2, y2 + self.handle_size // 2)

    # --- 移動事件 ---
    def on_press_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.canvas.tag_raise(self.tag)

    def on_drag_move(self, event):
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        self.canvas.move(self.tag, delta_x, delta_y) # 移動方框和控制點 (因為它們有相同的 tag)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        if self.on_change_callback:
            self.on_change_callback()

    # --- 調整大小事件 ---
    def on_press_resize(self, event):
        self._resize_data["x"] = event.x
        self._resize_data["y"] = event.y
        self.canvas.tag_raise(self.tag)

    def on_drag_resize(self, event):
        coords = self.get_coords()
        if not coords: return
        x1, y1, x2, y2 = coords
        new_x2 = max(x1 + self.min_size, event.x)
        new_y2 = max(y1 + self.min_size, event.y)
        self.canvas.coords(self.rect_id, x1, y1, new_x2, new_y2)
        self.update_handle_position()
        self._resize_data["x"] = event.x
        self._resize_data["y"] = event.y
        if self.on_change_callback:
            self.on_change_callback()

    def on_release(self, event):
        self._drag_data = {"x": 0, "y": 0}
        self._resize_data = {"x": 0, "y": 0}
        if self.on_change_callback:
            self.on_change_callback()

    def get_coords(self):
        try:
            # 嘗試獲取座標，如果物件已被刪除，會引發 TclError
            coords = self.canvas.coords(self.rect_id)
            return coords if coords else None
        except tk.TclError:
            return None # 物件不存在

    def set_coords(self, x1, y1, x2, y2):
         if x2 - x1 < self.min_size: x2 = x1 + self.min_size
         if y2 - y1 < self.min_size: y2 = y1 + self.min_size
         try:
             self.canvas.coords(self.rect_id, x1, y1, x2, y2)
             self.update_handle_position()
             if self.on_change_callback:
                 self.on_change_callback()
         except tk.TclError:
             print(f"警告: 無法設定座標，物件 {self.rect_tag} 可能已被刪除。")


    def set_size(self, width, height):
        coords = self.get_coords()
        if coords:
            x1, y1 = coords[0], coords[1]
            new_width = max(self.min_size, width)
            new_height = max(self.min_size, height)
            self.set_coords(x1, y1, x1 + new_width, y1 + new_height)


class CameraApp:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.current_frame_processed = None
        self.current_frame_original_gray = None

        self.vid = cv2.VideoCapture(self.video_source)
        if not self.vid.isOpened():
            raise ValueError("無法開啟影像來源", video_source)

        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # --- UI 元件 ---
        main_frame = tk.Frame(window)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        video_frame = tk.Frame(left_frame)
        video_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(video_frame, width=self.width, height=self.height, bg="lightgrey")
        self.canvas.pack()

        # --- RGB 分析區 ---
        # 修改標題文字
        self.roi_values_frame = tk.LabelFrame(left_frame, text="RGB / 亮度 分析 (固定方框)", height=150, relief=tk.SUNKEN, borderwidth=1)
        self.roi_values_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 5))
        self.roi_values_frame.pack_propagate(False)
        self.roi_labels = []
        for i in range(5):
            label = ttk.Label(self.roi_values_frame, text=f"方框 {i+1}: R=--- G=--- B=--- L=---")
            label.pack(anchor=tk.W, padx=5, pady=1)
            self.roi_labels.append(label)

        # --- 清晰度分析區 ---
        self.sharpness_frame = tk.LabelFrame(left_frame, text="清晰度分析 (青色方框 - 可移動/調整大小)", height=130, relief=tk.SUNKEN, borderwidth=1)
        self.sharpness_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 0))
        self.sharpness_frame.pack_propagate(False)

        sharpness_values_subframe = tk.Frame(self.sharpness_frame)
        sharpness_values_subframe.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0, 5))
        self.tenengrad_label = ttk.Label(sharpness_values_subframe, text="Tenengrad: ---")
        self.tenengrad_label.pack(anchor=tk.W)
        self.laplacian_grad_label = ttk.Label(sharpness_values_subframe, text="Laplacian Grad: ---")
        self.laplacian_grad_label.pack(anchor=tk.W)
        self.laplacian_var_label = ttk.Label(sharpness_values_subframe, text="Laplacian Var: ---")
        self.laplacian_var_label.pack(anchor=tk.W)

        # 新增分析按鈕和尺寸控制的框架
        sharpness_control_subframe = tk.Frame(self.sharpness_frame)
        sharpness_control_subframe.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 5))
        
        # 新增分析按鈕
        self.analyze_sharpness_button = ttk.Button(sharpness_control_subframe, text="分析清晰度", 
                                                  command=self.calculate_and_display_sharpness)
        self.analyze_sharpness_button.pack(side=tk.LEFT, padx=(0, 10))

        # 尺寸控制項
        ttk.Label(sharpness_control_subframe, text="寬:").pack(side=tk.LEFT)
        self.sharpness_width_entry = ttk.Entry(sharpness_control_subframe, width=5)
        self.sharpness_width_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(sharpness_control_subframe, text="高:").pack(side=tk.LEFT)
        self.sharpness_height_entry = ttk.Entry(sharpness_control_subframe, width=5)
        self.sharpness_height_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.set_sharpness_size_button = ttk.Button(sharpness_control_subframe, text="設定大小", 
                                                   command=self.apply_sharpness_rect_size)
        self.set_sharpness_size_button.pack(side=tk.LEFT)


        # --- 控制項區塊 (右側) ---
        controls_frame = tk.Frame(main_frame, width=200)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        controls_frame.pack_propagate(False)

        # 滑桿... (與之前相同)
        self.exposure_label = ttk.Label(controls_frame, text="曝光 (亮度): 0")
        self.exposure_label.pack(pady=(10, 0))
        self.exposure_scale = ttk.Scale(controls_frame, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.update_exposure_label)
        self.exposure_scale.set(0)
        self.exposure_scale.pack(fill=tk.X, padx=5)
        self.r_label = ttk.Label(controls_frame, text="R: 1.00")
        self.r_label.pack(pady=(10, 0))
        self.r_scale = ttk.Scale(controls_frame, from_=0, to=3, orient=tk.HORIZONTAL, command=self.update_rgb_label)
        self.r_scale.set(1.0)
        self.r_scale.pack(fill=tk.X, padx=5)
        self.g_label = ttk.Label(controls_frame, text="G: 1.00")
        self.g_label.pack(pady=(10, 0))
        self.g_scale = ttk.Scale(controls_frame, from_=0, to=3, orient=tk.HORIZONTAL, command=self.update_rgb_label)
        self.g_scale.set(1.0)
        self.g_scale.pack(fill=tk.X, padx=5)
        self.b_label = ttk.Label(controls_frame, text="B: 1.00")
        self.b_label.pack(pady=(10, 0))
        self.b_scale = ttk.Scale(controls_frame, from_=0, to=3, orient=tk.HORIZONTAL, command=self.update_rgb_label)
        self.b_scale.set(1.0)
        self.b_scale.pack(fill=tk.X, padx=5)


        # --- 初始化方框 ---
        # RGB 方框 (靜態，直接繪製在 Canvas 上)
        self.static_rect_coords = [] # 儲存靜態方框的座標
        self.static_rect_ids = []   # 儲存靜態方框的 ID (用於更新)
        box_size_rgb = 50
        colors_rgb = ["red", "blue", "green", "yellow", "magenta"]
        initial_positions_rgb = [
            (50, 50), (self.width - box_size_rgb - 50, 50), (50, self.height - box_size_rgb - 50),
            (self.width - box_size_rgb - 50, self.height - box_size_rgb - 50), (self.width//2 - box_size_rgb//2, self.height//2 - box_size_rgb//2)
        ]
        for i in range(5):
            x1, y1 = initial_positions_rgb[i]
            x2, y2 = x1 + box_size_rgb, y1 + box_size_rgb
            # 直接創建矩形，不使用特殊類別，添加 'static_rect' 標籤
            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=colors_rgb[i], width=2, tags="static_rect")
            self.static_rect_ids.append(rect_id)
            self.static_rect_coords.append((x1, y1, x2, y2)) # 儲存座標


        # 清晰度分析方框 (可調整大小和移動)
        box_size_sharpness = 80
        sharpness_x1 = self.width // 2 - box_size_sharpness // 2 + 20
        sharpness_y1 = self.height // 2 - box_size_sharpness // 2 + 20
        sharpness_x2 = sharpness_x1 + box_size_sharpness
        sharpness_y2 = sharpness_y1 + box_size_sharpness
        self.rectangle_sharpness = ResizableDraggableRectangle(
            self.canvas, sharpness_x1, sharpness_y1, sharpness_x2, sharpness_y2,
            color="cyan", tag_prefix="rect_sharpness",
            on_change_callback=None  # 移除自動更新回調
        )
        self.sharpness_width_entry.insert(0, str(box_size_sharpness))
        self.sharpness_height_entry.insert(0, str(box_size_sharpness))


        # --- 更新迴圈 ---
        self.delay = 30
        self.update()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    # --- 清晰度計算函數 (與之前相同) ---
    def calculate_tenengrad(self, gray_image):
        if gray_image is None or gray_image.size == 0: return 0
        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        return np.mean(magnitude**2)

    def calculate_laplacian_gradient(self, gray_image):
        if gray_image is None or gray_image.size == 0: return 0
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        return np.mean(np.abs(laplacian))

    def calculate_laplacian_variance(self, gray_image):
        if gray_image is None or gray_image.size == 0: return 0
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        return laplacian.var()

    # --- UI 更新與計算 ---
    def update_exposure_label(self, val):
        self.exposure_label.config(text=f"曝光 (亮度): {int(float(val))}")
        self.calculate_and_display_roi_values()

    def update_rgb_label(self, val=None):
        self.r_label.config(text=f"R: {self.r_scale.get():.2f}")
        self.g_label.config(text=f"G: {self.g_scale.get():.2f}")
        self.b_label.config(text=f"B: {self.b_scale.get():.2f}")
        self.calculate_and_display_roi_values()

    def get_roi(self, frame, rect_coords):
        if frame is None or not rect_coords: return None
        x1, y1, x2, y2 = map(int, rect_coords)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        if x1 >= x2 or y1 >= y2: return None
        return frame[y1:y2, x1:x2]

    def calculate_and_display_roi_values(self):
         """計算並顯示 5 個固定方框的 RGB 和亮度值"""
         if self.current_frame_processed is not None:
            for i in range(5):
                coords = self.static_rect_coords[i] # 使用儲存的固定座標
                roi = self.get_roi(self.current_frame_processed, coords)
                if roi is not None and roi.size > 0:
                    avg_bgr = cv2.mean(roi)[:3]
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    avg_luminance = cv2.mean(gray_roi)[0]
                    self.roi_labels[i].config(text=f"方框 {i+1}: R={avg_bgr[2]:.0f} G={avg_bgr[1]:.0f} B={avg_bgr[0]:.0f} L={avg_luminance:.0f}")
                else:
                    self.roi_labels[i].config(text=f"方框 {i+1}: (無效區域)")

    def calculate_and_display_sharpness(self):
        """計算並顯示清晰度方框的數值 (由 callback 觸發)"""
        if self.current_frame_original_gray is not None:
            coords = self.rectangle_sharpness.get_coords()
            if not coords:
                 self.clear_sharpness_labels()
                 return

            roi_gray = self.get_roi(self.current_frame_original_gray, coords)

            if roi_gray is not None and roi_gray.size > 0:
                tenengrad_val = self.calculate_tenengrad(roi_gray)
                lap_grad_val = self.calculate_laplacian_gradient(roi_gray)
                lap_var_val = self.calculate_laplacian_variance(roi_gray)

                self.tenengrad_label.config(text=f"Tenengrad: {tenengrad_val:.2f}")
                self.laplacian_grad_label.config(text=f"Laplacian Grad: {lap_grad_val:.2f}")
                self.laplacian_var_label.config(text=f"Laplacian Var: {lap_var_val:.2f}")
            else:
                self.clear_sharpness_labels()

    def clear_sharpness_labels(self):
        self.tenengrad_label.config(text="Tenengrad: ---")
        self.laplacian_grad_label.config(text="Laplacian Grad: ---")
        self.laplacian_var_label.config(text="Laplacian Var: ---")

    def apply_sharpness_rect_size(self):
        try:
            new_width = int(self.sharpness_width_entry.get())
            new_height = int(self.sharpness_height_entry.get())
            min_size = self.rectangle_sharpness.min_size

            if new_width < min_size or new_height < min_size:
                 messagebox.showwarning("尺寸無效", f"寬度和高度必須至少為 {min_size} 像素。")
                 return
            # 檢查是否超過畫布邊界 (基於當前左上角位置)
            coords = self.rectangle_sharpness.get_coords()
            if coords:
                x1, y1 = coords[0], coords[1]
                if x1 + new_width > self.width or y1 + new_height > self.height:
                     messagebox.showwarning("尺寸無效", f"設定的尺寸會超出影像邊界。")
                     return

            self.rectangle_sharpness.set_size(new_width, new_height)

        except ValueError:
            messagebox.showerror("輸入錯誤", "寬度和高度必須是有效的整數。")
        except tk.TclError:
             messagebox.showerror("錯誤", "無法設定尺寸，清晰度方框可能已被刪除。")
        except Exception as e:
             messagebox.showerror("錯誤", f"設定尺寸時發生錯誤: {e}")


    def update(self):
        ret, frame = self.vid.read()
        if ret:
            self.current_frame_original_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            brightness = self.exposure_scale.get()
            processed_frame = frame.astype(np.float32)
            processed_frame[:, :, 0] *= self.b_scale.get()
            processed_frame[:, :, 1] *= self.g_scale.get()
            processed_frame[:, :, 2] *= self.r_scale.get()
            processed_frame += brightness
            processed_frame = np.clip(processed_frame, 0, 255).astype(np.uint8)
            self.current_frame_processed = processed_frame.copy()

            cv_image_display = cv2.cvtColor(self.current_frame_processed, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv_image_display))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            # 將所有可互動的物件 (清晰度方框及其控制點) 移到最上層
            # 靜態方框不需要移動
            self.canvas.tag_raise("draggable")
            # 也可以明確指定清晰度方框的 tag
            # self.canvas.tag_raise(self.rectangle_sharpness.tag)

            # 計算固定 RGB 方框的值
            self.calculate_and_display_roi_values()
            # 清晰度值由 callback 更新

        else:
            print("無法讀取影像幀")
            self.current_frame_processed = None
            self.current_frame_original_gray = None
            for label in self.roi_labels:
                label.config(text=f"{label.cget('text').split(':')[0]}: ---")
            self.clear_sharpness_labels()

        self.window.after(self.delay, self.update)

    def on_closing(self):
        if self.vid.isOpened():
            self.vid.release()
        self.window.destroy()

# --- 主程式 ---
if __name__ == "__main__":
    try: import cv2
    except ImportError: print("錯誤：找不到 OpenCV。請執行: pip install opencv-python"); exit()
    try: from PIL import Image, ImageTk
    except ImportError: print("錯誤：找不到 Pillow。請執行: pip install Pillow"); exit()

    root = tk.Tk()
    app = CameraApp(root, "攝影機影像調整與分析")

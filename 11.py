import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import test

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.img_path = None
        self.face_coords = None
        self.face_path = None
        self.hr_img = None
        self.reconstructed_img = None
        # 图像路径和尺寸
        self.img_path = None
        self.img_width = None
        self.img_height = None

        # 人脸坐标
        self.face_coords = None
        self.create_widgets()

    def create_widgets(self):
        # 选择文件按钮
        self.select_button = tk.Button(self.master, text="选择文件", command=self.select_file)
        self.select_button.pack(side="top", pady=10)

        # Canvas显示图片
        self.canvas = tk.Canvas(self.master, width=1024, height=512)
        self.canvas.pack(side="top")

        # 圈出人脸按钮
        self.face_button = tk.Button(self.master, text="圈出人脸", command=self.draw_face)
        self.face_button.pack(side="left", padx=10)

        # 比较按钮
        self.compare_button = tk.Button(self.master, text="比较", command=self.compare)
        self.compare_button.pack(side="left", padx=10)

        # 超分辨率重建按钮
        self.reconstruct_button = tk.Button(self.master, text="超分辨率重建", command=self.reconstruct)
        self.reconstruct_button.pack(side="left", padx=10)

        # 退出按钮
        self.quit_button = tk.Button(self.master, text="退出", command=self.master.quit)
        self.quit_button.pack(side="right", padx=10)
        # 清除按钮
        self.clear_button = tk.Button(self.master, text="清除", command=self.clear)
        self.clear_button.pack(side="left", padx=10)

        # 重置按钮
        self.reset_button = tk.Button(self.master, text="重置", command=self.reset)
        self.reset_button.pack(side="left", padx=10)

    def select_file(self):
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=(
            ("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")))
        if not file_path:
            return
        img = Image.open(file_path)
        img = img.convert("RGB")

        self.img_width, self.img_height = img.size
        scale = min(1, 300/ self.img_width, 300 / self.img_height)
        # if img.width <= 300 and img.height <= 300:
        #     scale = max(400 / img.width, 400 / img.height)
        # else:
        #     scale = min(1, 300 / img.width, 300 / img.height)
        new_width = int(self.img_width * scale)
        new_height = int(self.img_height * scale)
        img = img.resize((new_width, new_height))
        self.img_tk = ImageTk.PhotoImage(img)  # 将ImageTk.PhotoImage对象绑定到实例变量上
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
        self.img_path = file_path
        self.face_coords = None
        self.face_path = None
        self.hr_img = None
        self.reconstructed_img = None
    def draw_face(self):
        # 如果没有选择文件，提示先选择文件
        if not self.img_path:
            messagebox.showerror("错误", "请先选择文件")
            return

        # 如果已经圈出人脸，提示先清除原来的圈
        if self.face_coords:
            messagebox.showerror("错误", "请先清除原来的圈")
            return
        scale = min(1, 300 / self.img_width, 300 / self.img_height)
        # if self.img_width <= 300 and self.img_height <= 300:
        #     scale = max(400 / self.img_width, 400 / self.img_height)
        # else:
        #     scale = min(1, 300 / self.img_width, 300 / self.img_height)
        # 标记圈人脸
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", lambda event: self.on_mouse_move(event, scale))
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.on_mouse_up(event, scale))

    def on_mouse_down(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_mouse_move(self, event, scale):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        if not self.face_coords:
            # 将画布坐标转换为图像坐标
            self.face_coords = (
                int(self.start_x / scale),
                int(self.start_y / scale),
                int(cur_x / scale),
                int(cur_y / scale),
            )
        else:
            self.canvas.delete("face")
            # 将画布坐标转换为图像坐标
            self.face_coords = (
                int(self.start_x / scale),
                int(self.start_y / scale),
                int(cur_x / scale),
                int(cur_y / scale),
            )
        x1, y1, x2, y2 = self.face_coords
        # 根据缩放比例调整坐标
        x1, y1, x2, y2 = int(x1 * scale), int(y1 * scale), int(x2 * scale), int(y2 * scale)
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="face")

    def on_mouse_up(self, event, scale):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")


    def get_face_img(self):
        if not self.face_coords:
            messagebox.showerror("错误", "请先圈出人脸")
            return None

        img = Image.open(self.img_path)
        cropped_img = img.crop(self.face_coords)
        cropped_img = cropped_img.convert("RGB")
        face_path = "face.jpg"
        cropped_img.save(face_path)
        self.face_path = face_path
        return face_path

    def compare(self):
        # 如果没有选择文件，提示先选择文件
        if not self.img_path:
            messagebox.showerror("错误", "请先选择文件")
            return

        # 获取圈出人脸的区域并显示在Canvas上
        face_path = self.get_face_img()
        if not face_path:
            return

        # 将圈出的人脸区域传入SRGAN模型进行超分辨率重建
        self.reconstructed_img = test.test(face_path)
        if self.reconstructed_img is None:
            messagebox.showerror("错误", "超分辨率重建失败")
            return

        # self.reconstructed_img = self.reconstructed_img.convert("RGB")
        # self.reconstructed_img = self.reconstructed_img.resize((100, 100))
        # self.reconstructed_img = ImageTk.PhotoImage(self.reconstructed_img)
        # self.canvas.create_image(512, 100, anchor=tk.NW, image=self.reconstructed_img)
        # self.reconstructed_img = np.array(self.reconstructed_img)
        # self.reconstructed_img = Image.fromarray(self.reconstructed_img)
        # top = tk.Toplevel(self.master)
        # top.title("对比")
        toplevel = tk.Toplevel(self.master)
        toplevel.title("对比")


        # 打开两张指定路径的图片
        image1 = Image.open('face.jpg')
        width1, height1 = image1.size

        if width1 <= 300 and height1 <= 300:
            scale = max(300 / width1, 300 / height1)
            new_width = int(width1 * scale)
            new_height = int(height1 * scale)
            image1 = image1.resize((new_width, new_height))
            width1, height1 = image1.size
        image2 = Image.open('results/test_srgan.jpg')
        image2 = image2.resize((width1,height1))
        # 将图片转换为 Tkinter PhotoImage 对象
        photo1 = ImageTk.PhotoImage(image1)
        photo2 = ImageTk.PhotoImage(image2)

        # 在新窗口中显示第一张图片
        label1 = tk.Label(toplevel, image=photo2,text="原图片", compound="top")
        label1.image = photo1
        label1.pack(side="left")

        # 在新窗口中显示第二张图片
        label2 = tk.Label(toplevel, image=photo1, text="超分辨后", compound="top")
        label2.image = photo2
        label2.pack(side="right")
        # left_img = Image.open('face.jpg')
        # right_img = Image.open('results/test_bicubic.jpg')
        #
        # # 调整图片大小
        # # left_img = left_img.resize((100, 100))
        # # right_img = right_img.resize((100, 100))
        #
        # # 创建左右两个Canvas控件
        # left_canvas = tk.Canvas(top, width=100, height=100)
        # left_canvas.pack(side="left")
        # right_canvas = tk.Canvas(top, width=100, height=100)
        # right_canvas.pack(side="right")
        #
        # # 在Canvas中显示图片
        # left_tk = ImageTk.PhotoImage(left_img)
        # left_canvas.create_image(512, 0, anchor=tk.NW, image=left_tk)
        # right_tk = ImageTk.PhotoImage(right_img)
        # right_canvas.create_image(0, 0, anchor=tk.NW, image=right_tk)

        # 创建关闭窗口按钮
        close_button = tk.Button(toplevel, text="关闭", command=toplevel.destroy)
        close_button.pack(pady=10)

    def reconstruct(self):
        # 如果没有选择文件，提示先选择文件
        if not self.img_path:
            messagebox.showerror("错误", "请先选择文件")
            return

        # 获取圈出人脸的区域
        face_path = self.get_face_img()
        if not face_path:
            return

        # 将圈出的人脸区域传入SRGAN模型进行超分辨率重建
        self.hr_img = test.test(face_path)
        if self.hr_img is None:
            messagebox.showerror("错误", "超分辨率重建失败")
            return
        toplevel = tk.Toplevel(self.master)
        toplevel.title("对比")

        # 打开两张指定路径的图片
        self.hr_img = Image.open(self.hr_img)
        # self.hr_img = self.hr_img.convert("RGB")
        self.hr_img = self.hr_img.resize((200, 200))
        photo1 = ImageTk.PhotoImage(self.hr_img)

        # 在新窗口中显示第一张图片
        label1 = tk.Label(toplevel, image=photo1, text="超分辨完成", compound="top")
        label1.image = photo1
        label1.pack(side="top")
        close_button = tk.Button(toplevel, text="关闭", command=toplevel.destroy)
        close_button.pack(pady=10)

        self.hr_img = self.hr_img.resize((100, 100))
        # self.hr_img = ImageTk.PhotoImage(self.hr_img)
        # self.canvas.create_image(512, 0, anchor=tk.NW, image=self.hr_img)
    def clear(self):
        self.canvas.delete("face")
        self.face_coords = None
        self.face_path = None
        self.hr_img = None
        self.reconstructed_img = None

    def reset(self):
        self.canvas.delete("all")
        self.img_path = None
        self.face_coords = None
        self.face_path = None
        self.hr_img = None
        self.reconstructed_img = None

    def exit(self):
        self.master.quit()
























if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


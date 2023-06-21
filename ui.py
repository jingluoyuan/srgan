import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# 初始化Tkinter窗口
root = tk.Tk()
root.title("圈出人脸并保存")
root.geometry("500x500")

# 创建画布
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

# 选择图片
def choose_image():
    filepath = filedialog.askopenfilename()
    image = cv2.imread(filepath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    show_image(image)

# 在画布上显示图片
def show_image(image):
    global img, img_tk
    img = Image.fromarray(image)
    # 对图像进行缩放
    img = img.resize((400, 400))
    img_tk = ImageTk.PhotoImage(image=img)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

# 在画布上绘制矩形
def draw_rectangle(event):
    canvas.delete("rect")
    x, y = event.x, event.y
    canvas.create_rectangle(x, y, x+100, y+100, outline='red', width=2, tags="rect")

# 保存图片
def save_image():
    rectangle = canvas.find_all()
    if len(rectangle) > 1:
        x1, y1, x2, y2 = canvas.coords(rectangle[-1])
        face = img.crop((x1, y1, x2, y2))
        filepath = filedialog.asksaveasfilename(defaultextension=".jpg")
        face.save(filepath)

# 创建按钮
choose_button = tk.Button(root, text="选择图片", command=choose_image)
choose_button.pack()

save_button = tk.Button(root, text="保存人脸", command=save_image)
save_button.pack()

# 绑定鼠标事件
canvas.bind("<Button-1>", draw_rectangle)

# 运行Tkinter窗口
root.mainloop()
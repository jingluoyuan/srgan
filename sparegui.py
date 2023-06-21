import os
import tkinter as tk
from PIL import Image, ImageTk
import  gui
def image_cropper(img_path, save_path):
    left_mouse_down_x = 0
    left_mouse_down_y = 0
    left_mouse_up_x = 0
    left_mouse_up_y = 0
    sole_rectangle = None

    def left_mouse_down(event):
        # print('鼠标左键按下')
        nonlocal left_mouse_down_x, left_mouse_down_y
        left_mouse_down_x = event.x
        left_mouse_down_y = event.y


    def left_mouse_up(event):
        # print('鼠标左键释放')
        nonlocal left_mouse_up_x, left_mouse_up_y
        left_mouse_up_x = event.x
        left_mouse_up_y = event.y
        corp_img(img_path, save_path, left_mouse_down_x, left_mouse_down_y,
                 left_mouse_up_x, left_mouse_up_y)


    def moving_mouse(event):
        # print('鼠标左键按下并移动')
        nonlocal sole_rectangle
        nonlocal left_mouse_down_x, left_mouse_down_y
        moving_mouse_x = event.x
        moving_mouse_y = event.y
        if sole_rectangle is not None:
            canvas.delete(sole_rectangle)  # 删除前一个矩形
        sole_rectangle = canvas.create_rectangle(left_mouse_down_x, left_mouse_down_y, moving_mouse_x,
                                                 moving_mouse_y, outline='red')


    def right_mouse_down(event):
        # print('鼠标右键按下')
        pass


    def right_mouse_up(event):
        # print('鼠标右键释放')
        pass


    def corp_img(source_path, save_path, x_begin, y_begin, x_end, y_end):
        if x_begin < x_end:
            min_x = x_begin
            max_x = x_end
        else:
            min_x = x_end
            max_x = x_begin
        if y_begin < y_end:
            min_y = y_begin
            max_y = y_end
        else:
            min_y = y_end
            max_y = y_begin
        save_path = os.path.abspath(save_path)
        if os.path.isfile(source_path):
            corp_image = Image.open(source_path)
            region = corp_image.crop((min_x, min_y, max_x, max_y))
            region.save(save_path)
            print('裁剪完成,保存于:{}'.format(save_path))
        else:
            print('未找到文件:{}'.format(source_path))

    win = tk.Tk()
    frame = tk.Frame(win)
    frame.pack()
    screenwidth = win.winfo_screenwidth()
    screenheight = win.winfo_screenheight()
    image = Image.open(img_path)
    image_x, image_y = image.size
    if image_x > screenwidth or image_y > screenheight:
        print('The picture size is too big,max should in:{}x{}, your:{}x{}'.format(screenwidth,
                                                                                   screenheight,
                                                                                   image_x,
                                                                                   image_y))
    img = ImageTk.PhotoImage(image)
    canvas = tk.Canvas(frame, width=image_x, height=image_y, bg='pink')
    i = canvas.create_image(0, 0, anchor='nw', image=img)
    canvas.pack()
    canvas.bind('<Button-1>', left_mouse_down)  # 鼠标左键按下
    canvas.bind('<ButtonRelease-1>', left_mouse_up)  # 鼠标左键释放
    canvas.bind('<Button-3>', right_mouse_down)  # 鼠标右键按下
    canvas.bind('<ButtonRelease-3>', right_mouse_up)  # 鼠标右键释放
    canvas.bind('<B1-Motion>', moving_mouse)  # 鼠标左键按下并移动
    win.mainloop()
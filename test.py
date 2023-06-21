from utils import *
from torch import nn
from models import SRResNet, Generator
import time
from PIL import Image

# 模型参数
large_kernel_size = 9  # 第一层卷积和最后一层卷积的核大小
small_kernel_size = 3  # 中间层卷积的核大小
n_channels = 64  # 中间层通道数
n_blocks = 16  # 残差模块数量
scaling_factor = 4  # 放大比例
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def test(img_path):
    # 预训练模型
    srgan_checkpoint = "./results/checkpoint_srgan.pth"

    # 加载模型SRResNet 或 SRGAN
    checkpoint = torch.load(srgan_checkpoint)
    generator = Generator(large_kernel_size=large_kernel_size,
                          small_kernel_size=small_kernel_size,
                          n_channels=n_channels,
                          n_blocks=n_blocks,
                          scaling_factor=scaling_factor)
    generator = generator.to(device)
    generator.load_state_dict(checkpoint['generator'])

    generator.eval()
    model = generator

    # 加载图像
    img = Image.open(img_path, mode='r')
    img = img.convert('RGB')

    # 双线性上采样
    Bicubic_img = img.resize((int(img.width * scaling_factor), int(img.height * scaling_factor)),
                             Image.Resampling.BICUBIC)
    Bicubic_img.save('./results/test_bicubic.jpg')

    # 图像预处理
    lr_img = convert_image(img, source='pil', target='imagenet-norm')
    lr_img.unsqueeze_(0)

    # 记录时间
    start = time.time()

    # 转移数据至设备
    lr_img = lr_img.to(device)  # (1, 3, w, h ), imagenet-normed

    # 模型推理
    # with torch.no_grad():
    #     sr_img = model(lr_img).squeeze(0).cpu().detach()  # (1, 3, w*scale, h*scale), in [-1, 1]
    #     sr_img = convert_image(sr_img, source='[-1, 1]', target='pil')
    # print('用时  {:.3f} 秒'.format(time.time() - start))
    # sr_img = sr_img.convert('RGB')
    #
    # # 保存图像
    # from os.path import expanduser, join
    #
    # # 保存图像到用户主目录
    # save_path = join(expanduser('~'), 'image.jpg')
    # sr_img.save(save_path)
    #
    # # 保存图像到当前工作目录
    # sr_img.save('image.jpg')
    # return sr_img
    with torch.no_grad():
        sr_img = model(lr_img).squeeze(0).cpu().detach()  # (1, 3, w*scale, h*scale), in [-1, 1]
        sr_img = convert_image(sr_img, source='[-1, 1]', target='pil')
        sr_img.save('./results/test_srgan.jpg')

    print('用时  {:.3f} 秒'.format(time.time() - start))
    return './results/test_srgan.jpg'
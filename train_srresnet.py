

import torch.backends.cudnn as cudnn
import torch
from torch import nn
from torchvision.utils import make_grid
from torch.utils.tensorboard import SummaryWriter
from models import SRResNet
from datasets import SRDataset
from utils import *

# 数据集参数
data_folder = './data/'          # 数据存放路径
lr_img_type = '[0, 255]'         # 低分辨率图像数据范围
hr_img_type = '[0, 255]'         # 高分辨率图像数据范围
crop_size = 96      # 高分辨率图像裁剪尺寸
scaling_factor = 4  # 放大比例

# 模型参数
large_kernel_size = 9   # 第一层卷积和最后一层卷积的核大小
small_kernel_size = 3   # 中间层卷积的核大小
n_channels = 64         # 中间层通道数
n_blocks = 16           # 残差模块数量
# 1个卷积模块+16个残差模块+1个卷积模块+2个子像素卷积模块+1个卷积模块
# 学习参数
checkpoint = None   # 预训练模型路径，如果不存在则为None
batch_size = 50     # 批大小
start_epoch = 1     # 轮数起始位置
epochs = 9       # 迭代轮数
workers = 4         # 工作线程数
lr = 1e-4           # 学习率

# 设备参数
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ngpu = 1            # 用来运行的gpu数量

cudnn.benchmark = True # 对卷积进行加速

writer = SummaryWriter() # 实时监控     使用命令 tensorboard --logdir runs  进行查看

def main():
    """
    训练.
    """
    global checkpoint,start_epoch,writer

    # 初始化
    model = SRResNet(large_kernel_size=large_kernel_size,
                        small_kernel_size=small_kernel_size,
                        n_channels=n_channels,
                        n_blocks=n_blocks,
                        scaling_factor=scaling_factor)
    # 初始化优化器
    optimizer = torch.optim.Adam(params=filter(lambda p: p.requires_grad, model.parameters()),lr=lr)

    # 迁移至默认设备进行训练
    model = model.to(device)
    criterion = nn.MSELoss().to(device)

    # 加载预训练模型
    if checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        print(f'loaded checkpoint {checkpoint} (epoch {start_epoch-1})')

    # 加载数据集
    train_dataset = SRDataset(data_folder,
                              lr_img_type=lr_img_type,
                              hr_img_type=hr_img_type,
                              split='train',
                              crop_size=crop_size,
                              scaling_factor=scaling_factor)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=workers, pin_memory=True, drop_last=True)

    # 开始迭代
    for epoch in range(start_epoch, epochs+1):
        print(f"\nEpoch {epoch}/{epochs}:")

        # 训练模型
        train_loss = train(train_loader=train_loader, model=model, criterion=criterion, optimizer=optimizer, epoch=epoch)

        # 保存模型参数
        if epoch % 10 == 0:
            save_checkpoint(epoch=epoch, model=model, optimizer=optimizer)

        # 实时监控
        writer.add_scalar('train_loss', train_loss, epoch)

    writer.close()

def train(train_loader, model, criterion, optimizer, epoch):
    """
    训练模型
    """
    model.train() # 将模型设置为训练模式
    train_losses = AverageMeter()

    for i, (lr_imgs, hr_imgs) in enumerate(train_loader):
        # 将数据移至默认设备
        lr_imgs = lr_imgs.to(device)
        hr_imgs = hr_imgs.to(device)

        # 正向传递
        sr_imgs = model(lr_imgs)

        # 计算损失
        loss = criterion(sr_imgs, hr_imgs)

        # 反向传递并更新权重
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # 记录损失
        train_losses.update(loss.item(), lr_imgs.size(0))

        # 每100个批次打印一次状态
        if i % 100 == 0:
            print(f"Epoch {epoch}, Batch {i}/{len(train_loader)}, Loss {loss.item():.6f}")

    print(f"Epoch {epoch}, Loss: {train_losses.avg:.6f}")
    return train_losses.avg

if __name__ == '__main__':
    main()
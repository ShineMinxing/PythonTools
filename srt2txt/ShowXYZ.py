import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取上一级目录
parent_dir = os.path.dirname(script_dir)
# 构建local_file目录路径
folder_path = os.path.join(parent_dir, 'local_file')

# 如果 local_file 文件夹不存在，退出程序
if not os.path.exists(folder_path):
    print(f"目录不存在：{folder_path}")
    exit()

# 获取所有 .txt 文件列表
txt_files = [f for f in os.listdir(folder_path) if( f.endswith('_xyz.txt') or f.endswith('_py.txt'))]

# 创建所有图形对象
figures = []

for txt_filename in txt_files:
    txt_file_path = os.path.join(folder_path, txt_filename)

    # 读取 txt 文件中的数据
    timestamps = []
    x_coords = []
    y_coords = []
    z_coords = []

    with open(txt_file_path, 'r') as file:
        for line in file:
            data = line.split()
            if len(data) >= 2:  # 至少有时间和一个坐标
                # 添加时间戳
                timestamps.append(f"{data[0]} {data[1]}")
                # 添加坐标数据
                if len(data) >= 3:
                    x_coords.append(float(data[2]))
                if len(data) >= 4:
                    y_coords.append(float(data[3]))
                if len(data) >= 5:
                    z_coords.append(float(data[4]))

    # 根据数据列数确定绘图类型
    if len(z_coords) > 0:  # 有Z坐标 - 3D图
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(x_coords, y_coords, z_coords, label='3D Path')
        ax.set_title(txt_filename.replace('.txt', ''))
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
    elif len(y_coords) > 0:  # 有Y坐标 - 2D XY图
        fig, ax = plt.subplots()
        ax.plot(x_coords, y_coords, label='Spherical Coordinate Path')
        ax.set_title(txt_filename.replace('.txt', ''))
        ax.set_xlabel('azimuth')
        ax.set_ylabel('elevation')
        ax.legend()
    else:  # 只有X坐标 - 时间-X图
        fig, ax = plt.subplots()
        ax.plot(timestamps, x_coords, label='X over Time')
        ax.set_title(txt_filename.replace('.txt', ''))
        ax.set_xlabel('Time')
        ax.set_ylabel('X')
        # 旋转x轴标签以避免重叠
        plt.xticks(rotation=45)
        ax.legend()
    
    figures.append(fig)
    print(f"绘制完成：{txt_filename}")

# 显示所有图形
plt.show()

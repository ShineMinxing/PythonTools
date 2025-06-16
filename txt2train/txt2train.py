import os
import numpy as np
import yaml

def load_config(config_path):
    """
    加载配置文件，获取是否覆盖文件、噪声协方差、预测步数和压缩设置等
    :param config_path: 配置文件路径
    :return: 配置字典
    """
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def add_gaussian_noise(data, noise_covariance):
    """
    向数据添加高斯噪声
    :param data: 输入数据
    :param noise_covariance: 高斯噪声的协方差
    :return: 添加噪声后的数据
    """
    noise = np.random.normal(0, noise_covariance, len(data))
    return data + noise

def process_file(input_path, config):
    """
    处理单个 _py.txt 文件，生成用于训练的输入输出数据
    :param input_path: 输入文件路径
    :param config: 配置字典
    :return: None
    """
    # 从配置中获取 A 和 B，若没有配置则使用默认值
    A = config.get('A', 25)
    B = config.get('B', 1)

    output_input_path = input_path.replace('.txt', '_input.txt')
    output_output_path = input_path.replace('.txt', '_output.txt')

    # 如果输出文件已经存在且配置要求不覆盖，跳过文件
    if os.path.exists(output_input_path) and not config['overwrite']:
        print(f"文件已存在且不覆盖，跳过文件: {output_input_path}")
        return
    if os.path.exists(output_output_path) and not config['overwrite']:
        print(f"文件已存在且不覆盖，跳过文件: {output_output_path}")
        return

    # 读取文件数据
    azimuth_data = []
    elevation_data = []

    with open(input_path, 'r') as infile:
        prev_azimuth = None
        prev_elevation = None

        for line in infile:
            parts = line.split()
            azimuth = float(parts[2])
            elevation = float(parts[3])

            # 如果配置要求压缩数据且当前行的 azimuth 和 elevation 与上一行相同，则跳过
            if config['compress_data'] and azimuth == prev_azimuth and elevation == prev_elevation:
                continue

            # 记录数据
            azimuth_data.append(azimuth)
            elevation_data.append(elevation)

            # 更新上一行的 azimuth 和 elevation
            prev_azimuth = azimuth
            prev_elevation = elevation

    # 生成输入数据 (添加噪声并保存)
    azimuth_input = []
    elevation_input = []

    # 为整个数据集添加噪声
    azimuth_data_with_noise = add_gaussian_noise(np.array(azimuth_data), config['azimuth_noise_covariance'])
    elevation_data_with_noise = add_gaussian_noise(np.array(elevation_data), config['elevation_noise_covariance'])

    # 生成输入数据
    azimuth_input = []
    elevation_input = []

    for i in range(0, len(azimuth_data) - A, 1):
        azimuth_segment = azimuth_data_with_noise[i:i+A]  # 使用带噪声的 azimuth 数据
        elevation_segment = elevation_data_with_noise[i:i+A]  # 使用带噪声的 elevation 数据

        azimuth_input.extend(azimuth_segment)
        elevation_input.extend(elevation_segment)

    # 写入 _py_input.txt 文件（每一行是连续的 A 个 azimuth 和 A 个 elevation，加上噪声）
    with open(output_input_path, 'w') as outfile:
        for i in range(0, len(azimuth_input) - A, A):
            azimuth_segment = azimuth_input[i:i+A]
            elevation_segment = elevation_input[i:i+A]
            # 写入一行数据
            outfile.write(" ".join([f"{x:.6f}" for x in azimuth_segment + elevation_segment]) + "\n")

    # 生成 _py_output.txt 文件（没有噪声的第 A+B 个 azimuth 和 elevation）
    azimuth_output = azimuth_data[A + B:]
    elevation_output = elevation_data[A + B:]
    with open(output_output_path, 'w') as outfile:
        for i in range(len(azimuth_output)):
            # 写入没有噪声的输出数据
            outfile.write(f"{azimuth_output[i]:.6f} {elevation_output[i]:.6f}\n")

def main():
    # 获取脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # 获取配置文件路径
    config_path = os.path.join(script_dir, 'config.yaml')

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        print(f"错误: 配置文件 {config_path} 不存在")
        return

    # 加载配置文件
    config = load_config(config_path)

    # 获取 local_file 目录路径
    local_file_dir = os.path.join(parent_dir, 'local_file')

    if not os.path.exists(local_file_dir):
        print(f"错误: 目录 {local_file_dir} 不存在")
        return

    # 处理所有以 _py.txt 结尾的文件
    for filename in os.listdir(local_file_dir):
        if filename.endswith('_py.txt'):
            input_path = os.path.join(local_file_dir, filename)
            print(f"正在处理文件: {input_path}")
            process_file(input_path, config)

    print("所有文件处理完成!")

if __name__ == "__main__":
    main()

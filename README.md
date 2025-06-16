# SMX的Python工具箱

本项目是SMX的各种小工具：

---

## srt2txt：SRT → XYZ → 方向角/俯仰角 → 可视化

1. **原始轨迹文件**  
   - 位于 `raw_file/` 目录，后缀 `.SRT`。  
   - 由 DJI Mini 3 Pro 拍摄时自动生成，记录无人机的时序经纬度与高度等。

2. **生成 XYZ 轨迹**  
   - 脚本：`srt2txt/SRT2TXT.py`  
   - 功能：将 `.SRT` 中的经纬度/高度数据，转换为以轨迹起点为原点的 **三维** (X, Y, Z) 轨迹。  
   - 输出：保存到 `local_file/` 目录下，文件名后缀为 `_xyz.txt`。  
   - 注意：`local_file/` 目录内容通过 `.gitignore` 排除，不会被提交到 GitHub。

3. **生成方向角 & 俯仰角数据**  
   - 脚本：`srt2txt/XYZ2PY.py`  
   - 功能：以python文件中指定的“观测点”为参考，将 XYZ 轨迹转化为 **方位角 (azimuth)** 与 **俯仰角 (elevation)** 序列。  
   - 输出：同样保存到 `local_file/`，文件后缀为 `_py.txt`。

4. **轨迹可视化检查**  
   - 脚本：`srt2txt/ShowXYZ.py`  
   - 功能：分别绘制三维轨迹和二维（X-Y、方位-俯仰）曲线，用于快速肉眼检查数据分布与合理性。

---

## txt2train：角度数据 → 神经网络训练集

1. **准备训练数据**  
   - 脚本：`txt2train/txt2train.py`  
   - 功能：将 `local_file/` 中以 `_py.txt` 结尾的方向/俯仰角序列，按照 **滑动窗口**（长度 A）+ **预测步长**（B）策略，生成神经网络的 **输入** 与 **输出** 文件：  
     - `*_input.txt`：每行包含 A 个 azimuth + A 个 elevation，并加入 Gaussian 噪声。  
     - `*_output.txt`：每行包含原始（无噪声）的第 A+B 个 azimuth & elevation。  
   - 配置：请编辑 `txt2train/config.yaml`，设置  
     ```yaml
     overwrite: true                   # 是否覆盖已存在的输入/输出文件
     azimuth_noise_covariance: 0.5     # azimuth 噪声方差
     elevation_noise_covariance: 0.5   # elevation 噪声方差
     A: 25                             # 输入窗口大小
     B: 1                              # 预测步长
     compress_data: true               # 是否压缩去重连续相同数据
     ```

2. **神经网络训练**  
   - 本项目不包含网络模型实现，您可以前往以下仓库获取完整的训练脚本与模型示例：  
     [ShineMinxing/PythonNeuralNetwork](https://github.com/ShineMinxing/PythonNeuralNetwork.git)

---

## 视频介绍
[![srt2txt txt2train使用方法](https://i0.hdslb.com/bfs/archive/650062a4aeb28cb7bfdd15e658de1523f537efb7.jpg)](https://www.bilibili.com/video/BV1ytMizEEdG)

---
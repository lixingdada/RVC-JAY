# RVC 语音变声

基于 [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) 搭建的语音变声环境。

## 快速开始

克隆后请阅读 [环境恢复指南](./环境恢复指南.md)，按步骤操作即可恢复使用。

简单来说：

```bash
git clone https://github.com/lixingdada/RVC.git
cd RVC
python -m venv .venv
.venv\Scripts\activate
pip install -r requirments_cu128_py312.txt
```

然后按 [环境恢复指南](./环境恢复指南.md) 下载模型文件，双击 `启动RVC.bat` 即可启动。

## 使用流程

1. 双击 `启动RVC.bat` 启动网页界面
2. 上传带伴奏的歌曲，使用人声分离功能去掉伴奏
3. 将分离出的人声上传到模型推理页面，选择 `singer.pth` 模型进行变声

详细参数说明见 [RVC操作文档.html](./RVC操作文档.html)。

## 文件说明

| 文件/目录 | 说明 |
|---|---|
| `启动RVC.bat` | 启动脚本 |
| `清理.bat` | 临时文件清理脚本 |
| `环境恢复指南.md` | 克隆后的环境恢复教程 |
| `RVC操作文档.html` | 参数设置操作文档 |
| `assets/weights/singer.pth` | 训练完成的歌手模型 |
| `assets/indices/` | 检索特征索引 |

## 致谢

本项目基于 RVC-Project 的 [Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)，遵循 MIT 许可证。

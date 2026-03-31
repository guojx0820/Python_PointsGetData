# PaperPilot Nano（低门槛点击即用）

你现在有两种用法：

## 方案 A（推荐给非程序员）：桌面版点击即用

### Windows
1. 双击 `start_paperpilot.bat`
2. 在界面里点击“选择论文文件并分析”
3. 点击“导出当前结果为 CSV”

### macOS / Linux
1. 双击（或终端运行）`start_paperpilot.sh`
2. 在界面里点击“选择论文文件并分析”
3. 点击“导出当前结果为 CSV”

> 桌面版主程序：`PaperPilotNano.py`（使用 Python 标准库，无第三方依赖）。

---

## 方案 B：API 服务版（给开发者）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

打开接口文档：http://127.0.0.1:8000/docs

关键接口：
- `POST /api/upload`
- `GET /api/reports`
- `GET /api/reports/{id}/export.csv`

---

## 一键打包成可执行文件（发给不会编程的用户）

在你自己的电脑执行：

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name PaperPilotNano PaperPilotNano.py
```

打包后可执行文件在 `dist/` 目录：
- Windows: `PaperPilotNano.exe`
- macOS/Linux: `PaperPilotNano`

你把这个文件发给用户，用户双击即可运行（无需理解代码）。

---

## 其它文件
- `opc_factory.py`：自动生成 PRD/执行计划/变现方案。
- `configs/vertical_research_assistant.json`：垂直方向配置模板。
- `docs/OPC_AI_AUTOBUILD_GUIDE_CN.md`：从 0 到变现的操作指南。

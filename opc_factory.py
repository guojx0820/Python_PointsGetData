"""
OPC Auto Factory (One-Person Company)
-------------------------------------
一个可扩展的“AI 自动化软件工厂”骨架，用于：
1) 读取垂直领域产品配置
2) 生成 PRD / 技术任务清单 / 上线检查清单
3) 输出变现执行步骤

说明：
- 该脚本默认离线可运行，先生成结构化文档与执行计划。
- 后续可在此基础上接入真实大模型 API 和 CI/CD。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class ProductSpec:
    project_name: str
    vertical: str
    target_users: list[str]
    core_pain: list[str]
    core_features: list[str]
    pricing: dict
    channels: list[str]
    stack: dict


def load_spec(path: str | Path) -> ProductSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ProductSpec(**data)


def _lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def generate_prd(spec: ProductSpec) -> str:
    return (
        f"# {spec.project_name} - PRD（自动生成）\n\n"
        "## 1. 产品定位\n"
        f"- 垂直领域：{spec.vertical}\n"
        f"- 核心用户：{', '.join(spec.target_users)}\n\n"
        "## 2. 核心痛点\n"
        f"{_lines(spec.core_pain)}\n\n"
        "## 3. MVP 功能\n"
        f"{_lines(spec.core_features)}\n\n"
        "## 4. 技术栈\n"
        f"- 后端：{spec.stack.get('backend')}\n"
        f"- 前端：{spec.stack.get('frontend')}\n"
        f"- 数据库：{spec.stack.get('db')}\n"
        f"- 异步任务：{spec.stack.get('queue')}\n"
        f"- LLM：{spec.stack.get('llm_provider')}\n\n"
        "## 5. 商业化\n"
        f"- Free：{json.dumps(spec.pricing.get('free', {}), ensure_ascii=False)}\n"
        f"- Pro：{json.dumps(spec.pricing.get('pro', {}), ensure_ascii=False)}\n"
        f"- Lab：{json.dumps(spec.pricing.get('lab', {}), ensure_ascii=False)}\n\n"
        "## 6. 获客渠道\n"
        f"{_lines(spec.channels)}\n"
    )


def generate_execution_plan(spec: ProductSpec) -> str:
    steps = [
        "第 1 周：完成需求冻结、页面原型、数据字段定义。",
        "第 2 周：实现论文上传、解析、结构化提取 API。",
        "第 3 周：实现对比表导出、队列任务、账单与订阅。",
        "第 4 周：灰度内测、支付上线、内容渠道冷启动。",
        "第 5-8 周：按用户反馈迭代，重点优化准确率和导出体验。",
    ]

    kpi = [
        "7 天内获取 10 个目标用户访谈",
        "14 天内上线可付费 MVP",
        "30 天内达成首批 5 个付费用户",
        "90 天内 MRR >= 3000 美元",
    ]

    return (
        f"# {spec.project_name} - 8 周执行计划（自动生成）\n\n"
        + "## 时间线\n"
        + "\n".join(f"- {s}" for s in steps)
        + "\n\n## KPI\n"
        + "\n".join(f"- {x}" for x in kpi)
        + "\n"
    )


def generate_monetization_playbook(spec: ProductSpec) -> str:
    return (
        f"# {spec.project_name} - 变现作战手册（自动生成）\n\n"
        "## 定价结构\n"
        "- Free：限制额度，主打试用。\n"
        "- Pro：个人研究者主力套餐。\n"
        "- Lab：团队协作与批量配额。\n\n"
        "## 快速变现步骤\n"
        "1. 上线 Stripe/Lemon Squeezy 支付页。\n"
        "2. 在注册后第 1 次导出结果时触发付费墙。\n"
        "3. 提供“上传 3 篇论文免费生成对比报告”。\n"
        "4. 输出可分享报告（带产品水印）形成裂变。\n"
        "5. 每周发布 2 篇垂直领域解读内容导流。\n\n"
        "## 自动化运营建议\n"
        "- 使用事件埋点监控：上传次数、导出次数、付费转化率。\n"
        "- 每 48 小时自动总结用户常见失败案例并生成改进任务。\n"
        "- 周度自动生成收入日报 + 渠道 ROI 报告。\n"
    )


def write_output(spec: ProductSpec, out_dir: str | Path = "output") -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    files = {
        "PRD.md": generate_prd(spec),
        "PLAN.md": generate_execution_plan(spec),
        "MONETIZATION.md": generate_monetization_playbook(spec),
    }

    written: list[Path] = []
    for name, content in files.items():
        target = out / name
        target.write_text(content, encoding="utf-8")
        written.append(target)

    return written


def main() -> None:
    spec = load_spec("configs/vertical_research_assistant.json")
    generated = write_output(spec)
    print("已生成以下文件：")
    for p in generated:
        print(f"- {p}")


if __name__ == "__main__":
    main()

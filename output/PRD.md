# PaperPilot Nano - PRD（自动生成）

## 1. 产品定位
- 垂直领域：材料科学（锂电池电解液）
- 核心用户：硕士/博士研究生, 高校课题组, 工业研发工程师

## 2. 核心痛点
- 论文筛选耗时
- 实验条件参数查找困难
- 文献复现实验设计效率低

## 3. MVP 功能
- 上传论文PDF后自动抽取：材料配方、实验温度、倍率、循环寿命
- 生成对比表（CSV/Excel）
- 给出可复现实验步骤草案
- 输出引用格式与摘要

## 4. 技术栈
- 后端：FastAPI
- 前端：Next.js
- 数据库：PostgreSQL
- 异步任务：Redis + Celery
- LLM：OpenAI-compatible API

## 5. 商业化
- Free：{"monthly_papers": 10, "export": "CSV"}
- Pro：{"price_usd_monthly": 29, "monthly_papers": 300, "export": "CSV + Excel + Notion"}
- Lab：{"price_usd_monthly": 149, "seats": 10}

## 6. 获客渠道
- 小红书/知乎垂类内容
- 高校实验室微信群
- GitHub + Product Hunt

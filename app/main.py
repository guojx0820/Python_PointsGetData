from __future__ import annotations

import csv
import io
import json

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from .extractor import build_abstract, extract_metrics
from .models import ExtractionResponse
from .paywall import UsageTracker
from .storage import get_report, init_db, list_reports, save_report


app = FastAPI(title="PaperPilot Nano MVP", version="0.1.0")
usage_tracker = UsageTracker()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/upload", response_model=ExtractionResponse)
async def upload_paper(
    file: UploadFile = File(...),
    x_api_key: str = Header(default="demo-free-user"),
    x_plan: str = Header(default="free"),
) -> ExtractionResponse:
    allowed, used, limit = usage_tracker.check_and_consume(x_api_key, x_plan)
    if not allowed:
        raise HTTPException(
            status_code=402,
            detail=f"已达到当前套餐月配额 {limit}。请升级套餐继续使用。",
        )

    content = await file.read()
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="文件解析失败，请上传 UTF-8 文本或可提取文本的 PDF。") from exc

    metrics = extract_metrics(text)
    abstract = build_abstract(text)
    report_id = save_report(file.filename, x_plan, metrics, abstract)

    response = ExtractionResponse(
        report_id=report_id,
        filename=file.filename,
        plan=x_plan,
        metrics=metrics,
        abstract=abstract,
    )

    return JSONResponse(
        status_code=200,
        content={
            **response.model_dump(),
            "usage": {"used": used, "limit": limit, "remaining": limit - used},
        },
    )


@app.get("/api/reports")
def reports() -> list[dict]:
    return [r.model_dump() for r in list_reports()]


@app.get("/api/reports/{report_id}/export.csv")
def export_csv(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    metrics = json.loads(report.metrics_json)
    if not metrics:
        raise HTTPException(status_code=400, detail="报告无可导出指标")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["metric", "value", "unit"])
    writer.writeheader()
    for row in metrics:
        writer.writerow(row)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"},
    )

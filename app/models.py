from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedMetric(BaseModel):
    metric: str
    value: str
    unit: str | None = None


class ExtractionResponse(BaseModel):
    report_id: int
    filename: str
    plan: str
    metrics: list[ExtractedMetric] = Field(default_factory=list)
    abstract: str


class ReportRecord(BaseModel):
    id: int
    filename: str
    plan: str
    metrics_json: str
    abstract: str

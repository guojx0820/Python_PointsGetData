from __future__ import annotations

import csv
import json
import re
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "PaperPilot Nano（点击即用版）"
DB_PATH = Path("data/desktop_reports.db")

PATTERNS: dict[str, str] = {
    "temperature": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>°C|C|K)",
    "cycle_life": r"(?P<value>\d{2,5})\s?(?P<unit>cycles?)",
    "coulombic_efficiency": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>%)",
    "capacity": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>mAh/g|mAh g-1|Ah/kg)",
    "voltage": r"(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>V)",
}


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                abstract TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def extract_metrics(text: str) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for metric, pattern in PATTERNS.items():
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            found.append(
                {
                    "metric": metric,
                    "value": m.group("value"),
                    "unit": m.groupdict().get("unit") or "",
                }
            )

    uniq: dict[tuple[str, str, str], dict[str, str]] = {}
    for x in found:
        uniq[(x["metric"], x["value"], x["unit"])] = x
    return list(uniq.values())[:200]


def build_abstract(text: str, max_chars: int = 300) -> str:
    clean = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3] + "..."


def save_report(filename: str, abstract: str, metrics: list[dict[str, str]]) -> int:
    payload = json.dumps(metrics, ensure_ascii=False)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO reports(filename, abstract, metrics_json) VALUES (?, ?, ?)",
            (filename, abstract, payload),
        )
        return int(cur.lastrowid)


def list_reports() -> list[tuple[int, str, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, filename, created_at FROM reports ORDER BY id DESC"
        ).fetchall()
    return [(int(r[0]), str(r[1]), str(r[2])) for r in rows]


def get_report_metrics(report_id: int) -> list[dict[str, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT metrics_json FROM reports WHERE id = ?", (report_id,)).fetchone()
    if not row:
        return []
    return json.loads(row[0])


class PaperPilotApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("980x640")

        self.abstract_var = tk.StringVar(value="请先点击“选择论文文件并分析”。")
        self.current_report_id: int | None = None

        self._build_ui()
        self._refresh_report_list()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="选择论文文件并分析", command=self.analyze_file).pack(side="left")
        ttk.Button(top, text="导出当前结果为 CSV", command=self.export_current_csv).pack(side="left", padx=8)
        ttk.Button(top, text="刷新历史报告", command=self._refresh_report_list).pack(side="left")

        left = ttk.LabelFrame(self.root, text="抽取结果", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        self.tree = ttk.Treeview(left, columns=("metric", "value", "unit"), show="headings", height=20)
        self.tree.heading("metric", text="指标")
        self.tree.heading("value", text="数值")
        self.tree.heading("unit", text="单位")
        self.tree.column("metric", width=200)
        self.tree.column("value", width=120)
        self.tree.column("unit", width=120)
        self.tree.pack(fill="both", expand=True)

        abstract_box = ttk.LabelFrame(left, text="摘要", padding=10)
        abstract_box.pack(fill="x", pady=(8, 0))
        ttk.Label(abstract_box, textvariable=self.abstract_var, wraplength=620, justify="left").pack(fill="x")

        right = ttk.LabelFrame(self.root, text="历史报告", padding=10)
        right.pack(side="right", fill="y", padx=(5, 10), pady=10)

        self.report_list = tk.Listbox(right, width=42, height=28)
        self.report_list.pack(fill="both", expand=True)
        self.report_list.bind("<<ListboxSelect>>", self.load_selected_report)

    def analyze_file(self) -> None:
        path = filedialog.askopenfilename(
            title="选择论文文本/PDF(可提取文本)",
            filetypes=[("Text/PDF", "*.txt *.md *.pdf"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            raw = Path(path).read_bytes()
            text = raw.decode("utf-8", errors="ignore")
            if not text.strip():
                raise ValueError("文件内容为空或无法提取文本")
        except Exception as exc:
            messagebox.showerror("读取失败", f"无法读取文件：{exc}")
            return

        metrics = extract_metrics(text)
        abstract = build_abstract(text)
        report_id = save_report(Path(path).name, abstract, metrics)

        self.current_report_id = report_id
        self._render_metrics(metrics)
        self.abstract_var.set(abstract)
        self._refresh_report_list()
        messagebox.showinfo("完成", f"分析完成，报告ID：{report_id}，共抽取 {len(metrics)} 条指标。")

    def _render_metrics(self, metrics: list[dict[str, str]]) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in metrics:
            self.tree.insert("", "end", values=(row["metric"], row["value"], row["unit"]))

    def _refresh_report_list(self) -> None:
        self.report_list.delete(0, tk.END)
        for report_id, filename, created_at in list_reports():
            self.report_list.insert(tk.END, f"#{report_id} | {filename} | {created_at}")

    def load_selected_report(self, _event: object) -> None:
        sel = self.report_list.curselection()
        if not sel:
            return
        item = self.report_list.get(sel[0])
        report_id = int(item.split("|")[0].strip().replace("#", ""))
        metrics = get_report_metrics(report_id)
        self.current_report_id = report_id
        self._render_metrics(metrics)
        self.abstract_var.set(f"已加载历史报告 #{report_id}。")

    def export_current_csv(self) -> None:
        if self.current_report_id is None:
            messagebox.showwarning("提示", "请先分析文件或选择历史报告。")
            return

        metrics = get_report_metrics(self.current_report_id)
        if not metrics:
            messagebox.showwarning("提示", "当前报告无可导出数据。")
            return

        out_path = filedialog.asksaveasfilename(
            title="导出 CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"report_{self.current_report_id}.csv",
        )
        if not out_path:
            return

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["metric", "value", "unit"])
            writer.writeheader()
            for row in metrics:
                writer.writerow(row)

        messagebox.showinfo("导出成功", f"CSV 已保存到：\n{out_path}")


def main() -> None:
    init_db()
    root = tk.Tk()
    PaperPilotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

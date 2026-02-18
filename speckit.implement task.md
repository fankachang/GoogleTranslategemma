speckit 實作任務說明

目的：建立 speckit.implement task.md，說明各階段要做的工作，並在每個階段完成時進行提交紀錄。

階段 1 — 初始草稿
- 描述任務範圍與目標
- 建立本檔並提交（已完成）

階段 2 — 逐步實作
- 根據需求填寫實作細節
- 每完成一小步即 commit
- 子任務：
  - 設計資料模型與資料結構（已完成）
    - Speckit 主要資料結構：
      - Project: { id: string, name: string, description: string, created_at: datetime }
      - Task: { id: string, project_id: string, title: string, status: enum(pending, in_progress, done), assignee?: string, created_at: datetime, updated_at: datetime }
      - Event: { id: string, task_id: string, type: string, payload: object, timestamp: datetime }
    - 儲存選項：支援 JSON 檔案儲存與 SQLite（視需求切換）
    - 資料驗證：使用簡單 schema 驗證（例如 JSON Schema 或自訂驗證函式）
  - 撰寫核心函式與模組
  - 加入單元測試
  - 撰寫使用範例與 README 範例段落

階段 3 — 驗收與整理
- 整理內容、補充註解與文件
- 最後一次 commit，標記任務完成

提交紀錄說明：
每個 commit 應包含清楚的一行摘要（中文），必要時加上說明段落，並在 commit 訊息末尾加入 Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>。

（此檔為初稿，之後依階段更新並在完成時提交。）
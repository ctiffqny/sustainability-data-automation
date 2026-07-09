from dataclasses import dataclass, field


@dataclass
class FileInfo:
    source: str
    target: str


@dataclass
class ConfigSummary:
    category: str
    source_sheet: str
    target_sheet: str


@dataclass
class PreviewResult:
    status: str
    category: str
    updated_rows: list[dict] = field(default_factory=list)
    new_columns: list[str] = field(default_factory=list)
    skipped_columns: list[str] = field(default_factory=list)
    inconsistency_output: list[str] = field(default_factory=list)
    preview_session_id: str | None = None
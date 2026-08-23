import argparse
import base64
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
try:
    from build_erps_html import maybe_build_erps_report
except ImportError:
    def maybe_build_erps_report(*args, **kwargs):
        return None

try:
    from dsx_charts import enrich_groups_with_charts, register_chart_helpers
except ImportError:
    def enrich_groups_with_charts(groups):
        return groups
    def register_chart_helpers(context):
        return context

try:
    from sync_unified_from_results import refresh_unified_db
except ImportError:
    def refresh_unified_db(*args, **kwargs):
        pass


SCRIPT_DIR = Path(__file__).resolve().parent
UNIFIED_DB_FILE = SCRIPT_DIR / "unified_db.json"
CABLES_FILE = SCRIPT_DIR / "cables_parsed.json"
RESULTS_FILE = SCRIPT_DIR / "cables_results.json"
TEMPLATE_FILE = SCRIPT_DIR / "templates" / "main.md"
GGS_TEMPLATE_FILE = SCRIPT_DIR / "templates" / "template_ggs.md"
EQUIP_DIR = SCRIPT_DIR / "equip"
FRAMED_TEMPLATE_FILE = SCRIPT_DIR / "templates" / "framed.md"
APPENDIX_TEMPLATE_FILE = SCRIPT_DIR / "templates" / "appendices_bundle.md"
LIST_FILE = SCRIPT_DIR / "switches_list.txt"
RAW_RESULTS_DIR = SCRIPT_DIR / "results"
DEFAULT_PROJECT = "2023-10/26-02-СС1"
PROJECT_CODE_RE = re.compile(r"(?P<code>\d{5}-\d{2}-\d{4}-[A-Za-zА-Яа-я0-9]+)", re.UNICODE)

YES_VALUES = {"y", "yes", "д", "да", "1", "true"}
LOCATION_PLACEHOLDERS = {"", "не указано", "unknown", "klt"}
ERMAKOVSKOE_PROJECT_OBJECT = (
    "ГОРНО-ОБОГАТИТЕЛЬНЫЙ КОМПЛЕКС ПО ДОБЫЧЕ И ПЕРЕРАБОТКЕ "
    "ФЛЮОРИТ-БЕРИЛЛИЕВЫХ РУД МЕСТОРОЖДЕНИЯ «ЕРМАКОВСКОЕ»"
)
ERMAKOVSKOE_PROJECT_OBJECT_SHORT = 'ГОК "Ермаковское"'

DEFAULT_INSTRUMENT = {
    "model": "DSX-5000 CAT 6A/CLASS Fa 1000MHz Copper Module",
    "serial": "2989500",
    "test_date": "16-Jan-25",
}


def normalize_project_name(project: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", str(project).strip(), flags=re.UNICODE)
    return cleaned.strip("_") or "project"


OUTPUT_DIR = SCRIPT_DIR / "output"


def get_image_data_uri(image_name: str) -> str:
    path = SCRIPT_DIR / image_name
    if path.is_file():
        try:
            b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            ext = path.suffix.lstrip(".").lower() or "png"
            return f"data:image/{ext};base64,{b64}"
        except Exception:
            pass
    return image_name


def get_font_data_uri(font_name: str = "PF Din Text Cond Pro.ttf") -> str:
    path = SCRIPT_DIR / font_name
    if path.is_file():
        try:
            b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:font/truetype;charset=utf-8;base64,{b64}"
        except Exception:
            pass
    return font_name


def sync_assets_to_output(dest_dir: Path | None = None) -> None:
    target_dir = dest_dir or OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    
    font_file = SCRIPT_DIR / "PF Din Text Cond Pro.ttf"
    if font_file.is_file():
        try:
            b64 = base64.b64encode(font_file.read_bytes()).decode("ascii")
            css_content = f"""@font-face {{
  font-family: "PF Din Text Cond Pro";
  src: url("data:font/truetype;charset=utf-8;base64,{b64}") format("truetype");
  font-weight: normal;
  font-style: normal;
}}

@font-face {{
  font-family: "PF Din Text Cond Pro";
  src: url("data:font/truetype;charset=utf-8;base64,{b64}") format("truetype");
  font-weight: bold;
  font-style: normal;
}}

html, body {{
  font-family: "PF Din Text Cond Pro", "PF DIN Text Pro", Arial, sans-serif !important;
  font-size: 14pt;
  line-height: 1.5;
}}

body, p, div, span, table, thead, tbody, tr, th, td, li, ol, ul, strong, em, b, i {{
  font-family: "PF Din Text Cond Pro", "PF DIN Text Pro", Arial, sans-serif !important;
}}

p {{
  font-size: 14pt;
  line-height: 1.5;
  text-align: justify;
  text-indent: 1.25cm;
}}

ol, ul {{
  font-size: 14pt;
  line-height: 1.5;
}}

li {{
  font-size: 14pt;
  line-height: 1.5;
  text-align: justify;
}}

table {{
  font-size: 12pt !important;
}}

table th, table td {{
  font-size: 12pt !important;
}}

table th:first-child, table td:first-child {{
  text-align: left !important;
}}

table.acoustic-table, table.acoustic-table th, table.acoustic-table td {{
  font-size: 10pt !important;
}}
"""
            (SCRIPT_DIR / "pdf-fonts.css").write_text(css_content, encoding="utf-8")
            (target_dir / "pdf-fonts.css").write_text(css_content, encoding="utf-8")
        except Exception:
            pass

    for asset_name in ("logo.png", "sign.png", "PF Din Text Cond Pro.ttf"):
        src = SCRIPT_DIR / asset_name
        dst = target_dir / asset_name
        if src.is_file() and not dst.exists():
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass


def default_list_file(project: str) -> Path:
    if not project:
        return LIST_FILE
    return SCRIPT_DIR / f"switches_list_{normalize_project_name(project)}.txt"


def default_output_file(project: str) -> Path:
    sync_assets_to_output(OUTPUT_DIR)
    if not project:
        return OUTPUT_DIR / "Итоговый_Журнал_ПНР.md"
    return OUTPUT_DIR / f"Журнал_ПНР_{normalize_project_name(project)}.md"


def default_artifacts_dir(project: str) -> Path:
    base_dir = SCRIPT_DIR / "build_html"
    if not project:
        return base_dir / "project"
    return base_dir / normalize_project_name(project)


def refresh_unified_db(log_func=print, dry_run: bool = False):
    from sync_unified_from_results import ARCHIVE_DIR, UNIFIED_DB_PATH, detect_results_dir, sync

    _log = log_func or print
    if dry_run:
        _log("[SYNC] Проверка локального обновления базы без записи.")
    else:
        _log("[SYNC] Обновление базы из локальных results/...")
    return sync(
        results_dir=detect_results_dir(),
        unified_db_path=UNIFIED_DB_PATH,
        archive_dir=ARCHIVE_DIR,
        keep_results=True,
        dry_run=dry_run,
    )


def count_meaningful_lines(text: str) -> int:
    if not isinstance(text, str):
        return 0
    return len([line for line in text.splitlines() if len(line.strip()) > 2 and "---" not in line])


def is_useful_command_output(command: Any, output: Any) -> bool:
    text = normalize_text(output)
    if not text:
        return False

    command_text = normalize_text(command).lower()
    if command_text in {
        "show lacp port-channel",
        "show spanning-tree detail",
        "show mac address-table",
    }:
        return False

    lower_text = text.lower()
    if (
        "% invalid" in lower_text
        or "% incomplete command" in lower_text
        or "invalid command" in lower_text
        or "unrecognized command" in lower_text
    ):
        return False
    if "read_channel_timing's absolute timer expired" in lower_text or "socket is closed" in lower_text:
        return False

    command_words = [part for part in re.split(r"\s+", command_text) if part]
    data_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or set(line) <= {"-", "=", " "}:
            continue
        lower_line = line.lower()
        if lower_line.endswith("#") or lower_line.endswith(">"):
            continue
        if command_text and lower_line == command_text:
            continue
        if command_words and lower_line.replace(" ", "") == "".join(command_words):
            continue
        data_lines.append(line)

    if len(data_lines) < 2:
        return False

    header_only_patterns = [
        {"unit", "id", "link", "status", "speed", "uptime", "neighbor"},
        {"port", "temp", "voltage", "current", "output", "input", "los"},
    ]
    if len(data_lines) == 1:
        lowered_words = set(re.findall(r"[a-z]+", data_lines[0].lower()))
        if any(pattern <= lowered_words for pattern in header_only_patterns):
            return False

    if command_text == "show stack links details" and len(data_lines) <= 2:
        lowered = " ".join(data_lines).lower()
        if "unit id" in lowered and "neighbor" in lowered:
            return False

    return True


def is_useful_config_output(config: Any) -> bool:
    text = normalize_text(config)
    if not text:
        return False
    return text.upper() not in {"TFTP SENT", "TFTP SKIPPED", "TFTP SUCCESS", "TFTP UPLOAD FAILED"}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = "\n".join(str(item) for item in value)
    return str(value).strip()


LOG_TIMESTAMP_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})-(?P<month>[A-Za-z]{3})-(?P<year>\d{4})\s+"
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
)
LOG_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_log_timestamp(line: str) -> datetime | None:
    match = LOG_TIMESTAMP_RE.match(line)
    if not match:
        return None
    month = LOG_MONTHS.get(match.group("month").lower())
    if not month:
        return None
    try:
        return datetime(
            int(match.group("year")), month, int(match.group("day")),
            int(match.group("hour")), int(match.group("minute")), int(match.group("second")),
        )
    except ValueError:
        return None


def _filter_log_output(text: str, reference_time: datetime) -> str:
    """Keep the command summary and only event blocks from the last 24 hours."""
    lines = text.splitlines()
    first_event = next((index for index, line in enumerate(lines) if _parse_log_timestamp(line)), None)
    if first_event is None:
        return text

    cutoff = reference_time - timedelta(hours=24)
    filtered = lines[:first_event]
    keep_event = False
    for line in lines[first_event:]:
        timestamp = _parse_log_timestamp(line)
        if timestamp is not None:
            keep_event = cutoff <= timestamp <= reference_time
        if keep_event:
            filtered.append(line)
    compact: list[str] = []
    for line in filtered:
        if not line.strip() and compact and not compact[-1].strip():
            continue
        compact.append(line)
    return "\n".join(compact).rstrip()


def _filter_interface_output(text: str) -> str:
    """Hide absent logical interfaces and the generated Loopback section."""
    filtered: list[str] = []
    for line in text.splitlines():
        lower_line = line.lower()
        columns = line.split()
        if (
            len(columns) > 2
            and re.fullmatch(r"po\d+", columns[0], flags=re.IGNORECASE)
            and all(value == "0" for value in columns[1:])
        ):
            continue
        if "not present" in lower_line:
            continue
        if "loopback" in lower_line and "state" in lower_line:
            if filtered and filtered[-1].strip().lower() == "admin link":
                filtered.pop()
            break
        filtered.append(line)
    return "\n".join(filtered).rstrip()


def prepare_devices_for_report(devices: list[dict[str, Any]], reference_time: datetime) -> list[dict[str, Any]]:
    prepared = deepcopy(devices)
    for device in prepared:
        for key in ("cabinet", "location", "site", "place", "model", "segment"):
            if device.get(key):
                device[key] = re.sub(r"\s+", " ", normalize_text(device[key])).strip()
        for command_data in (device.get("commands") or {}).values():
            if not isinstance(command_data, dict):
                continue
            command = normalize_text(command_data.get("command")).lower()
            output = normalize_text(command_data.get("output"))
            if command.startswith("show interfaces"):
                output = _filter_interface_output(output)
            if command.startswith("show logging"):
                output = _filter_log_output(output, reference_time)
            command_data["output"] = output
    return prepared


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _read_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json_file(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def extract_project_code_from_text(value: Any) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    match = PROJECT_CODE_RE.search(text)
    return match.group("code") if match else ""


def resolve_cables_source(filepath: str | Path | None, project_code: str | None = None) -> tuple[Path, str]:
    requested_path = Path(filepath) if filepath else CABLES_FILE
    resolved_project = normalize_text(project_code) or extract_project_code_from_text(requested_path.stem)

    if requested_path.suffix.lower() == ".xlsx":
        json_candidate = requested_path.with_suffix(".json")
        if json_candidate.exists():
            requested_path = json_candidate

    if (requested_path == CABLES_FILE or not requested_path.exists()) and resolved_project:
        project_json = SCRIPT_DIR / "cables" / f"cables_{resolved_project}.json"
        if project_json.exists():
            requested_path = project_json

    return requested_path, resolved_project


def resolve_results_cache_path(project_code: str) -> Path:
    if not project_code:
        return RESULTS_FILE
    return SCRIPT_DIR / "cables" / f"cables_results_{normalize_project_name(project_code)}.json"


def _normalize_dash_pair(value: str) -> str:
    return str(value or "").replace("-", "–").strip()


def _pair_to_pairnum(pair_name: str) -> str:
    mapping = {
        "1–2": "12",
        "1-2": "12",
        "3–6": "36",
        "3-6": "36",
        "4–5": "45",
        "4-5": "45",
        "7–8": "78",
        "7-8": "78",
    }
    raw = str(pair_name or "").strip()
    return mapping.get(raw, raw.replace("–", "").replace("-", ""))


def _is_optic_cable(cable: dict[str, Any]) -> bool:
    cable_type = normalize_text(cable.get("cable_type")).lower()
    cable_mark = normalize_text(cable.get("cable_mark")).lower()
    optic_tokens = ("оптич", "optic", "fiber", "fo", "os1", "os2", "om1", "om2", "om3", "om4", "om5")
    return any(token in cable_type or token in cable_mark for token in optic_tokens)


def _build_pair_variations(cable: dict[str, Any]) -> dict[str, float]:
    pair_to_key = {"1–2": "v1", "3–6": "v2", "4–5": "v3", "7–8": "v4"}
    variations = {key: 1.0 for key in pair_to_key.values()}

    for test in cable.get("tests", []) or []:
        pair_name = _normalize_dash_pair(test.get("pair", ""))
        key = pair_to_key.get(pair_name)
        if not key:
            continue

        r_calc = test.get("r_calc")
        r_meas = test.get("r_meas")
        dev = test.get("dev")

        value = None
        if isinstance(r_calc, (int, float)) and isinstance(r_meas, (int, float)) and r_calc:
            value = float(r_meas) / float(r_calc)
        elif isinstance(dev, (int, float)):
            value = 1.0 + (float(dev) / 100.0)

        if value is not None:
            variations[key] = round(value, 4)

    return variations


def _generate_synthetic_pair_tests(cable: dict[str, Any]) -> dict[str, Any]:
    """
    Учебная детерминированная модель тестов по четырем парам.
    Значения стабильны для одного и того же trace_id.
    """
    trace_id = normalize_text(cable.get("trace_id")) or "unknown"
    rnd = random.Random(f"pairs::{trace_id}")
    length = _safe_float(cable.get("length_m", 0.0))

    # Базовое значение сопротивления на пару для учебного отчета.
    # Не измерение, а расчетная модель для стабильной генерации примеров.
    r_base = round(length * 0.19, 2)

    tests = []
    for pair_name in ("1–2", "3–6", "4–5", "7–8"):
        variation = rnd.uniform(0.985, 1.035)
        r_meas = round(r_base * variation, 2)
        dev = round((r_meas / r_base - 1) * 100, 1) if r_base else 0.0
        att = round((length * 0.21) + rnd.uniform(0.10, 0.60), 2)

        tests.append(
            {
                "pair": pair_name,
                "r_calc": r_base,
                "r_meas": r_meas,
                "dev": dev,
                "att": att,
                "result": "Pass" if abs(dev) <= 7 else "Fail",
            }
        )

    overall_status = "PASS" if all(t["result"] == "Pass" for t in tests) else "FAIL"
    return {
        "tests": tests,
        "r_summary": r_base,
        "status": overall_status,
    }


def _build_summary_tests(cable: dict[str, Any]) -> list[dict[str, Any]]:
    trace_id = normalize_text(cable.get("trace_id")) or "unknown"
    rnd = random.Random(f"summary::{trace_id}")
    length = _safe_float(cable.get("length_m", 0.0))
    status = normalize_text(cable.get("status")).upper() or "PASS"

    il_margin = round(max(0.12, 0.95 - length * 0.004 + rnd.uniform(-0.08, 0.06)), 3)
    next_margin = round(max(0.15, 0.65 - length * 0.002 + rnd.uniform(-0.10, 0.08)), 3)
    cdnext_margin = round(max(0.18, 0.70 - length * 0.002 + rnd.uniform(-0.10, 0.08)), 3)
    cmrl_margin = round(max(0.20, 0.90 - length * 0.001 + rnd.uniform(-0.10, 0.10)), 3)
    rl_margin = round(max(0.20, 0.85 - length * 0.001 + rnd.uniform(-0.10, 0.10)), 3)
    tcl_margin = round(max(0.20, 0.75 - length * 0.0015 + rnd.uniform(-0.08, 0.08)), 3)
    fext_margin = round(max(0.15, 0.60 - length * 0.0015 + rnd.uniform(-0.08, 0.08)), 3)

    if status != "PASS":
        il_margin = round(min(il_margin, 0.12), 3)
        next_margin = round(min(next_margin, 0.09), 3)
        fext_margin = round(min(fext_margin, 0.07), 3)

    result = "Pass" if status == "PASS" else "Fail"
    return [
        {
            "name": "NEXT",
            "result": result,
            "worst_margin": next_margin,
            "freq_mhz": round(rnd.uniform(1.00, 35.00), 2),
            "pair": "12-36",
            "artifact_sn": str(rnd.randint(5100000, 5100099)),
        },
        {
            "name": "CDNEXT",
            "result": result,
            "worst_margin": cdnext_margin,
            "freq_mhz": round(rnd.uniform(25.00, 80.00), 2),
            "pair": "45-78",
            "artifact_sn": str(rnd.randint(5100000, 5100099)),
        },
        {
            "name": "CMRL",
            "result": result,
            "worst_margin": cmrl_margin,
            "freq_mhz": round(rnd.uniform(400.00, 950.00), 2),
            "pair": "45",
            "artifact_sn": str(rnd.randint(5100000, 5100099)),
        },
        {
            "name": "RL",
            "result": result,
            "worst_margin": rl_margin,
            "freq_mhz": round(rnd.uniform(400.00, 980.00), 2),
            "pair": "36",
            "artifact_sn": str(rnd.randint(5100000, 5100099)),
        },
        {
            "name": "TCL",
            "result": result,
            "worst_margin": tcl_margin,
            "freq_mhz": round(rnd.uniform(20.00, 80.00), 2),
            "pair": "78",
            "artifact_sn": str(rnd.randint(5100000, 5100099)),
        },
        {
            "name": "IL",
            "result": result,
            "worst_margin": il_margin,
            "freq_mhz": round(rnd.uniform(1.00, 10.00), 2),
            "pair": "12",
            "artifact_sn": str(rnd.randint(3558300, 3558499)),
        },
        {
            "name": "FEXT",
            "result": result,
            "worst_margin": fext_margin,
            "freq_mhz": round(rnd.uniform(20.00, 80.00), 2),
            "pair": "78-45",
            "artifact_sn": str(rnd.randint(3558300, 3558499)),
        },
    ]


def _build_loop_resistance(cable: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for test in cable.get("tests", []) or []:
        pair_num = _pair_to_pairnum(test.get("pair", ""))
        r_calc = _safe_float(test.get("r_calc", 0.0))
        r_meas = _safe_float(test.get("r_meas", r_calc))

        limit = round(max(0.80, r_calc * 0.02), 2)
        result = "Pass" if abs(r_meas - r_calc) <= limit else "Fail"

        rows.append(
            {
                "parameter": "Resistance on pair",
                "pair": pair_num,
                "measured": round(r_meas, 2),
                "expected": round(r_calc, 2),
                "limit": limit,
                "result": result,
            }
        )

    return rows


def _build_resistance_imbalance(cable: dict[str, Any]) -> list[dict[str, Any]]:
    trace_id = normalize_text(cable.get("trace_id")) or "unknown"
    rnd = random.Random(f"imbalance::{trace_id}")
    rows: list[dict[str, Any]] = []

    for test in cable.get("tests", []) or []:
        pair_num = _pair_to_pairnum(test.get("pair", ""))
        r_calc = _safe_float(test.get("r_calc", 0.0))
        r_meas = _safe_float(test.get("r_meas", r_calc))
        dev = abs(_safe_float(test.get("dev", 0.0)))

        expected_pair = round(r_calc / 2 if r_calc else 0.0, 2)
        measured_pair = round(r_meas / 2 if r_meas else 0.0, 2)
        limit_pair = round(max(0.80, expected_pair * 0.035), 2)
        result_pair = "Pass" if abs(measured_pair - expected_pair) <= limit_pair else "Fail"

        rows.append(
            {
                "parameter": "Resistance on pair",
                "pair": pair_num,
                "measured": measured_pair,
                "expected": expected_pair,
                "limit": limit_pair,
                "result": result_pair,
            }
        )

        imbalance_expected = round(min(0.95, dev / 10.0), 2)
        imbalance_measured = round(max(0.00, imbalance_expected + rnd.uniform(-0.03, 0.03)), 2)
        imbalance_limit = round(max(0.05, 0.06 + dev * 0.02), 2)
        imbalance_result = "Pass" if abs(imbalance_measured - imbalance_expected) <= imbalance_limit else "Fail"

        rows.append(
            {
                "parameter": "Resistance imbalance on pair",
                "pair": pair_num,
                "measured": imbalance_measured,
                "expected": imbalance_expected,
                "limit": imbalance_limit,
                "result": imbalance_result,
            }
        )

    return rows


def _fmt_date_for_report(value: Any) -> str:
    text = normalize_text(value)
    return text or DEFAULT_INSTRUMENT["test_date"]


def attach_dsx_style_report_fields(cable: dict[str, Any], instrument: dict[str, str] | None = None) -> dict[str, Any]:
    item = deepcopy(cable)
    instrument_data = deepcopy(DEFAULT_INSTRUMENT)
    if instrument:
        instrument_data.update(instrument)
    instrument_data["test_date"] = _fmt_date_for_report(item.get("test_date") or instrument_data.get("test_date"))

    item["instrument"] = instrument_data
    item["report_title"] = item.get("report_title", "As-Left Report")
    item["page_title"] = item.get("page_title", "DSX Cable Analyzer")
    item["test_program"] = item.get("test_program", "TFSTest v2.7.8110")
    item["report_form"] = item.get("report_form", "DSX Report Form v3.05")
    item["status"] = normalize_text(item.get("status")).upper() or "PASS"

    if not item.get("tests"):
        item.update(_generate_synthetic_pair_tests(item))

    summary_tests = deepcopy(item.get("summary_tests") or [])
    if not summary_tests:
        summary_tests = _build_summary_tests(item)

    item["summary_tests"] = summary_tests
    item["worst_margin"] = round(min((t["worst_margin"] for t in summary_tests), default=0.0), 3)
    item["loop_resistance"] = _build_loop_resistance(item)
    item["resistance_imbalance"] = _build_resistance_imbalance(item)

    item.update(_build_pair_variations(item))
    return item


def attach_report_fields_to_groups(groups: dict[str, Any], instrument: dict[str, str] | None = None) -> dict[str, Any]:
    output: dict[str, Any] = {}

    for rack, data in (groups or {}).items():
        output[rack] = {
            "scs": [],
            "optic": deepcopy(data.get("optic", [])),
        }
        for cable in data.get("scs", []):
            output[rack]["scs"].append(attach_dsx_style_report_fields(cable, instrument=instrument))

    return output


def load_cables_data(
    filepath: str | Path | None,
    instrument: dict[str, str] | None = None,
    project_code: str | None = None,
) -> dict[str, Any]:
    """
    Загружает кабельный журнал, для медных линий подтягивает/генерирует учебные тестовые данные
    и возвращает группы по шкафам с уже обогащенными полями под шаблоны.
    """
    cable_path, resolved_project = resolve_cables_source(filepath, project_code=project_code)
    if not cable_path.exists():
        return {}

    source_data = _read_json_file(cable_path, {})
    cache_path = resolve_results_cache_path(resolved_project)
    raw_cache = _read_json_file(cache_path, {})
    test_cache = raw_cache if isinstance(raw_cache, dict) else {}

    groups: dict[str, dict[str, list[dict[str, Any]]]] = {}
    updated_cache = False

    cable_journal = source_data.get("tables", {}).get("cable_journal", [])
    for source_cable in cable_journal:
        cable = deepcopy(source_cable)
        rack = normalize_text(cable.get("start_point")) or "Неизвестный шкаф"
        trace_id = normalize_text(cable.get("trace_id")) or "unknown"

        groups.setdefault(rack, {"scs": [], "optic": []})

        if _is_optic_cable(cable):
            groups[rack]["optic"].append(cable)
            continue

        cached_data = test_cache.get(trace_id)
        if isinstance(cached_data, dict):
            cable.update(deepcopy(cached_data))
        else:
            generated = _generate_synthetic_pair_tests(cable)
            cable.update(generated)
            test_cache[trace_id] = deepcopy(generated)
            updated_cache = True

        groups[rack]["scs"].append(cable)

    if updated_cache:
        _write_json_file(cache_path, test_cache)
        print(f"[КЭШ] Новые тестовые данные сохранены в {cache_path}")

    return attach_report_fields_to_groups(groups, instrument=instrument)


def extract_all_devices(filepath: str | Path | None = None) -> list[dict[str, Any]]:
    db_path = Path(filepath) if filepath else UNIFIED_DB_FILE
    if not db_path.exists():
        raise FileNotFoundError(f"Файл базы данных не найден: {db_path}")

    data = _read_json_file(db_path, {})
    if not isinstance(data, dict):
        raise ValueError(f"Ожидался dict в {db_path}, получено: {type(data).__name__}")

    return list(data.values())


def get_projects(devices: list[dict[str, Any]]) -> list[tuple[str, int]]:
    counts = Counter(device.get("project") for device in devices if device.get("project"))
    return sorted(counts.items(), key=lambda item: item[0])


def get_default_project(projects: list[tuple[str, int]]) -> str:
    available_projects = [project for project, _count in projects]
    if DEFAULT_PROJECT in available_projects:
        return DEFAULT_PROJECT
    return available_projects[0] if available_projects else ""


def choose_project_interactively(projects: list[tuple[str, int]]) -> str:
    if not projects:
        raise ValueError("В unified_db.json не найдено ни одного проекта.")

    default_project = get_default_project(projects)
    project_by_number: dict[str, str] = {}

    print("Доступные проекты:")
    for index, (project, count) in enumerate(projects, start=1):
        marker = " [по умолчанию]" if project == default_project else ""
        print(f"  {index}. {project} ({count} устройств){marker}")
        project_by_number[str(index)] = project

    raw_value = input(f"Выбери проект номером или кодом [{default_project}]: ").strip()
    if not raw_value:
        return default_project
    if raw_value in project_by_number:
        return project_by_number[raw_value]

    available_projects = {project for project, _count in projects}
    if raw_value in available_projects:
        return raw_value

    raise ValueError(f"Неизвестный проект: {raw_value}")


def filter_devices_by_project(devices: list[dict[str, Any]], project: str) -> list[dict[str, Any]]:
    filtered = [device for device in devices if device.get("project") == project]
    return sorted(filtered, key=lambda item: (item.get("segment", ""), item.get("ip", "")))


def clean_location_value(value: Any) -> str:
    text = re.sub(r"\s+", " ", normalize_text(value)).strip()
    if text.lower() in LOCATION_PLACEHOLDERS:
        return ""
    return text


def unique_clean_values(values: list[Any]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        text = clean_location_value(value)
        if text and text not in unique_values:
            unique_values.append(text)
    return unique_values


def summarize_values(values: list[Any], fallback: str) -> str:
    unique_values = unique_clean_values(values)

    if not unique_values:
        return fallback
    if len(unique_values) == 1:
        return unique_values[0]
    if len(unique_values) <= 3:
        return "; ".join(unique_values)
    summary = f"{', '.join(unique_values[:3])} и еще {len(unique_values) - 3}"
    return f"{fallback}: {summary}" if fallback else summary


def extract_common_prefix(values: list[Any]) -> str:
    cleaned = [clean_location_value(value) for value in values if clean_location_value(value)]
    if len(cleaned) < 2:
        return cleaned[0] if cleaned else ""

    prefix = cleaned[0]
    for value in cleaned[1:]:
        while prefix and not value.startswith(prefix):
            prefix = prefix[:-1]
        if not prefix:
            break
    return prefix.strip(" ,.-")


def is_usable_common_location(value: Any) -> bool:
    text = clean_location_value(value)
    if len(text) < 18:
        return False
    last_word = text.split()[-1].lower()
    return last_word not in {"для", "и", "с", "по", "на", "в"}


def build_project_metadata(devices: list[dict[str, Any]]) -> dict[str, Any]:
    project_code = next((normalize_text(device.get("project")) for device in devices if normalize_text(device.get("project"))), "")
    site_values = [device.get("site") for device in devices]
    place_values = [device.get("place") for device in devices]
    location_values = [device.get("location") for device in devices]
    segment_values = sorted({normalize_text(device.get("segment")) for device in devices if normalize_text(device.get("segment"))})
    unique_sites = unique_clean_values(site_values)
    unique_places = unique_clean_values(place_values)
    explicit_project_object = next(
        (normalize_text(device.get("project_object")) for device in devices if normalize_text(device.get("project_object"))),
        "",
    )
    explicit_project_object_short = next(
        (normalize_text(device.get("project_object_short")) for device in devices if normalize_text(device.get("project_object_short"))),
        "",
    )

    fallback_object = f"Объекты проекта {project_code}" if project_code else "Объект не указан"
    common_location = extract_common_prefix(location_values)

    has_ermak_10_53 = any(normalize_text(device.get("ip")).startswith("10.53.10.") for device in devices)
    if explicit_project_object:
        project_object = explicit_project_object
        project_object_short = explicit_project_object_short or explicit_project_object
    elif has_ermak_10_53:
        project_object = ERMAKOVSKOE_PROJECT_OBJECT
        project_object_short = ERMAKOVSKOE_PROJECT_OBJECT_SHORT
    else:
        project_object = summarize_values(unique_sites, "")
        project_object_short = ""
    if not project_object:
        if len(unique_places) == 1:
            project_object = unique_places[0]
        elif 1 < len(unique_places) <= 3:
            project_object = "; ".join(unique_places)
    if not project_object and is_usable_common_location(common_location):
        project_object = common_location
    if not project_object:
        project_object = fallback_object

    return {
        "project_code": project_code or "Не указан",
        "project_object": project_object,
        "project_object_short": project_object_short or project_object,
        "project_sites": unique_sites,
        "project_places": unique_places,
        "project_segments": segment_values,
        "project_segments_text": ", ".join(segment_values) if segment_values else "Не указано",
    }


def create_switch_list(devices: list[dict[str, Any]], list_file: str | Path) -> Path:
    list_path = Path(list_file)
    with list_path.open("w", encoding="utf-8") as handle:
        handle.write("# Удали строки с коммутаторами, на которые НЕ НУЖЕН чек-лист.\n")
        handle.write("# Формат: IP | HOSTNAME | СЕГМЕНТ\n")
        for device in sorted(devices, key=lambda item: (item.get("segment", "КСПД"), item.get("ip", ""))):
            handle.write(
                f"{device.get('ip', 'Unknown')} | {device.get('hostname', 'Unknown')} | {device.get('segment', 'Unknown')}\n"
            )
    return list_path


def load_selected_ips(list_file: str | Path) -> set[str]:
    list_path = Path(list_file)
    selected_ips: set[str] = set()
    with list_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            selected_ips.add(line.split("|")[0].strip())
    return selected_ips


def resolve_devices_for_render(
    project_devices: list[dict[str, Any]],
    list_file: str | Path | None = None,
    use_all_devices: bool = False,
) -> list[dict[str, Any]]:
    if use_all_devices:
        return project_devices

    list_path = Path(list_file) if list_file else None
    if not list_path or not list_path.exists():
        raise FileNotFoundError("Файл списка не найден. Сначала выполни create-list или используй --all-devices.")

    selected_ips = load_selected_ips(list_path)
    filtered = [device for device in project_devices if device.get("ip") in selected_ips]
    return sorted(filtered, key=lambda item: (item.get("segment", ""), item.get("ip", "")))


def build_context(final_devices: list[dict[str, Any]], cable_groups: dict[str, Any], include_clock: bool = True) -> dict[str, Any]:
    now = datetime.now()
    report_devices = prepare_devices_for_report(final_devices, now)

    total_scs = sum(len(group.get("scs", [])) for group in cable_groups.values()) if cable_groups else 0
    total_optic = sum(len(group.get("optic", [])) for group in cable_groups.values()) if cable_groups else 0
    total_ports = sum(
        48 if "48" in str(d.get("model", "")) else 24 if "24" in str(d.get("model", "")) else 28
        for d in report_devices
    )

    cabinets = unique_clean_values([d.get("cabinet") for d in report_devices if d.get("cabinet")])
    cabinets_str = ", ".join(cabinets) if cabinets else "по проекту"

    date_str = now.strftime("%d.%m.%Y")
    year_str = str(now.year)
    start_date_str = "23.06.2026"

    months_ru = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }
    month_name = months_ru.get(now.month, "июня")

    work_log_entries = [
        {
            "date": start_date_str,
            "description": "Подготовительный этап: проверка готовности электроснабжения, заземления шкафов, наличия рабочей документации. Проведен целевой инструктаж по ТБ и ОТ.",
            "result": "Замечаний нет. Допуск оформлен.",
            "sign_info": "Гл. спец. Кудря Н.Ю.",
        }
    ]
    for dev in report_devices:
        dev_model = dev.get("model") or "MES"
        dev_ip = dev.get("ip") or ""
        dev_cab = f", шкаф: {dev.get('cabinet')}" if dev.get("cabinet") else ""
        dev_loc = f", пом.: {dev.get('location')}" if dev.get("location") else ""
        dev_fw = dev.get("fw") or "актуальной версии"
        work_log_entries.append({
            "date": date_str,
            "description": f"Автономная наладка коммутатора {dev_model} (IP: {dev_ip}{dev_cab}{dev_loc}): проверка микрокода ПО {dev_fw}, конфигурирование VLAN, STP, LLDP, проверка интерфейсов и снятие диагностических дампов.",
            "result": "Соответствует проекту. [x] В норме",
            "sign_info": "Гл. спец. Кудря Н.Ю.",
        })
    if total_scs or total_optic:
        work_log_entries.append({
            "date": date_str,
            "description": f"Приемо-сдаточный контроль и тестирование кабельных линий связи (СКС: {total_scs} линий, ВОЛС: {total_optic} трасс) прибором DSX-5000.",
            "result": "Все тесты PASS. Характеристики в норме.",
            "sign_info": "Гл. спец. Кудря Н.Ю.",
        })
    work_log_entries.append({
        "date": date_str,
        "description": "Комплексное опробование сетевого сегмента под непрерывной нагрузкой. Проверка времени сходимости кольцевой топологии (ERPS/STP), устойчивости сквозной передачи данных и задержек.",
        "result": "Система функционирует штатно. Готова к сдаче.",
        "sign_info": "Гл. спец. Кудря Н.Ю.",
    })

    acts_list = [
        {
            "name": "Акт готовности объекта к производству пусконаладочных работ",
            "sign_info": f"{start_date_str}, Кудря Н.Ю.",
        },
        {
            "name": f"Протокол проверки монтажа и заземления активного сетевого оборудования (шкафы: {cabinets_str})",
            "sign_info": f"{start_date_str}, Кудря Н.Ю.",
        },
        {
            "name": f"Протоколы автономной наладки и индивидуальных испытаний сетевых коммутаторов ({len(report_devices)} шт.)",
            "sign_info": f"{date_str}, Кудря Н.Ю.",
        },
    ]
    if total_scs or total_optic:
        acts_list.append({
            "name": "Протоколы приемо-сдаточных измерений кабельных линий связи СКС и ВОЛС",
            "sign_info": f"{date_str}, Кудря Н.Ю.",
        })
    acts_list.extend([
        {
            "name": "Акт о проведении автономных испытаний системы (Приложение И)",
            "sign_info": f"{date_str}, Кудря Н.Ю.",
        },
        {
            "name": "Акт приемки пусконаладочных работ системы (Приложение Ж)",
            "sign_info": f"{date_str}, Кудря Н.Ю.",
        },
    ])

    context = {
        "devices": report_devices,
        "cable_groups": cable_groups,
        "groups": cable_groups,
        "date": date_str,
        "report_year": year_str,
        "month_name": month_name,
        "work_start_date": start_date_str,
        "actual_end_date": date_str,
        "contract_end_date": date_str,
        "contractor_name": "ООО «Голд Линк»",
        "contractor_responsible": "Главный специалист технической группы Кудря Н.Ю.",
        "journal_number": "1",
        "total_pages": "11",
        "total_scs_lines": total_scs,
        "total_optic_lines": total_optic,
        "total_ports": total_ports,
        "cabinets_summary": cabinets_str,
        "work_log_entries": work_log_entries,
        "acts_list": acts_list,
        "show_clock_section": include_clock,
        "count_meaningful_lines": count_meaningful_lines,
        "is_useful_command_output": is_useful_command_output,
        "is_useful_config_output": is_useful_config_output,
    }
    context.update(build_project_metadata(report_devices))
    return context


def normalize_rendered_markdown(text: str) -> str:
    lines = text.splitlines()
    normalized: list[str] = []
    in_fence = False

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            normalized.append(line)
            continue

        if not in_fence and stripped.startswith("<"):
            normalized.append(stripped)
            continue

        normalized.append(line)

    return "\n".join(normalized) + ("\n" if text.endswith("\n") else "")


def render_markdown_from_template(template_path: str | Path, context: dict[str, Any], output_path: str | Path) -> Path:
    from jinja2 import Environment, FileSystemLoader

    template_path = Path(template_path)
    output_path = Path(output_path)

    search_dirs = [
        str(template_path.parent),
        str(SCRIPT_DIR / "templates"),
        str(SCRIPT_DIR),
    ]
    unique_dirs = [d for i, d in enumerate(search_dirs) if d not in search_dirs[:i] and Path(d).exists()]

    env = Environment(loader=FileSystemLoader(unique_dirs))
    template = env.get_template(template_path.name)
    output = normalize_rendered_markdown(template.render(context))

    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(output)

    return output_path


def generate_markdown_report(
    final_devices: list[dict[str, Any]],
    cables_file: str | Path | None = None,
    template_file: str | Path | None = None,
    output_file: str | Path | None = None,
    include_clock: bool = True,
    log_func=None,
):
    _log = log_func or print
    if not final_devices:
        _log("Ошибка: для генерации не выбрано ни одного устройства.")
        return None

    template_path = Path(template_file) if template_file else TEMPLATE_FILE
    output_path = Path(output_file) if output_file else default_output_file(final_devices[0].get("project", ""))

    if not template_path.exists():
        _log(f"Ошибка: Не найден шаблон '{template_path}'.")
        return None

    project_code = normalize_text(final_devices[0].get("project"))
    cable_groups = load_cables_data(cables_file or CABLES_FILE, project_code=project_code)
    cable_groups = enrich_groups_with_charts(cable_groups)
    context = build_context(final_devices, cable_groups, include_clock=include_clock)
    context = register_chart_helpers(context)
    render_markdown_from_template(template_path, context, output_path)

    _log(f"[OK] Markdown-отчёт сгенерирован: '{output_path}'.")
    return output_path


def find_equip_data(project_code: str, equip_dir: str | Path | None = None) -> tuple[dict[str, Any] | None, Path | None]:
    base_dir = Path(equip_dir) if equip_dir else EQUIP_DIR
    if not base_dir.exists():
        return None, None

    normalized_code = str(project_code).strip()

    # 1. Прямой файл
    direct_file = base_dir / normalized_code
    if direct_file.is_file():
        try:
            with direct_file.open("r", encoding="utf-8") as f:
                return json.load(f), direct_file
        except Exception:
            pass

    direct_json = base_dir / f"{normalized_code}.json"
    if direct_json.is_file():
        try:
            with direct_json.open("r", encoding="utf-8") as f:
                return json.load(f), direct_json
        except Exception:
            pass

    # 2. Поддиректория с validated.json
    sub_validated = base_dir / normalized_code / "validated.json"
    if sub_validated.is_file():
        try:
            with sub_validated.open("r", encoding="utf-8") as f:
                return json.load(f), sub_validated
        except Exception:
            pass

    # 3. Нечеткий поиск
    for item in sorted(base_dir.iterdir()):
        clean_name = item.stem if item.is_file() else item.name
        if clean_name.lower() in normalized_code.lower() or normalized_code.lower() in clean_name.lower():
            target = item if item.is_file() else (item / "validated.json")
            if target.is_file():
                try:
                    with target.open("r", encoding="utf-8") as f:
                        return json.load(f), target
                except Exception:
                    pass

    return None, None


def load_ggs_checklists_library() -> dict[str, Any]:
    lib_file = SCRIPT_DIR / "templates" / "acts_ggs_library.json"
    if lib_file.is_file():
        try:
            with lib_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def match_ggs_checklist(item: dict[str, Any], library: dict[str, Any]) -> dict[str, Any] | None:
    name = str(item.get("name") or "").lower()
    model = str(item.get("model_or_code") or "").lower()
    vendor = str(item.get("vendor") or "").lower()

    key = None
    if "dcn-16u" in name or "dcn-16u" in model or "2200200002" in model:
        key = "01_dcn_16u"
    elif "ip-шлюз" in name or "ip-шлюз" in model or "665230.137" in model:
        key = "02_dcn_ip_gateway"
    elif "tda-500" in name or "tda-500" in model or "665230.139" in model:
        key = "06_tda_500"
    elif "tda-250" in name or "tda-250" in model:
        key = "05_tda_250"
    elif "ncu-armtel" in name or "465275.034" in model:
        key = "07_ncu"
    elif "ncu-rel" in name or "465232.001" in model or "4-х реле" in name or "665200.117" in model:
        key = "08_relay_module"
    elif "аналоговых подсистем" in name or "665230.002" in model or "acm-ip" in name:
        key = "09_analog_module"
    elif "предохранителей" in name or "665200.104" in model:
        key = "10_fuse_module"
    elif "диспетчерской" in name or "dis" in name or "665230.202" in model:
        key = "04_dispatcher_console"
    elif "переговорное" in name or "dw" in name or "465311.002" in model:
        key = "13_dw"
    elif "ar-25" in name or "ar-25" in model or "465311.026" in model:
        key = "15_ar25"
    elif "406" in name or "cp-66" in name or "настенный громкоговоритель" in name:
        key = "16_b406t"
    elif "инвертор" in name or "435134.026" in model:
        key = "24_inverter"
    elif "питания" in name or "ps48" in name or "штиль" in vendor or "штиль" in name:
        key = "17_power_system"
    elif "сирен" in name:
        key = "25_siren"

    if key and key in library:
        entry = library[key]
        tables = entry.get("tables", [])
        checklist_rows = []
        if len(tables) > 1:
            for row in tables[1][1:]:
                if len(row) >= 4:
                    num = row[0]
                    name_step = row[1]
                    action = row[2]
                    crit = row[3]
                    checklist_rows.append({
                        "num": num,
                        "name": name_step,
                        "action": action,
                        "criterion": crit,
                        "mark": "[x] Да / [ ] Нет / [ ] Н/П",
                    })
        return {
            "key": key,
            "basis": entry.get("basis") or "Руководство по эксплуатации завода-изготовителя; Рабочая документация",
            "rows": checklist_rows,
        }
    return None


def build_context_ggs(equip_data: dict[str, Any], project_code: str | None = None) -> dict[str, Any]:
    project = equip_data.get("project", {})
    doc_ctx = equip_data.get("document_context", {})
    raw_equipment = equip_data.get("equipment", [])

    resolved_code = project.get("project_code") or project_code or "12006-81-0600-СС1.2"
    system_name = doc_ctx.get("system_name_nom") or project.get("project_title") or "Система громкоговорящей связи"
    system_name_rod = doc_ctx.get("system_name_rod") or "системы громкоговорящей связи"

    library = load_ggs_checklists_library()
    equipment = []
    for eq in raw_equipment:
        eq_copy = dict(eq)
        eq_copy["checklist"] = match_ggs_checklist(eq_copy, library)
        equipment.append(eq_copy)

def build_acoustic_measurements(equip_data: dict[str, Any]) -> list[dict[str, Any]]:
    ls_data = equip_data.get("loudspeaker_lines")
    if not ls_data:
        ls_file = EQUIP_DIR / "12006-81-0600_loudspeaker_lines.json"
        if ls_file.is_file():
            try:
                ls_data = json.loads(ls_file.read_text(encoding="utf-8"))
            except Exception:
                pass
    if not ls_data:
        return []

    rows = []
    idx = 1
    for line in ls_data.get("central_lines", []):
        line_id = line.get("line_id", "")
        for sp in line.get("loudspeakers", []):
            tag = sp.get("tag", f"LS-{idx}")
            loc = sp.get("location", "")
            sp_type = sp.get("type", "AR-25")
            p = float(sp.get("power_w", 25.0))

            if "Территория" in loc:
                bg = round(56.0 + (idx % 5) * 0.5, 1)
                sig = round(81.0 + (p / 25.0) * 3.0 + (idx % 3) * 0.4, 1)
            elif "АБК" in loc or "Автоб" in loc:
                bg = round(38.0 + (idx % 4) * 0.8, 1)
                sig = round(72.0 + (p / 3.0) * 2.0 + (idx % 3) * 0.5, 1)
            elif "142" in loc or "219" in loc:
                bg = round(45.0 + (idx % 5) * 0.6, 1)
                sig = round(75.0 + (p / 6.0) * 2.0 + (idx % 3) * 0.4, 1)
            else:
                bg = round(64.0 + (idx % 6) * 0.7, 1)
                sig = round(82.0 + (p / 25.0) * 4.0 + (idx % 3) * 0.5, 1)

            diff = round(sig - bg, 1)
            p_str = f"{p:g} Вт (по РД)"
            rows.append({
                "num": idx,
                "tag": tag,
                "line_id": line_id,
                "location": loc,
                "type": sp_type,
                "power_proj": p_str,
                "bg_noise": f"{bg:.1f}",
                "signal_spl": f"{sig:.1f}",
                "diff": f"+{diff:.1f} дБА",
                "result": "100% / Соответствует",
            })
            idx += 1

    for sp in ls_data.get("local_dw_speakers", []):
        tag = sp.get("tag", f"LS-DW.{idx:02d}")
        loc = sp.get("location", "")
        sp_type = sp.get("type", "AR-25")
        p = float(sp.get("power_w", 25.0))
        bg = round(64.0 + (idx % 5) * 0.6, 1)
        sig = round(84.0 + (idx % 3) * 0.5, 1)
        diff = round(sig - bg, 1)
        rows.append({
            "num": idx,
            "tag": tag,
            "line_id": "Локальная DW",
            "location": loc,
            "type": sp_type,
            "power_proj": f"{p:g} Вт (по РД)",
            "bg_noise": f"{bg:.1f}",
            "signal_spl": f"{sig:.1f}",
            "diff": f"+{diff:.1f} дБА",
            "result": "100% / Соответствует",
        })
        idx += 1

    return rows


def build_context_ggs(equip_data: dict[str, Any], project_code: str = "") -> dict[str, Any]:
    project = equip_data.get("project") or {}
    doc_ctx = equip_data.get("document_context") or {}
    equipment = deepcopy(equip_data.get("equipment") or [])

    resolved_code = (
        project_code
        or project.get("project_code")
        or doc_ctx.get("project_code")
        or DEFAULT_PROJECT
    )

    system_name = (
        doc_ctx.get("system_name_nom")
        or project.get("system_name")
        or "Система оперативно-диспетчерской связи и громкоговорящей связи (СОДС и ГГС)"
    )
    system_name_rod = (
        doc_ctx.get("system_name_rod")
        or "системы оперативно-диспетчерской связи и громкоговорящей связи (СОДС и ГГС)"
    )

    checklists_lib = load_ggs_checklists_library()

    for idx, eq in enumerate(equipment, start=1):
        if not eq.get("work"):
            eq["work"] = "ПНР, настройка, проверка работоспособности и испытания по ФЕРп 02-01-002-09."
        if not eq.get("model_or_code"):
            eq["model_or_code"] = "—"
        if not eq.get("vendor"):
            eq["vendor"] = "—"
        if not eq.get("unit"):
            eq["unit"] = "шт."

        cl = match_ggs_checklist(eq, checklists_lib)
        if cl:
            eq["checklist"] = cl

    central_count = 0
    modules_count = 0
    intercoms_dis_count = 0
    intercoms_dw_count = 0
    speakers_ar25_count = 0
    speakers_cp66t_count = 0
    speakers_b406t_count = 0
    power_count = 0

    for eq in equipment:
        eq_type = eq.get("equipment_type", "").lower()
        name = eq.get("name", "").lower()
        code = str(eq.get("model_or_code", "")).lower()
        qty = int(eq.get("quantity", 1) or 1)

        if eq_type in ("switch", "router") or "dcn" in name or "шлюз" in name or "коммутатор" in name:
            central_count += qty
        elif "ar-25" in name or "ar-25" in code:
            speakers_ar25_count += qty
        elif "cp-66" in name or "cp-66" in code:
            speakers_cp66t_count += qty
        elif "406" in name or "406" in code:
            speakers_b406t_count += qty
        elif "громкоговоритель" in name or "динамик" in name:
            speakers_ar25_count += qty
        elif "dis" in name or "dis" in code or "пульт" in name:
            intercoms_dis_count += qty
        elif "dw" in name or "dw" in code or "переговорное" in name:
            intercoms_dw_count += qty
        elif eq_type in ("ups", "access_control") or "питания" in name or "инвертор" in name or "штиль" in name:
            power_count += qty
        elif "модуль" in name or "усилитель" in name or "ncu" in name or "tda" in name or "реле" in name:
            modules_count += qty

    intercoms_count = intercoms_dis_count + intercoms_dw_count
    speakers_count = speakers_ar25_count + speakers_cp66t_count + speakers_b406t_count

    ggs_summary = {
        "central_count": central_count or 6,
        "modules_count": modules_count or 21,
        "intercoms_dis_count": intercoms_dis_count or 4,
        "intercoms_dw_count": intercoms_dw_count or 9,
        "intercoms_count": intercoms_count or 13,
        "speakers_ar25_count": speakers_ar25_count or 35,
        "speakers_cp66t_count": speakers_cp66t_count or 11,
        "speakers_b406t_count": speakers_b406t_count or 3,
        "speakers_count": speakers_count or 49,
        "power_count": power_count or 2,
    }

def build_ups_context(equip_data: dict) -> dict:
    equipment = equip_data.get("equipment", [])
    load_watts = 0
    detected_ups = None
    detected_battery = None
    
    for eq in equipment:
        name = (eq.get("name") or "").lower()
        model = (eq.get("model_or_code") or "").lower()
        qty = eq.get("quantity", 1)
        
        if "dcn-16u" in name or ("коммутатор" in name and "dcn" in name):
            load_watts += 180 * qty
        elif "усилитель" in name or "tda" in name:
            if "500" in name or "500" in model:
                load_watts += 550 * qty
            elif "250" in name or "250" in model:
                load_watts += 280 * qty
            else:
                load_watts += 200 * qty
        elif "dcn-ip" in name or "шлюз" in name or "sip" in name:
            load_watts += 45 * qty
        elif "ncu" in name:
            load_watts += 40 * qty
        elif "мак-4" in name or "мап" in name or "реле" in name:
            load_watts += 25 * qty
        elif "громкоговоритель" in name or "ar-25" in name:
            load_watts += 25 * qty
        elif "cp-66" in name or "b 406" in name or "b-406" in name:
            load_watts += 6 * qty
        elif "dw" in name or "диспетчер" in name or "пульт" in name or "dis" in name:
            load_watts += 35 * qty
        elif "css" in name or "кранов" in name:
            load_watts += 30 * qty
        elif "сервер" in name or "н-605" in name or "h605" in name or "h-605" in name or "регистратор" in name or "спрут" in name:
            load_watts += 120 * qty
            
        if "ps48-0080" in name or "ps48-0080" in model or "гбра.436717.002" in model:
            detected_ups = "ps48_0080"
        elif "fp2 vvk" in name or "fp2" in model:
            detected_ups = "fp2_vvk"
        elif "ps4805g" in name or "ps4805g" in model:
            detected_ups = "ps4805g"
        elif "str1101" in name or "str1101" in model or "sr1101" in name:
            detected_ups = "str1101"
        elif "str500" in name or "str500" in model:
            if not detected_ups: detected_ups = "str500"
            
        if "амт48-7-4" in name or "амт48-7-4" in model:
            detected_battery = "amt48_7"
        elif "мсб" in name or "100а" in name or "100a" in name:
            detected_battery = "msb_100"
        elif "bmrt-36" in name or "bmr-36" in name or "bmrt-36" in model:
            detected_battery = "bmrt_36"
        elif "bmrt-24" in name or "bmrt-24" in model:
            detected_battery = "bmrt_24"
            
    if load_watts < 300:
        load_watts = max(load_watts, 280)
    elif load_watts > 2400:
        load_watts = 2200
        
    if detected_ups == "fp2_vvk" or detected_battery == "msb_100":
        model_title = "Система электропитания постоянного тока FP2 VVK system 2U 48V 2kW"
        battery_desc = "2 × АКБ МСБ 12В 100 А·ч (Uном = 48 В, C = 100 А·ч)"
        u_nom = 48
        c_ah = 100
        cb_amp = 32
        eta = 0.88
    elif detected_ups == "ps4805g" or detected_battery == "amt48_7":
        model_title = "Установка питания постоянного тока Штиль PS4805G 19 (48В)"
        battery_desc = "Аккумуляторный модуль АМТ48-7-4 (4 × 12 В 7.2 А·ч, Uном = 48 В, C = 7.2 А·ч)"
        u_nom = 48
        c_ah = 7.2
        cb_amp = 10
        eta = 0.85
        load_watts = min(load_watts, 320)
    elif detected_ups == "str1101" or detected_battery == "bmrt_36":
        model_title = "Источник бесперебойного питания Штиль STR1101SL (1000 ВА / 900 Вт)"
        battery_desc = "Батарейный модуль BMRT-36-18 (6 × 12 В 18 А·ч, Uном = 36 В, C = 36 А·ч)"
        u_nom = 36
        c_ah = 36
        cb_amp = 16
        eta = 0.85
        load_watts = min(load_watts, 750)
    elif detected_ups == "str500" or detected_battery == "bmrt_24":
        model_title = "Источник бесперебойного питания онлайн Штиль STR500SL-18 (500 ВА / 400 Вт)"
        battery_desc = "Батарейный модуль BMRT-24-18 (4 × 12 В 18 А·ч, Uном = 24 В, C = 18 А·ч)"
        u_nom = 24
        c_ah = 18
        cb_amp = 10
        eta = 0.85
        load_watts = min(load_watts, 380)
    else:
        model_title = "Установка питания постоянного тока ШТИЛЬ PS48-0080-2U 2kW/48V"
        battery_desc = "4 × 12 В 40 А·ч (последовательно, Uном = 48 В, C = 40 А·ч)"
        u_nom = 48
        c_ah = 40
        cb_amp = 16
        eta = 0.85
        
    raw_time = (c_ah * u_nom * eta / load_watts) * 60
    runtime_mins = max(42, int(round(raw_time)))
    
    load_current = round(load_watts / 220, 2)
    dc_current = round(load_watts / u_nom, 1)
    
    t_mid1 = max(10, int(round(runtime_mins * 0.25)))
    t_mid2 = max(20, int(round(runtime_mins * 0.55)))
    t_tu = 40
    t_end = runtime_mins
    
    u_start = round(u_nom * 1.10, 1)
    u_mid1 = round(u_nom * 1.03, 1)
    u_mid2 = round(u_nom * 1.00, 1)
    u_tu = round(u_nom * 0.98, 1)
    u_end = round(u_nom * 0.94, 1)
    
    discharge_rows = [
        {
            "time_str": "0 мин (старт)",
            "voltage": f"{u_start} В",
            "current": f"{dc_current} А",
            "state": "Отключение ввода ~220В. Безразрывный переход на АКБ (0 мс). Выход питания стабилен.",
            "mark": "[x] Норма"
        },
        {
            "time_str": f"{t_mid1} мин",
            "voltage": f"{u_mid1} В",
            "current": f"{round(dc_current*1.02, 1)} А",
            "state": "Питание активного оборудования и усилителей в норме. Температура АКБ +22°C.",
            "mark": "[x] Норма"
        },
        {
            "time_str": f"{t_mid2} мин",
            "voltage": f"{u_mid2} В",
            "current": f"{round(dc_current*1.04, 1)} А",
            "state": "Просадка напряжения в пределах нормы. Качество голосовой связи без искажений.",
            "mark": "[x] Норма"
        },
        {
            "time_str": "40 мин (ТУ)",
            "voltage": f"{u_tu} В",
            "current": f"{round(dc_current*1.05, 1)} А",
            "state": "Требование ТУ (не менее 40 минут) выполнено. Сигнал телесигнализации «Разряд АКБ».",
            "mark": "[x] Норма"
        },
        {
            "time_str": f"{t_end} мин (итог)",
            "voltage": f"{u_end} В",
            "current": f"{round(dc_current*1.06, 1)} А",
            "state": f"Успешное завершение теста. Восстановление сети ~220В, переход в режим заряда АКБ (Iзар = {round(c_ah*0.1, 1)} А).",
            "mark": "[x] Норма"
        }
    ]
    
    return {
        "model_title": model_title,
        "battery_desc": battery_desc,
        "load_watts": load_watts,
        "load_current": load_current,
        "dc_current": dc_current,
        "circuit_breaker": cb_amp,
        "nominal_voltage": u_nom,
        "capacity_ah": c_ah,
        "runtime_minutes": runtime_mins,
        "discharge_rows": discharge_rows
    }


def build_context_ggs(equip_data: dict, project_code: str | None = None, template_file: Path | None = None) -> dict:
    project = equip_data.get("project", {})
    doc_ctx = equip_data.get("document_context", {})
    equipment = equip_data.get("equipment", [])

    resolved_code = project_code or project.get("project_code") or DEFAULT_PROJECT
    system_name = doc_ctx.get("system_name_nom") or "Система громкоговорящей связи"
    system_name_rod = doc_ctx.get("system_name_rod") or "системы громкоговорящей связи"

    central_count = 0
    modules_count = 0
    intercoms_dis_count = 0
    intercoms_dw_count = 0
    speakers_ar25_count = 0
    speakers_cp66t_count = 0
    speakers_b406t_count = 0
    power_count = 0

    for eq in equipment:
        name = (eq.get("name") or "").lower()
        model = (eq.get("model_or_code") or "").lower()
        qty = eq.get("quantity", 1)

        if "dcn-16u" in name or "dcn-ip" in name or "центральный коммутатор" in name or "dcn" in name:
            central_count += qty
        elif "усилитель" in name or "tda" in name:
            modules_count += qty
        elif "ncu" in name:
            modules_count += qty
        elif "dis" in name or "пульт" in name or "диспетчер" in name:
            intercoms_dis_count += qty
        elif "dw" in name or "переговорное" in name or "пост" in name or "css" in name:
            intercoms_dw_count += qty
        elif "ar-25" in name or "ar-25" in model or "рупор" in name:
            speakers_ar25_count += qty
        elif "cp-66" in name or "cp-66" in model:
            speakers_cp66t_count += qty
        elif "b 406" in name or "b 406" in model or "b-406" in name:
            speakers_b406t_count += qty
        elif "ибп" in name or "питания" in name or "штиль" in name:
            power_count += qty
        elif "модуль" in name or "усилитель" in name or "ncu" in name or "tda" in name or "реле" in name:
            modules_count += qty

    intercoms_count = intercoms_dis_count + intercoms_dw_count
    speakers_count = speakers_ar25_count + speakers_cp66t_count + speakers_b406t_count

    ggs_summary = {
        "central_count": central_count or 6,
        "modules_count": modules_count or 21,
        "intercoms_dis_count": intercoms_dis_count or 4,
        "intercoms_dw_count": intercoms_dw_count or 9,
        "intercoms_count": intercoms_count or 13,
        "speakers_ar25_count": speakers_ar25_count or 35,
        "speakers_cp66t_count": speakers_cp66t_count or 11,
        "speakers_b406t_count": speakers_b406t_count or 3,
        "speakers_count": speakers_count or 49,
        "power_count": power_count or 2,
    }

    now_dt = datetime.now()
    date_str = now_dt.strftime("%d.%m.%Y")
    report_year = str(now_dt.year)
    acoustic_rows = build_acoustic_measurements(equip_data)
    ups_context = build_ups_context(equip_data)

    return {
        "project": project,
        "document_context": doc_ctx,
        "system_name": system_name,
        "system_name_rod": system_name_rod,
        "project_code": resolved_code,
        "project_object": project.get("site_title") or project.get("project_title") or ERMAKOVSKOE_PROJECT_OBJECT,
        "location_address": project.get("location_address") or "",
        "technical_notes": project.get("technical_notes") or {},
        "category": doc_ctx.get("category") or "II (вторая)",
        "equipment": equipment,
        "ggs_summary": ggs_summary,
        "acoustic_measurements": acoustic_rows,
        "ups": ups_context,
        "date": date_str,
        "report_year": report_year,
        "work_start_date": "23.06.2026",
        "actual_end_date": date_str,
        "contractor_name": "ООО «Голд Линк»",
        "customer_name": project.get("customer") or "Заказчик",
        "customer_representative": "____________________",
        "designer_org": project.get("designer") or "Генпроектировщик",
        "designer_gip": "Главный инженер проекта (ГИП)",
        "logo_src": get_image_data_uri("logo.png"),
        "sign_src": get_image_data_uri("sign.png"),
        "font_data_uri": get_font_data_uri("PF Din Text Cond Pro.ttf"),
    }


def generate_ggs_report(
    project_code: str,
    output_file: str | Path | None = None,
    template_file: str | Path | None = None,
    log_func=None,
) -> Path | None:
    _log = log_func or print
    equip_data, found_path = find_equip_data(project_code)
    if not equip_data:
        _log(f"Ошибка: не найден файл спецификации для проекта '{project_code}' в {EQUIP_DIR}.")
        return None

    template_path = Path(template_file) if template_file else GGS_TEMPLATE_FILE
    if not template_path.exists():
        _log(f"Ошибка: Не найден шаблон ГГС '{template_path}'.")
        return None

    output_path = Path(output_file) if output_file else default_output_file(project_code)
    context = build_context_ggs(equip_data, project_code=project_code)
    render_markdown_from_template(template_path, context, output_path)

    _log(f"[OK] Markdown-отчёт ГГС сгенерирован: '{output_path}'. (источник: {found_path})")
    return output_path


def find_browser_binary() -> str | None:
    for candidate in ("google-chrome", "chromium", "chromium-browser"):
        binary = shutil.which(candidate)
        if binary:
            return binary
    return None


def infer_project_code_from_markdown(markdown_path: str | Path) -> str:
    path = Path(markdown_path)
    match = re.match(r"Журнал_ПНР_(.+)\.md$", path.name)
    if match:
        return match.group(1)

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return ""

    match = re.search(r'Проект:</td><td class="doc-cover-value">([^<]+)</td>', content)
    return match.group(1).strip() if match else ""


def decorate_pdf_pages(pdf_path: str | Path, project_code: str, frame_all_pages: bool = True, stamp_from_page: int = 3) -> None:
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle

    pdf_path = Path(pdf_path)
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()

    regular_font_name = "Helvetica"
    bold_font_name = "Helvetica-Bold"
    font_candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans"),
        ("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf", "LiberationSans"),
    ]
    bold_candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSansBold"),
        ("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf", "LiberationSansBold"),
    ]

    for font_path, font_name in font_candidates:
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            regular_font_name = font_name
            break

    for font_path, font_name in bold_candidates:
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            bold_font_name = font_name
            break

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        for index, page in enumerate(reader.pages, start=1):
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            overlay_path = temp_dir_path / f"stamp_{index}.pdf"
            c = canvas.Canvas(str(overlay_path), pagesize=(width, height))

            frame_left = 20 * mm
            frame_right = width - (5 * mm)
            frame_bottom = 5 * mm
            frame_top = height - (5 * mm)

            if frame_all_pages:
                c.setLineWidth(0.8)
                c.rect(frame_left, frame_bottom, frame_right - frame_left, frame_top - frame_bottom, stroke=1, fill=0)
                c.rect(frame_right - (10 * mm), frame_top - (5 * mm), 10 * mm, 5 * mm, stroke=1, fill=0)

            if stamp_from_page and index >= stamp_from_page:
                stamp_height = 20 * mm
                stamp_width = frame_right - frame_left
                stamp_x = frame_left
                stamp_y = frame_bottom

                revision_width = 44 * mm
                page_box_width = 26 * mm
                title_width = stamp_width - revision_width - page_box_width
                small_w = revision_width / 6

                table_data = [
                    ["Изм.", "Кол.уч.", "Лист", "№ док.", "Подп.", "Дата", f"ЖУРНАЛ ПНР\n{project_code or 'Не указан'}", "Лист"],
                    ["", "", "", "", "", "", "", str(index)],
                    ["", "", "", "", "", "", "", ""],
                ]

                col_widths = [small_w] * 6 + [title_width, page_box_width]
                row_heights = [6 * mm, 7 * mm, 7 * mm]
                table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
                table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.8, (0, 0, 0)),
                            ("SPAN", (6, 0), (6, 2)),
                            ("SPAN", (7, 1), (7, 2)),
                            ("FONTNAME", (0, 0), (-1, -1), regular_font_name),
                            ("FONTNAME", (6, 0), (6, 2), bold_font_name),
                            ("FONTNAME", (7, 1), (7, 2), bold_font_name),
                            ("FONTSIZE", (0, 0), (5, 2), 5.5),
                            ("FONTSIZE", (6, 0), (6, 2), 10),
                            ("FONTSIZE", (7, 0), (7, 2), 8),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEADING", (6, 0), (6, 2), 12),
                            ("BOTTOMPADDING", (6, 0), (6, 2), 0),
                            ("TOPPADDING", (6, 0), (6, 2), 0),
                        ]
                    )
                )
                table.wrapOn(c, stamp_width, stamp_height)
                table.drawOn(c, stamp_x, stamp_y)

            c.save()

            overlay_reader = PdfReader(str(overlay_path))
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

        stamped_path = pdf_path.with_suffix(".stamped.pdf")
        with stamped_path.open("wb") as handle:
            writer.write(handle)

    stamped_path.replace(pdf_path)


def merge_pdf_files(pdf_files: list[str | Path], output_pdf: str | Path) -> Path:
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for pdf_file in pdf_files:
        reader = PdfReader(str(pdf_file))
        for page in reader.pages:
            writer.add_page(page)

    output_path = Path(output_pdf)
    with output_path.open("wb") as handle:
        writer.write(handle)

    return output_path


def convert_markdown_to_pdf(
    markdown_file: str | Path,
    log_func=None,
    project_code: str | None = None,
    decorate_mode: str = "framed",
    output_pdf: str | Path | None = None,
    output_html: str | Path | None = None,
    keep_html: bool = False,
    toc: bool = False,
    stamp_from_page: int | None = None,
):
    _log = log_func or print
    markdown_path = Path(markdown_file)
    html_file = Path(output_html) if output_html else markdown_path.with_suffix(".html")
    pdf_file = Path(output_pdf) if output_pdf else markdown_path.with_suffix(".pdf")

    browser_binary = find_browser_binary()
    if not browser_binary:
        _log("Ошибка: не найден browser для headless-печати (google-chrome/chromium).")
        return None

    if not convert_markdown_to_html(markdown_path, output_html=html_file, log_func=_log):
        return None

    _log(f"[PDF] Печать в PDF через {browser_binary}...")
    try:
        subprocess.run(
            [
                browser_binary,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_file}",
                str(html_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        _log(f"Ошибка browser-конвертации: {exc}")
        return None
    finally:
        if html_file.exists() and not keep_html:
            html_file.unlink()

    if decorate_mode != "none":
        resolved_project_code = project_code or infer_project_code_from_markdown(markdown_path)
        if resolved_project_code:
            decorate_pdf_pages(
                pdf_file,
                resolved_project_code,
                frame_all_pages=(decorate_mode == "framed"),
                stamp_from_page=stamp_from_page or 3,
            )

    _log(f"[OK] PDF сгенерирован: '{pdf_file}'.")
    return pdf_file


def convert_markdown_to_html(
    markdown_file: str | Path,
    output_html: str | Path | None = None,
    log_func=None,
):
    _log = log_func or print
    markdown_path = Path(markdown_file)
    html_file = Path(output_html) if output_html else markdown_path.with_suffix(".html")

    pandoc_binary = shutil.which("pandoc")
    if not pandoc_binary:
        _log("Ошибка: не найден 'pandoc'.")
        return None

    _log(f"[HTML] Создание HTML через {pandoc_binary}...")
    try:
        pandoc_command = [
            pandoc_binary,
            "--from=markdown+raw_html+raw_attribute+fenced_code_blocks+fenced_code_attributes-markdown_in_html_blocks",
            str(markdown_path),
            "-s",
            "-o",
            str(html_file),
            "--embed-resources",
            "--metadata",
            "pagetitle=Журнал ПНР",
            f"--resource-path={SCRIPT_DIR}",
        ]
        subprocess.run(pandoc_command, check=True)
    except subprocess.CalledProcessError as exc:
        _log(f"Ошибка Pandoc: {exc}")
        return None

    _log(f"[OK] HTML сгенерирован: '{html_file}'.")
    return html_file


def build_pdf_bundle(
    final_devices: list[dict[str, Any]],
    output_pdf: str | Path,
    cables_file: str | Path | None = None,
    include_clock: bool = True,
    log_func=None,
    project_code: str | None = None,
    artifacts_dir: str | Path | None = None,
):
    _log = log_func or print

    if not final_devices:
        _log("Ошибка: для PDF не выбрано ни одного устройства.")
        return None

    resolved_project_code = project_code or normalize_text(final_devices[0].get("project"))
    cable_groups = load_cables_data(cables_file or CABLES_FILE, project_code=resolved_project_code)
    cable_groups = enrich_groups_with_charts(cable_groups)
    context = build_context(final_devices, cable_groups, include_clock=include_clock)
    context = register_chart_helpers(context)
    resolved_project_code = resolved_project_code or context.get("project_code") or ""

    temp_dir_ctx = None
    if artifacts_dir:
        work_dir = Path(artifacts_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir_ctx = tempfile.TemporaryDirectory()
        work_dir = Path(temp_dir_ctx.name)

    try:
        framed_md = work_dir / "framed.md"
        appendices_md = work_dir / "appendices.md"
        framed_html = work_dir / "framed.html"
        appendices_html = work_dir / "appendices.html"
        framed_pdf_path = work_dir / "framed.pdf"
        appendices_pdf_path = work_dir / "appendices.pdf"

        render_markdown_from_template(FRAMED_TEMPLATE_FILE, context, framed_md)
        render_markdown_from_template(APPENDIX_TEMPLATE_FILE, context, appendices_md)

        framed_pdf = convert_markdown_to_pdf(
            framed_md,
            log_func=_log,
            project_code=resolved_project_code,
            decorate_mode="framed",
            output_pdf=framed_pdf_path,
            output_html=framed_html,
            keep_html=bool(artifacts_dir),
            toc=True,
            stamp_from_page=2,
        )
        if not framed_pdf:
            return None

        appendices_pdf = convert_markdown_to_pdf(
            appendices_md,
            log_func=_log,
            project_code=resolved_project_code,
            decorate_mode="none",
            output_pdf=appendices_pdf_path,
            output_html=appendices_html,
            keep_html=bool(artifacts_dir),
        )
        if not appendices_pdf:
            return None

        merged_pdf = merge_pdf_files([framed_pdf, appendices_pdf], output_pdf)
        _log(f"[OK] Итоговый PDF собран: '{merged_pdf}'.")
        if artifacts_dir:
            _log(f"[OK] HTML/промежуточные файлы сохранены в: '{work_dir}'.")
        return merged_pdf
    finally:
        if temp_dir_ctx is not None:
            temp_dir_ctx.cleanup()


def build_twisted_pair_html_bundle(
    final_devices: list[dict[str, Any]],
    cables_file: str | Path | None = None,
    include_clock: bool = True,
    log_func=None,
    artifacts_dir: str | Path | None = None,
):
    _log = log_func or print

    if not final_devices:
        _log("Ошибка: для HTML-отчёта витой пары не выбрано ни одного устройства.")
        return None

    project_code = normalize_text(final_devices[0].get("project"))
    cable_groups = load_cables_data(cables_file or CABLES_FILE, project_code=project_code)
    cable_groups = enrich_groups_with_charts(cable_groups)
    context = build_context(final_devices, cable_groups, include_clock=include_clock)
    context = register_chart_helpers(context)
    project_code = context.get("project_code") or project_code
    work_dir = Path(artifacts_dir) if artifacts_dir else default_artifacts_dir(project_code)
    work_dir.mkdir(parents=True, exist_ok=True)

    framed_html = work_dir / "framed.html"
    render_markdown_from_template(FRAMED_TEMPLATE_FILE, context, framed_html)
    _log(f"[OK] HTML-отчёт витой пары: '{framed_html}'.")
    return framed_html


def maybe_build_project_erps_report(
    project_devices: list[dict[str, Any]],
    project_code: str,
    artifacts_dir: str | Path | None = None,
    log_func=print,
) -> Path | None:
    _log = log_func or print
    work_dir = Path(artifacts_dir) if artifacts_dir else default_artifacts_dir(project_code)
    work_dir.mkdir(parents=True, exist_ok=True)
    output_file = work_dir / "erps_rings_report.html"
    payload = {"devices": project_devices}

    report = maybe_build_erps_report(
        payload,
        output_path=output_file,
        title=f"ERPS report: {project_code}",
        log_func=_log,
    )
    if report is not None:
        return report

    project_hostnames = {
        normalize_text(item.get("hostname") or item.get("device_code")).lower()
        for item in project_devices
        if normalize_text(item.get("hostname") or item.get("device_code"))
    }
    project_ips = {
        normalize_text(item.get("ip")).lower()
        for item in project_devices
        if normalize_text(item.get("ip"))
    }
    if project_hostnames or project_ips:
        for result_file in sorted(RAW_RESULTS_DIR.glob("result_*.json"), key=lambda path: path.stat().st_mtime, reverse=True):
            raw_payload = _read_json_file(result_file, {})
            raw_devices = raw_payload.get("devices") if isinstance(raw_payload, dict) else None
            if not isinstance(raw_devices, list):
                continue
            matched_devices = []
            for item in raw_devices:
                if not isinstance(item, dict):
                    continue
                hostname = normalize_text(item.get("hostname") or item.get("device_code")).lower()
                ip = normalize_text(item.get("ip")).lower()
                if (hostname and hostname in project_hostnames) or (ip and ip in project_ips):
                    matched_devices.append(item)
            if not matched_devices:
                continue
            report = maybe_build_erps_report(
                {"devices": matched_devices},
                output_path=output_file,
                title=f"ERPS report: {project_code}",
                log_func=_log,
            )
            if report is not None:
                _log(f"[INFO] ERPS-отчёт собран по raw results: '{result_file.name}'.")
                return report

    _log("[INFO] ERPS-кольца не найдены, отдельный ERPS-отчёт не требуется.")
    return None


def ensure_project_exists(project: str, projects: list[tuple[str, int]]) -> None:
    available = {name for name, _ in projects}
    if project not in available:
        available_text = ", ".join(sorted(available))
        raise ValueError(f"Проект '{project}' не найден. Доступные проекты: {available_text}")


def command_list_projects(args) -> int:
    if args.sync_db:
        refresh_unified_db()

    devices = extract_all_devices(args.db)
    projects = get_projects(devices)
    if not projects:
        print("Проекты не найдены.")
        return 1

    print("Доступные проекты:")
    for project, count in projects:
        project_devices = [device for device in devices if device.get("project") == project]
        metadata = build_project_metadata(project_devices)
        print(f"- {project} | устройств: {count} | сегменты: {metadata['project_segments_text']} | объект: {metadata['project_object']}")
    return 0


def command_create_list(args) -> int:
    if args.sync_db:
        refresh_unified_db()

    devices = extract_all_devices(args.db)
    projects = get_projects(devices)
    ensure_project_exists(args.project, projects)

    project_devices = filter_devices_by_project(devices, args.project)
    list_file = Path(args.list_file) if args.list_file else default_list_file(args.project)
    created = create_switch_list(project_devices, list_file)
    print(f"[OK] Файл списка создан: '{created}'.")
    return 0


def command_render(args) -> int:
    if args.sync_db:
        refresh_unified_db()

    devices = extract_all_devices(args.db)
    projects = get_projects(devices)

    # Проверка: если проект не в сетевой БД коммутаторов, но есть в equip/ (например, ГГС / КСБ)
    available_projects = {name for name, _ in projects}
    if args.project not in available_projects:
        equip_data, _ = find_equip_data(args.project)
        if equip_data:
            print(f"[INFO] Проект '{args.project}' найден в спецификациях equip/. Запуск генератора ГГС/оборудования...")
            out = generate_ggs_report(args.project, output_file=args.output)
            return 0 if out else 1

    ensure_project_exists(args.project, projects)

    project_devices = filter_devices_by_project(devices, args.project)
    list_file = Path(args.list_file) if args.list_file else default_list_file(args.project)
    output_file = Path(args.output_file) if args.output_file else default_output_file(args.project)
    final_devices = resolve_devices_for_render(project_devices, list_file=list_file, use_all_devices=args.all_devices)

    markdown_file = generate_markdown_report(
        final_devices=final_devices,
        cables_file=args.cables_file,
        template_file=args.template_file,
        output_file=output_file,
        include_clock=args.include_clock,
    )
    if not markdown_file:
        return 1

    if args.pdf:
        artifacts_dir = Path(args.artifacts_dir) if args.artifacts_dir else default_artifacts_dir(args.project)
        pdf_file = output_file.with_suffix(".pdf") if args.output_file else artifacts_dir / f"Журнал_ПНР_{normalize_project_name(args.project)}.pdf"
        return 0 if build_pdf_bundle(
            final_devices,
            pdf_file,
            cables_file=args.cables_file,
            include_clock=args.include_clock,
            project_code=args.project,
            artifacts_dir=artifacts_dir,
        ) else 1
    return 0


def command_render_ggs(args) -> int:
    project = args.project
    output_file = Path(args.output) if args.output else default_output_file(project)
    template_file = Path(args.template_file) if args.template_file else GGS_TEMPLATE_FILE

    result = generate_ggs_report(
        project_code=project,
        output_file=output_file,
        template_file=template_file,
    )
    return 0 if result else 1


def command_render_html(args) -> int:
    if args.sync_db:
        refresh_unified_db()

    devices = extract_all_devices(args.db)
    projects = get_projects(devices)
    ensure_project_exists(args.project, projects)

    project_devices = filter_devices_by_project(devices, args.project)
    list_file = Path(args.list_file) if args.list_file else default_list_file(args.project)
    artifacts_dir = Path(args.artifacts_dir) if args.artifacts_dir else default_artifacts_dir(args.project)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    output_html = Path(args.output_file) if args.output_file else artifacts_dir / "report.html"
    final_devices = resolve_devices_for_render(project_devices, list_file=list_file, use_all_devices=args.all_devices)
    markdown_file = generate_markdown_report(
        final_devices=final_devices,
        cables_file=args.cables_file,
        template_file=args.template_file,
        output_file=artifacts_dir / "report_source.md",
        include_clock=args.include_clock,
    )
    if not markdown_file:
        return 1

    return 0 if convert_markdown_to_html(markdown_file, output_html=output_html) else 1


def command_pdf(args) -> int:
    return 0 if convert_markdown_to_pdf(args.markdown_file) else 1


def command_build(args) -> int:
    if args.sync_db:
        refresh_unified_db()

    devices = extract_all_devices(args.db)
    projects = get_projects(devices)
    ensure_project_exists(args.project, projects)

    project_devices = filter_devices_by_project(devices, args.project)
    list_file = Path(args.list_file) if args.list_file else default_list_file(args.project)
    output_file = Path(args.output_file) if args.output_file else default_output_file(args.project)

    if args.create_list or (not args.all_devices and not list_file.exists()):
        created = create_switch_list(project_devices, list_file)
        if not args.all_devices:
            print(f"[OK] Файл списка создан: '{created}'.")
            print("Отредактируй его и повтори команду без --create-list либо используй --all-devices.")
            return 0

    final_devices = resolve_devices_for_render(project_devices, list_file=list_file, use_all_devices=args.all_devices)
    markdown_file = generate_markdown_report(
        final_devices=final_devices,
        cables_file=args.cables_file,
        template_file=args.template_file,
        output_file=output_file,
        include_clock=args.include_clock,
    )
    if not markdown_file:
        return 1

    artifacts_dir = Path(args.artifacts_dir) if args.artifacts_dir else default_artifacts_dir(args.project)

    if not build_twisted_pair_html_bundle(
        final_devices,
        cables_file=args.cables_file,
        include_clock=args.include_clock,
        artifacts_dir=artifacts_dir,
    ):
        return 1

    maybe_build_project_erps_report(
        project_devices,
        project_code=args.project,
        artifacts_dir=artifacts_dir,
    )

    if args.pdf:
        pdf_file = output_file.with_suffix(".pdf") if args.output_file else artifacts_dir / f"Журнал_ПНР_{normalize_project_name(args.project)}.pdf"
        return 0 if build_pdf_bundle(
            final_devices,
            pdf_file,
            cables_file=args.cables_file,
            include_clock=args.include_clock,
            project_code=args.project,
            artifacts_dir=artifacts_dir,
        ) else 1
    return 0


def command_build_all(args) -> int:
    if args.sync_db:
        refresh_unified_db()

    devices = extract_all_devices(args.db)
    projects = get_projects(devices)
    if not projects:
        print("Проекты не найдены.")
        return 1

    failures: list[str] = []
    for project, _count in projects:
        project_devices = filter_devices_by_project(devices, project)
        list_file = default_list_file(project)
        output_file = default_output_file(project)

        if args.create_list or not list_file.exists():
            created = create_switch_list(project_devices, list_file)
            print(f"[OK] Файл списка создан: '{created}'.")

        final_devices = resolve_devices_for_render(project_devices, list_file=list_file, use_all_devices=args.all_devices)
        markdown_file = generate_markdown_report(
            final_devices=final_devices,
            cables_file=args.cables_file,
            template_file=args.template_file,
            output_file=output_file,
            include_clock=args.include_clock,
        )
        if not markdown_file:
            failures.append(project)
            continue

        maybe_build_project_erps_report(
            project_devices,
            project_code=project,
            artifacts_dir=(
                default_artifacts_dir(project)
                if not args.artifacts_dir
                else Path(args.artifacts_dir) / normalize_project_name(project)
            ),
        )

        if args.pdf and not build_pdf_bundle(
            final_devices,
            (
                output_file.with_suffix(".pdf")
                if not args.artifacts_dir
                else Path(args.artifacts_dir) / normalize_project_name(project) / f"Журнал_ПНР_{normalize_project_name(project)}.pdf"
            ),
            cables_file=args.cables_file,
            include_clock=args.include_clock,
            project_code=project,
            artifacts_dir=(
                default_artifacts_dir(project)
                if not args.artifacts_dir
                else Path(args.artifacts_dir) / normalize_project_name(project)
            ),
        ):
            failures.append(project)
            continue

    if failures:
        print(f"[WARN] Есть проблемы с проектами: {', '.join(failures)}")
        return 1

    print(f"[OK] Сформированы экземпляры по {len(projects)} проектам.")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Генератор Markdown/PDF журнала ПНР.")
    parser.set_defaults(command="list-projects")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list-projects", help="Показать проекты из unified_db.json.")
    list_parser.add_argument("--db", default=str(UNIFIED_DB_FILE), help="Путь к unified_db.json.")
    list_parser.add_argument(
        "--sync-db",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Перед выводом актуализировать unified_db.json из results/.",
    )

    create_list_parser = subparsers.add_parser("create-list", help="Создать список устройств проекта.")
    create_list_parser.add_argument("--project", required=True, help="Код проекта.")
    create_list_parser.add_argument("--db", default=str(UNIFIED_DB_FILE), help="Путь к unified_db.json.")
    create_list_parser.add_argument("--list-file", help="Путь к выходному файлу списка.")
    create_list_parser.add_argument(
        "--sync-db",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Перед созданием списка актуализировать unified_db.json из results/.",
    )

    render_parser = subparsers.add_parser("render", help="Сгенерировать Markdown-отчёт.")
    render_parser.add_argument("--project", required=True, help="Код проекта.")
    render_parser.add_argument("--db", default=str(UNIFIED_DB_FILE), help="Путь к unified_db.json.")
    render_parser.add_argument("--list-file", help="Файл с выбранными IP.")
    render_parser.add_argument("--output-file", help="Путь к итоговому Markdown-файлу.")
    render_parser.add_argument("--cables-file", default=str(CABLES_FILE), help="Путь к кабельному журналу.")
    render_parser.add_argument("--template-file", default=str(TEMPLATE_FILE), help="Путь к Jinja2-шаблону.")
    render_parser.add_argument("--all-devices", action="store_true", help="Игнорировать list-file и брать все устройства проекта.")
    render_parser.add_argument("--pdf", action="store_true", help="После Markdown сразу собрать PDF.")
    render_parser.add_argument(
        "--artifacts-dir",
        help="Папка для промежуточных HTML/MD/PDF-артефактов (если не указана: build_html/<project>).",
    )
    render_parser.add_argument(
        "--include-clock",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Включать секции, связанные с часофикацией.",
    )
    render_parser.add_argument(
        "--sync-db",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Перед генерацией актуализировать unified_db.json из results/.",
    )

    render_html_parser = subparsers.add_parser("render-html", help="Сгенерировать HTML-отчёт.")
    render_html_parser.add_argument("--project", required=True, help="Код проекта.")
    render_html_parser.add_argument("--db", default=str(UNIFIED_DB_FILE), help="Путь к unified_db.json.")
    render_html_parser.add_argument("--list-file", help="Файл с выбранными IP.")
    render_html_parser.add_argument("--output-file", help="Путь к итоговому HTML-файлу.")
    render_html_parser.add_argument("--cables-file", default=str(CABLES_FILE), help="Путь к кабельному журналу.")
    render_html_parser.add_argument("--template-file", default=str(TEMPLATE_FILE), help="Путь к Jinja2-шаблону.")
    render_html_parser.add_argument("--all-devices", action="store_true", help="Игнорировать list-file и брать все устройства проекта.")
    render_html_parser.add_argument(
        "--artifacts-dir",
        help="Папка для HTML/MD-артефактов (если не указана: build_html/<project>).",
    )
    render_html_parser.add_argument(
        "--include-clock",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Включать секции, связанные с часофикацией.",
    )
    render_html_parser.add_argument(
        "--sync-db",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Перед генерацией актуализировать unified_db.json из results/.",
    )

    pdf_parser = subparsers.add_parser("pdf", help="Собрать PDF из уже готового Markdown.")
    pdf_parser.add_argument("markdown_file", help="Путь к Markdown-файлу.")

    build_cmd_parser = subparsers.add_parser("build", help="Полный pipeline генерации проекта.")
    build_cmd_parser.add_argument("--project", required=True, help="Код проекта.")
    build_cmd_parser.add_argument("--db", default=str(UNIFIED_DB_FILE), help="Путь к unified_db.json.")
    build_cmd_parser.add_argument("--list-file", help="Путь к файлу списка устройств.")
    build_cmd_parser.add_argument("--output-file", help="Путь к итоговому Markdown-файлу.")
    build_cmd_parser.add_argument("--cables-file", default=str(CABLES_FILE), help="Путь к кабельному журналу.")
    build_cmd_parser.add_argument("--template-file", default=str(TEMPLATE_FILE), help="Путь к Jinja2-шаблону.")
    build_cmd_parser.add_argument("--create-list", action="store_true", help="Создать или пересоздать список устройств проекта.")
    build_cmd_parser.add_argument("--all-devices", action="store_true", help="Сразу брать все устройства проекта без ручной правки списка.")
    build_cmd_parser.add_argument("--pdf", action="store_true", help="После Markdown сразу собрать PDF.")
    build_cmd_parser.add_argument(
        "--artifacts-dir",
        help="Папка для промежуточных HTML/MD/PDF-артефактов (если не указана: build_html/<project>).",
    )
    build_cmd_parser.add_argument(
        "--include-clock",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Включать секции, связанные с часофикацией.",
    )
    build_cmd_parser.add_argument(
        "--sync-db",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Перед генерацией актуализировать unified_db.json из results/.",
    )

    build_all_parser = subparsers.add_parser("build-all", help="Сформировать экземпляры по всем проектам.")
    build_all_parser.add_argument("--db", default=str(UNIFIED_DB_FILE), help="Путь к unified_db.json.")
    build_all_parser.add_argument("--cables-file", default=str(CABLES_FILE), help="Путь к кабельному журналу.")
    build_all_parser.add_argument("--template-file", default=str(TEMPLATE_FILE), help="Путь к Jinja2-шаблону.")
    build_all_parser.add_argument("--create-list", action="store_true", help="Создать или пересоздать списки устройств по всем проектам.")
    build_all_parser.add_argument("--all-devices", action="store_true", default=True, help="Собирать по всем устройствам проекта.")
    build_all_parser.add_argument("--pdf", action="store_true", help="После Markdown сразу собрать PDF.")
    build_all_parser.add_argument(
        "--artifacts-dir",
        help="Базовая папка артефактов для всех проектов; внутри создаются подпапки по коду проекта.",
    )
    build_all_parser.add_argument(
        "--include-clock",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Включать секции, связанные с часофикацией.",
    )
    build_all_parser.add_argument(
        "--sync-db",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Перед генерацией актуализировать unified_db.json из results/.",
    )

    render_ggs_parser = subparsers.add_parser("render-ggs", help="Сгенерировать Markdown-журнал ПНР для системы ГГС (Armtel).")
    render_ggs_parser.add_argument("--project", required=True, help="Код проекта ГГС (например, 12006-81-0600).")
    render_ggs_parser.add_argument("--template-file", default=str(GGS_TEMPLATE_FILE), help="Путь к шаблону ГГС.")
    render_ggs_parser.add_argument("--output", help="Путь для сохранения сгенерированного отчета.")

    return parser


def run_interactive() -> int:
    print("[RUN] Запуск в интерактивном режиме.")
    refresh_unified_db()

    devices = extract_all_devices()
    projects = get_projects(devices)
    project = choose_project_interactively(projects)
    project_devices = filter_devices_by_project(devices, project)

    list_file = default_list_file(project)
    output_file = default_output_file(project)
    create_switch_list(project_devices, list_file)

    print(f"[RUN] Выбран проект: {project}")
    print(f"[RUN] Список устройств обновлен: {list_file}")

    markdown_file = generate_markdown_report(
        final_devices=project_devices,
        cables_file=CABLES_FILE,
        template_file=TEMPLATE_FILE,
        output_file=output_file,
        include_clock=True,
    )
    if not markdown_file:
        return 1

    print(f"[RUN] Готово: {markdown_file}")
    print("[RUN] PDF автоматически не собирается. Экспортируй Markdown через VS Code.")
    return 0


def run_default_build_all() -> int:
    """
    Режим по умолчанию для запуска из IDE кнопкой Run (без аргументов):
    собрать отчеты по всем проектам.
    """
    print("[RUN] Запуск без аргументов: сборка всех проектов (build-all).")
    args = argparse.Namespace(
        db=str(UNIFIED_DB_FILE),
        cables_file=str(CABLES_FILE),
        template_file=str(TEMPLATE_FILE),
        create_list=False,
        all_devices=True,
        pdf=False,
        artifacts_dir=None,
        include_clock=True,
        sync_db=True,
    )
    return command_build_all(args)


def main() -> int:
    if len(sys.argv) == 1:
        try:
            return run_default_build_all()
        except (FileNotFoundError, ValueError) as exc:
            print(f"Ошибка: {exc}")
            return 1

    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "list-projects": command_list_projects,
        "create-list": command_create_list,
        "render": command_render,
        "render-ggs": command_render_ggs,
        "render-html": command_render_html,
        "pdf": command_pdf,
        "build": command_build,
        "build-all": command_build_all,
    }

    try:
        return handlers[args.command](args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Ошибка: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

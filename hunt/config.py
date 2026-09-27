"""Paths and config loading."""
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
PROFILE_DIR = ROOT / "profile"
QUEUE_DIR = ROOT / "queue"
LETTERS_DIR = ROOT / "output" / "letters"
DB_PATH = DATA_DIR / "jobs.db"
CV_PATH = PROFILE_DIR / "cv.md"
PROJECTS_PATH = PROFILE_DIR / "projects.md"   # extra GitHub projects, same rules as the CV
TRACKER_XLSX = ROOT / "tracker.xlsx"
TRACKER_CSV = ROOT / "tracker.csv"

STATUSES = ["new", "drafted", "applied", "interview", "rejected", "offer", "skipped"]

# Order used when two jobs have the same fit score.
LABEL_ORDER = ["remote_open", "nigeria", "sponsor_yes", "sponsor_likely", "sponsor_unknown", "restricted"]


def load_yaml(name):
    path = CONFIG_DIR / name if not os.path.isabs(str(name)) else Path(name)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_env():
    """Read .env into os.environ if python-dotenv is installed."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(ROOT / ".env")


def label_rank(label):
    return LABEL_ORDER.index(label) if label in LABEL_ORDER else len(LABEL_ORDER)


def fact_texts():
    """The CV plus the extra projects file: everything letters may use."""
    texts = [CV_PATH.read_text(encoding="utf-8")]
    if PROJECTS_PATH.exists():
        texts.append(PROJECTS_PATH.read_text(encoding="utf-8"))
    return "\n\n".join(texts)

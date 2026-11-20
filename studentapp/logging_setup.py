"""Konfigurasi logging ke file (agar tidak mengganggu tampilan menu)."""

import logging
from pathlib import Path


def setup_logging(debug=False, log_file="logs/app.log"):
    """INFO secara default; DEBUG jika debug=True. Jika file log gagal dibuat, pakai stderr."""
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    try:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers = [logging.FileHandler(log_file, encoding="utf-8")]
    except OSError:
        handlers = [logging.StreamHandler()]
    logging.basicConfig(level=level, format=fmt, handlers=handlers, force=True)

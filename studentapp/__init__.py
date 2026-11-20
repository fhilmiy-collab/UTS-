"""Package studentapp: logika Student Data Analyzer (UTS TK091).

Alur dependensi antar-module (tanpa siklus):
    exceptions <- validation <- records <- pipeline <- cli <- main.py
    analysis, storage, report dipakai oleh pipeline/cli.
"""

from .analysis import determine_status, summarize
from .validation import validate_student

__version__ = "1.0.0"
__all__ = ["determine_status", "summarize", "validate_student", "__version__"]

"""Make the shared Jackson 5 engine importable; this folder comes first so its timing.py (Beat It grid) wins."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ENGINE = HERE.parents[1] / 'jackson5' / 'src'
for p in (str(ENGINE), str(HERE)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(HERE))

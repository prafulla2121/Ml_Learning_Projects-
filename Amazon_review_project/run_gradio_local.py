import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from amazon_review_intel.ui.gradio_app import run

if __name__ == "__main__":
    run()

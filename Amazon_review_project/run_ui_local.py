import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))


def run_gradio() -> None:
    from amazon_review_intel.ui.gradio_app import run

    print("Starting Gradio UI...")
    run()


def run_streamlit() -> None:
    print("Starting Streamlit UI...")
    streamlit_app = SRC / "amazon_review_intel" / "ui" / "streamlit_app.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(streamlit_app), "--server.port", "7860", "--server.address", "127.0.0.1"],
        check=True,
    )


if __name__ == "__main__":
    try:
        run_gradio()
    except Exception as exc:
        print(f"Gradio UI unavailable, falling back to Streamlit: {exc}")
        run_streamlit()

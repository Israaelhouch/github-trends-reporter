import logging
import os

_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(log_dir: str = "logs", level: int = logging.INFO) -> None:
    """Configure the root logger once: console + a rolling file in `log_dir`.

    Modules should just use `logging.getLogger(__name__)`.
    """
    root = logging.getLogger()
    if getattr(root, "_trends_configured", False):
        return

    os.makedirs(log_dir, exist_ok=True)
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))

    file_handler = logging.FileHandler(os.path.join(log_dir, "pipeline.log"), encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_FORMAT))

    root.addHandler(console)
    root.addHandler(file_handler)
    # Keep third-party HTTP chatter out of the pipeline log.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    root._trends_configured = True

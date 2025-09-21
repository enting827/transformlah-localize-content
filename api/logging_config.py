import logging
import sys
import os

class UnicodeStreamHandler(logging.StreamHandler):
    """Stream handler that safely handles Unicode characters"""
    
    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            # Fallback: replace problematic characters and try again
            try:
                msg = self.format(record)
                # Replace Unicode characters that can't be encoded
                safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
                self.stream.write(safe_msg + self.terminator)
                self.flush()
            except Exception:
                # If all else fails, silently continue
                pass

def get_logger(name: str = __name__, level=logging.INFO) -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler with Unicode safety
        console_handler = UnicodeStreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler with UTF-8 encoding
        try:
            file_handler = logging.FileHandler("logs/app.log", encoding='utf-8', errors='replace')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass

        logger.setLevel(level)

    return logger
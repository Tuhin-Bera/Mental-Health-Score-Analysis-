from main import app


def main() -> None:
    print("Use: uvicorn main:app --reload")


__all__ = ["app", "main"]

def get_version():
    from pathlib import Path

    try:
        return (Path(__file__).parents[1] / "VERSION").read_text().strip()
    except FileNotFoundError:
        return "0.0.0dev0"


if __name__ == "__main__":
    print(f"installed version of this project: {get_version()}")

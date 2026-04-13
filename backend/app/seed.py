from app.db.bootstrap import bootstrap_database


def main() -> None:
    bootstrap_database(seed=True)


if __name__ == "__main__":
    main()

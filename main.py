from src.cli import cli_execute, cli_prepare
from src.logger import logger

def main() -> None:
    try:
        parser = cli_prepare()
        args = parser.parse_args()
        cli_execute(args)
    except Exception as ex:
        logger.exception(ex)
        exit(1)

if __name__ == "__main__":
    main()

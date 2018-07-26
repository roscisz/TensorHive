import tensorhive.cli as cli
import logging
from tensorhive.config import LogConfig

# GLOBAL TODOS
# TODO Capture tracebacks from all exceptions with e.g. log.error()


def main():
    LogConfig.apply()
    cli.main()


if __name__ == "__main__":
    main()

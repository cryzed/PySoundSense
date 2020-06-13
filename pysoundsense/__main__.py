from loguru import logger

from . import initialize, ExitCode
from .console import get_argument_parser, run


def main() -> None:
    argument_parser = get_argument_parser()
    arguments = argument_parser.parse_args()
    initialize(
        arguments.log_path,
        arguments.logging_level,
        arguments.log_rotation,
        arguments.log_compression,
        arguments.log_retention,
    )

    # noinspection PyBroadException
    try:
        argument_parser.exit(run(arguments))
    except KeyboardInterrupt:
        logger.info("Interrupted")
        argument_parser.exit(ExitCode.Success)
    except Exception:
        logger.exception("Unexpected error occurred:")
        argument_parser.exit(ExitCode.Failure)


if __name__ == "__main__":
    main()

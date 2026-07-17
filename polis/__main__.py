import sys


def _run():
    """Forward ``python -m polis`` to the real CLI, or fail cleanly if it is absent.

    Every flag and subcommand (``--help`` included) routes through the same
    ``polis.cli.main`` the installed ``polis`` entry point uses, so behavior is
    identical. If the CLI module cannot be imported, print a short message to
    stderr and exit non-zero instead of leaking an ImportError traceback.
    """
    try:
        from polis.cli import main
    except ImportError as exc:
        sys.stderr.write(f"polis: could not load the command-line interface: {exc}\n")
        return 1
    return main()


if __name__ == "__main__":
    sys.exit(_run())

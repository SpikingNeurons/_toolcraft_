"""Console script for toolcraft."""
import sys
# Note that this will load all tools and call APP() to register the commands
from . import tools


def main():
    tools.APP()


if __name__ == '__main__':
    sys.exit(main())


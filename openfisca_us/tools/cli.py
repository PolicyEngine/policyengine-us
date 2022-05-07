import argparse
import logging
import os
import sys
from openfisca_us.tools.testing import run_tests
from openfisca_core.scripts import build_tax_benefit_system

OPENFISCA_US = "openfisca_us"


def add_tax_benefit_system_arguments(parser):
    parser.add_argument(
        "-c",
        "--country-package",
        default=OPENFISCA_US,
        action="store",
        help='country package to use. If not provided, an automatic detection will be attempted by scanning the python packages installed in your environment which name contains the word "openfisca".',
    )
    parser.add_argument(
        "-e",
        "--extensions",
        default=[],
        action="store",
        help="extensions to load",
        nargs="*",
    )
    parser.add_argument(
        "-r",
        "--reforms",
        action="store",
        help="reforms to apply to the country package",
        nargs="*",
    )

    return parser


def build_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        help="Available commands", dest="command"
    )
    subparsers.required = (
        True  # Can be added as an argument of add_subparsers in Python 3
    )

    def build_test_parser(parser):
        parser = add_tax_benefit_system_arguments(parser)
        parser.add_argument(
            "path",
            help="paths (files or directories) of tests to execute",
            nargs="+",
        )
        parser.add_argument(
            "-n",
            "--name_filter",
            default=None,
            help="partial name of tests to execute. Only tests with the given name_filter in their name, file name, or keywords will be run.",
        )
        parser.add_argument(
            "-p",
            "--pdb",
            action="store_true",
            default=False,
            help="drop into debugger on failures or errors",
        )
        parser.add_argument(
            "--performance-graph",
            "--performance",
            action="store_true",
            default=False,
            help="output a performance graph in a 'performance_graph.html' file",
        )
        parser.add_argument(
            "--performance-tables",
            action="store_true",
            default=False,
            help="output performance CSV tables",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            default=False,
            help="increase output verbosity",
        )
        parser.add_argument(
            "-o",
            "--only-variables",
            nargs="*",
            default=None,
            help="variables to test. If specified, only test the given variables.",
        )
        parser.add_argument(
            "-i",
            "--ignore-variables",
            nargs="*",
            default=None,
            help="variables to ignore. If specified, do not test the given variables.",
        )

        return parser

    parser_test = subparsers.add_parser(
        "test", help="Run OpenFisca YAML tests"
    )
    parser_test = build_test_parser(parser_test)

    return parser


def main():
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        stream=sys.stdout,
    )

    tax_benefit_system = build_tax_benefit_system(
        OPENFISCA_US, args.extensions, args.reforms
    )

    options = {
        "pdb": args.pdb,
        "performance_graph": args.performance_graph,
        "performance_tables": args.performance_tables,
        "verbose": args.verbose,
        "name_filter": args.name_filter,
        "only_variables": args.only_variables,
        "ignore_variables": args.ignore_variables,
    }

    paths = [os.path.abspath(path) for path in args.path]
    sys.exit(run_tests(tax_benefit_system, paths, options))


if __name__ == "__main__":
    main()

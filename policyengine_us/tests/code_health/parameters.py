"""
This module contains a test that iterates through all parameter files in the policyengine_us/parameters directory and asserts that none of them contain the '\t' character.
"""

from policyengine_us.model_api import REPO


def test_parameter_files_do_not_contain_tabs():
    """
    This test iterates through all parameter files in the policyengine_us/parameters directory and asserts that none of them contain the '\t' character.
    """
    errors = []
    for file_name in (REPO / "parameters").glob("**/*.yaml"):
        with file_name.open() as file:
            i = 0
            for line in file:
                i += 1
                if "\t" in line:
                    errors.append(
                        f"\n\n{file_name.relative_to(REPO)} (line {i}):"
                        + "'\\t' character found in line (shown below):\n\n"
                        + line.replace("\t", "[TAB]")
                    )

    num_errors = len(errors)
    assert num_errors == 0, (
        f"\nFound {len(errors)} parameter file{'s' if len(errors) != 1 else ''} with tabs. Details below:"
        + "\n".join(errors)
    )

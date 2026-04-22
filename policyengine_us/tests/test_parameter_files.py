from datetime import date
from pathlib import Path

import yaml


PARAMETERS_DIR = Path(__file__).resolve().parents[1] / "parameters"


def test_parameter_yaml_files_are_syntax_parseable():
    errors = []

    for path in sorted(PARAMETERS_DIR.rglob("*.yaml")):
        try:
            yaml.compose(path.read_text())
        except yaml.YAMLError as exc:
            errors.append(f"{path.relative_to(PARAMETERS_DIR.parent)}: {exc}")

    assert errors == []


def test_calworks_yaml_fixes_preserve_effective_dates():
    max_au_size = yaml.safe_load(
        (
            PARAMETERS_DIR
            / "gov/states/ca/cdss/tanf/cash/monthly_payment/max_au_size.yaml"
        ).read_text()
    )
    region1_counties = yaml.safe_load(
        (
            PARAMETERS_DIR / "gov/states/ca/cdss/tanf/cash/region1_counties.yaml"
        ).read_text()
    )

    assert list(max_au_size["values"].keys()) == [date(2023, 10, 1)]
    assert list(region1_counties["values"].keys()) == [date(2023, 7, 1)]

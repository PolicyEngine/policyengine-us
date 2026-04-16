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

"""No shipped reform stores a variable apart from baseline policy.

A reform's baseline arm drops each holder the reform built for its own
definition of a variable in another entity or with other ``ETERNITY``
storage, and refuses an input the caller gave that variable
(``SPMSimulationMixin._refuse_inputs_baseline_policy_drops``). Only a reform
that redefines a variable that way reaches either path. This scan reads the
source of every reform under ``policyengine_us/reforms``, without importing
the package, and finds none that does. A new reform that changes a variable's
entity or all-time storage fails it, and so does one that passes
``update_variable``, ``add_variable`` or ``replace_variable`` anything other
than a class defined in its own file.

A reform's class that leaves out ``entity`` or ``definition_period`` keeps
the baseline variable's, so a missing attribute counts as unchanged. The scan
reads two forms at the top level of a class body: a plain assignment
(``definition_period = ETERNITY``) and an annotated one with a value
(``definition_period: str = ETERNITY``). It doesn't read a tuple target
(``entity, definition_period = ...``), an augmented assignment, an assignment
inside an ``if`` or a loop in the class body, an attribute set on the class
after its ``class`` statement or through ``setattr``, or an attribute the
class inherits from a base other than ``Variable`` or a baseline variable.

The second test checks that the scan flags the reforms this package's tests
build to store a variable apart, and the third that it reads the annotated
form.
"""

import ast
import re
from functools import cache
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[2]
ATTRIBUTES = ("entity", "definition_period")
CHANGES = re.compile(
    r"\.(update_variable|add_variable|replace_variable)\(\s*([A-Za-z_][A-Za-z0-9_]*)"
)


def named(node):
    """An entity or period expression as a name, or None if it isn't one."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        # Core accepts "year" and "eternity" as well as YEAR and ETERNITY.
        return node.value.upper()
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def variable_classes(path):
    """Each Variable class in ``path``, with the attributes its body sets.

    A class counts if it subclasses ``Variable`` or a baseline variable the
    file imports from ``policyengine_us.variables``."""
    tree = ast.parse(path.read_text(), filename=str(path))
    baseline_names = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("policyengine_us.variables")
        for alias in node.names
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = {
            base.id if isinstance(base, ast.Name) else getattr(base, "attr", None)
            for base in node.bases
        }
        if "Variable" not in bases and not bases & baseline_names:
            continue
        attributes = {}
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name) and target.id in ATTRIBUTES:
                        attributes[target.id] = statement.value
            elif (
                isinstance(statement, ast.AnnAssign)
                and statement.value is not None
                and isinstance(statement.target, ast.Name)
                and statement.target.id in ATTRIBUTES
            ):
                attributes[statement.target.id] = statement.value
        yield node.name, attributes, node.lineno


def label(path):
    """``path`` from the repository root, or in full outside it."""
    if path.is_relative_to(PACKAGE.parent):
        return path.relative_to(PACKAGE.parent)
    return path


@cache
def baseline_variables():
    found = {}
    for path in sorted((PACKAGE / "variables").rglob("*.py")):
        for name, attributes, _ in variable_classes(path):
            found[name] = {key: named(value) for key, value in attributes.items()}
    return found


def stored_apart(files):
    """The classes in ``files`` that redefine a baseline variable in another
    entity or with other all-time storage, and the comparisons the scan
    can't make."""
    baseline = baseline_variables()
    apart, unresolved = [], []
    for path in files:
        for name, attributes, line in variable_classes(path):
            if name not in baseline:
                continue
            where = f"{name} ({label(path)}:{line})"
            for key, value in attributes.items():
                mine, theirs = named(value), baseline[name].get(key)
                if mine is None or theirs is None:
                    unresolved.append(f"{where}: {key}")
                elif key == "entity" and mine != theirs:
                    apart.append((name, where))
                elif key == "definition_period" and (mine == "ETERNITY") != (
                    theirs == "ETERNITY"
                ):
                    apart.append((name, where))
    return apart, unresolved


def changes_the_scan_cannot_see(files):
    """Variable changes whose argument isn't a class defined in the same file,
    or a loop variable over such classes."""
    found = []
    for path in files:
        text = path.read_text()
        defined = {name for name, _, _ in variable_classes(path)}
        for node in ast.walk(ast.parse(text)):
            if (
                isinstance(node, ast.For)
                and isinstance(node.target, ast.Name)
                and isinstance(node.iter, (ast.Tuple, ast.List))
                and all(
                    isinstance(element, ast.Name) and element.id in defined
                    for element in node.iter.elts
                )
            ):
                defined.add(node.target.id)
        for match in CHANGES.finditer(text):
            if match.group(2) not in defined:
                found.append(f"{match.group(1)}({match.group(2)}) in {label(path)}")
    return found


def test_no_shipped_reform_stores_a_variable_apart_from_baseline_policy():
    reforms = sorted((PACKAGE / "reforms").rglob("*.py"))
    assert len(reforms) > 100
    apart, unresolved = stored_apart(reforms)
    assert apart == []
    assert unresolved == []
    assert changes_the_scan_cannot_see(reforms) == []


def test_the_scan_flags_reforms_built_to_store_a_variable_apart():
    tests = PACKAGE / "tests" / "core"
    apart, _ = stored_apart(
        [tests / "test_reform_baseline_arm_inputs.py", tests / "test_spm_system.py"]
    )
    assert {"child_care_subsidies", "is_household_head"} <= {name for name, _ in apart}


def test_the_scan_reads_an_annotated_assignment(tmp_path):
    """``definition_period: str = ETERNITY`` sets the class attribute as the
    plain assignment does, so the scan flags a reform that stores
    ``child_care_subsidies`` for all time that way."""
    reform = tmp_path / "annotated_reform.py"
    reform.write_text(
        "from policyengine_core.periods import ETERNITY\n"
        "from policyengine_core.variables import Variable\n"
        "\n"
        "\n"
        "class child_care_subsidies(Variable):\n"
        "    definition_period: str = ETERNITY\n"
    )
    apart, unresolved = stored_apart([reform])
    assert [name for name, _ in apart] == ["child_care_subsidies"]
    assert unresolved == []

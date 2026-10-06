"""The stored EITC documentation charts agree with the parameters they show.

The docs build does not execute notebooks (`execute_notebooks: off` in
docs/_config.yml), so docs/gov/irs/credits/eitc.ipynb publishes the outputs it
was last saved with. Those outputs kept the 2021 joint phase-out bonus ($5,940)
for childless couples after the parameters moved to 2022 ($6,130), and a check
of the curves' maxima alone could not see it.

This check reads the notebook and the EITC parameter files without importing
the model. For the year the notebook simulates, it recomputes every stored
point of both charts, in the initial view and in each animation frame:

- the credit from 26 U.S.C. 32(a): the phase-in rate times earnings, capped at
  the maximum credit and at the maximum less the phase-out rate times earnings
  above the phase-out start (plus the joint bonus for couples), never below
  zero. The notebook's households have no income but the head's wages, so
  earnings are also AGI;
- the marginal rate as `IndividualSim.deriv` computes it: forward differences
  of the unrounded credit over the wage grid, the last one repeated;
- the wage grid itself, from the notebook's `sim.vary(...)` call.
"""

import json
import math
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
NOTEBOOK = REPO / "docs" / "gov" / "irs" / "credits" / "eitc.ipynb"
EITC = REPO / "policyengine_us" / "parameters" / "gov" / "irs" / "credits" / "eitc"
PLOTLY_MIME = "application/vnd.plotly.v1+json"
CHILD_COUNTS = {0, 1, 2, 3}
# Frames are named by the number of adults; two adults file jointly.
ADULT_FRAMES = {"1", "2"}
CREDIT_TOLERANCE = 1  # stored credits are rounded to whole dollars
RATE_TOLERANCE = 1e-4  # stored rates come from float32 credits


class _DateStringLoader(yaml.SafeLoader):
    """Keeps date keys as strings, so the 0000-01-01 sentinel loads."""


_DateStringLoader.yaml_implicit_resolvers = {
    key: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _value_in(node, year):
    """A leaf's value on January 1 of the year, as annual simulations read it."""
    values = node.get("values", node)
    instant = f"{year}-01-01"
    dates = [key for key in values if key != "metadata" and key <= instant]
    uprated = "uprating" in node.get("metadata", {})
    # The check cannot reproduce uprating, so an indexed amount must be
    # authored for the year itself.
    assert dates and (not uprated or instant in dates), (
        f"no authored value for {instant}"
    )
    value = values[max(dates)]
    return value["value"] if isinstance(value, dict) else value


def _by_child_count(file_name, year):
    raw = yaml.load((EITC / file_name).read_text(), Loader=_DateStringLoader)
    rows = sorted(
        (_value_in(row["threshold"], year), _value_in(row["amount"], year))
        for row in raw["brackets"]
    )

    def lookup(children):
        return next(
            amount for threshold, amount in reversed(rows) if children >= threshold
        )

    return lookup


def _schedule(year):
    maximum = _by_child_count("max.yaml", year)
    phase_in_rate = _by_child_count("phase_in_rate.yaml", year)
    phase_out_rate = _by_child_count("phase_out/rate.yaml", year)
    phase_out_start = _by_child_count("phase_out/start.yaml", year)
    joint_bonus = _by_child_count("phase_out/joint_bonus.yaml", year)

    def credit(adults, children):
        cap = maximum(children)
        start = phase_out_start(children)
        if adults == "2":
            start += joint_bonus(children)

        def at(wage):
            phased_out = cap - phase_out_rate(children) * max(0, wage - start)
            return max(0, min(phase_in_rate(children) * wage, cap, phased_out))

        return at

    return credit


def _notebook():
    notebook = json.loads(NOTEBOOK.read_text())
    sources = ["".join(cell["source"]) for cell in notebook["cells"]]
    setup = next(source for source in sources if "IndividualSim(" in source)
    year = int(re.search(r"IndividualSim\(year=(\d{4})\)", setup).group(1))
    vary = re.search(
        r"sim\.vary\(\"employment_income\", max=([\d_]+), step=(\d+)\)", setup
    )
    wages = list(range(0, int(vary.group(1).replace("_", "")) + 1, int(vary.group(2))))
    charts = {}
    for cell in notebook["cells"]:
        source = "".join(cell["source"])
        if cell["cell_type"] != "code" or "px.line(" not in source:
            continue
        measure = re.search(r'"employment_income",\s*"(\w+)"', source).group(1)
        outputs = [
            output
            for output in cell["outputs"]
            if PLOTLY_MIME in output.get("data", {})
        ]
        assert len(outputs) == 1, f"the {measure} cell has no single stored chart"
        charts[measure] = outputs[0]["data"][PLOTLY_MIME]
    assert set(charts) == {"eitc", "mtr"}
    return year, wages, charts


def _views(chart):
    """(adults, traces) for the initial view and each animation frame."""
    frames = {frame["name"]: frame["data"] for frame in chart["frames"]}
    assert set(frames) == ADULT_FRAMES
    # The initial view is the first frame, before the slider moves.
    return [("1", chart["data"])] + sorted(frames.items())


def _chart_errors(chart, measure, wages, credit):
    errors = []
    for adults, traces in _views(chart):
        assert {int(trace["name"]) for trace in traces} == CHILD_COUNTS
        for trace in traces:
            children = int(trace["name"])
            where = f"{measure}, {adults} adult(s), {children} children"
            if trace["x"] != wages:
                errors.append(f"{where}: wage axis is not the vary() grid")
                continue
            amounts = [credit(adults, children)(wage) for wage in wages]
            if measure == "eitc":
                expected = [round(amount) for amount in amounts]
                tolerance = CREDIT_TOLERANCE
            else:
                steps = [
                    -(after - before) / (high - low)
                    for before, after, low, high in zip(
                        amounts, amounts[1:], wages, wages[1:]
                    )
                ]
                expected = steps + steps[-1:]
                tolerance = RATE_TOLERANCE
            for wage, stored, wanted in zip(wages, trace["y"], expected):
                if not math.isclose(stored, wanted, rel_tol=0, abs_tol=tolerance):
                    errors.append(
                        f"{where}, wages {wage:,}: stored {stored}, parameters {wanted}"
                    )
    return errors


@pytest.fixture(scope="module")
def stored():
    year, wages, charts = _notebook()
    return year, wages, charts, _schedule(year)


@pytest.mark.parametrize("measure", ["eitc", "mtr"])
def test_stored_eitc_chart_matches_parameters(stored, measure):
    _, wages, charts, credit = stored
    errors = _chart_errors(charts[measure], measure, wages, credit)

    assert not errors, f"{len(errors)} stored points differ:\n" + "\n".join(errors[:20])


def _mutated(chart, change):
    chart = json.loads(json.dumps(chart))
    change(chart)
    return chart


@pytest.mark.parametrize(
    "measure, change",
    [
        # A curve stored in reverse order.
        ("eitc", lambda chart: chart["frames"][1]["data"][2]["y"].reverse()),
        ("mtr", lambda chart: chart["data"][1]["y"].reverse()),
        # A wage axis that no longer matches the simulated grid.
        (
            "eitc",
            lambda chart: chart["frames"][0]["data"][0]["x"].__setitem__(0, 1_000_000),
        ),
        ("eitc", lambda chart: chart["data"][3]["x"].pop()),
        # One point a few dollars off, as the stale joint-bonus frames were.
        (
            "eitc",
            lambda chart: chart["frames"][1]["data"][0]["y"].__setitem__(152, 552),
        ),
    ],
)
def test_chart_check_rejects_corrupted_charts(stored, measure, change):
    _, wages, charts, credit = stored
    chart = _mutated(charts[measure], change)

    assert _chart_errors(chart, measure, wages, credit)

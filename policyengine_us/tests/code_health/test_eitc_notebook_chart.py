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

It also checks the labels a reader sees: each chart's title year, each
curve's hover labels, and that each slider step plays the frame it names.
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
CHILD_COUNTS = [0, 1, 2, 3]
# Frames are named by the number of adults; two adults file jointly.
ADULT_FRAMES = ["1", "2"]
# Stored credits are the credit rounded to whole dollars, so they sit within
# half a dollar of the exact amount, plus float32 noise (about 5e-4 at these
# amounts).
CREDIT_TOLERANCE = 0.502
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


def _value_in(node, year, uprated):
    """A leaf's value on January 1 of the year, as annual simulations read it."""
    values = node.get("values", node)
    instant = f"{year}-01-01"
    dates = [key for key in values if key != "metadata" and key <= instant]
    uprated = uprated or "uprating" in node.get("metadata", {})
    # The check cannot reproduce uprating, so an indexed amount must be
    # authored for the year itself.
    assert dates and (not uprated or instant in dates), (
        f"no authored value for {instant}"
    )
    value = values[max(dates)]
    return value["value"] if isinstance(value, dict) else value


def _by_child_count(file_name, year):
    raw = yaml.load((EITC / file_name).read_text(), Loader=_DateStringLoader)
    # Core also applies uprating declared on the whole scale to its leaves.
    scale_uprated = any("uprating" in key for key in raw.get("metadata", {}))

    def uprated(bracket):
        # ... and uprating declared on a bracket to its components.
        return scale_uprated or any(
            "uprating" in key for key in bracket.get("metadata", {})
        )

    rows = sorted(
        (
            _value_in(row["threshold"], year, uprated(row)),
            _value_in(row["amount"], year, uprated(row)),
        )
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
    charts, titles = {}, {}
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
        titles[measure] = re.search(r'title="([^"]+)"', source).group(1)
    assert set(charts) == {"eitc", "mtr"}
    return year, wages, charts, titles


def _views(chart):
    """(adults, traces) for the initial view and each animation frame."""
    # The initial view is the first frame, before the slider moves.
    return [(ADULT_FRAMES[0], chart["data"])] + [
        (frame["name"], frame["data"]) for frame in chart["frames"]
    ]


def _label_errors(chart, measure, year, title):
    errors = []
    stored_title = chart["layout"]["title"]["text"]
    if stored_title != title or str(year) not in stored_title:
        errors.append(f"{measure}: title {stored_title!r} is not the cell's {title!r}")
    if [frame["name"] for frame in chart["frames"]] != ADULT_FRAMES:
        errors.append(f"{measure}: frames are not {ADULT_FRAMES}")
    steps = chart["layout"]["sliders"][0]["steps"]
    if [step["label"] for step in steps] != ADULT_FRAMES:
        errors.append(f"{measure}: slider steps are not {ADULT_FRAMES}")
    for step in steps:
        if step["args"][0] != [step["label"]]:
            errors.append(
                f"{measure}: slider step {step['label']} plays {step['args'][0]}"
            )
    return errors


def _chart_errors(chart, measure, year, title, wages, credit):
    errors = _label_errors(chart, measure, year, title)
    for adults, traces in _views(chart):
        # Plotly matches a frame's curves to the initial view's by position.
        names = [int(trace["name"]) for trace in traces]
        if names != CHILD_COUNTS:
            errors.append(f"{measure}, {adults} adult(s): curves are {names}")
            continue
        for trace in traces:
            children = int(trace["name"])
            where = f"{measure}, {adults} adult(s), {children} children"
            hover = trace["hovertemplate"]
            if f"Adults={adults}<" not in hover or f"Children={children}<" not in hover:
                errors.append(f"{where}: hover labels read {hover!r}")
            if trace["x"] != wages or len(trace["y"]) != len(wages):
                errors.append(f"{where}: points are not on the vary() grid")
                continue
            amounts = [credit(adults, children)(wage) for wage in wages]
            if measure == "eitc":
                expected = amounts
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
            for wage, stored, wanted in zip(wages, trace["y"], expected, strict=True):
                if not math.isclose(stored, wanted, rel_tol=0, abs_tol=tolerance):
                    errors.append(
                        f"{where}, wages {wage:,}: stored {stored}, parameters {wanted}"
                    )
    return errors


@pytest.fixture(scope="module")
def stored():
    year, wages, charts, titles = _notebook()
    return year, wages, charts, titles, _schedule(year)


@pytest.mark.parametrize("measure", ["eitc", "mtr"])
def test_stored_eitc_chart_matches_parameters(stored, measure):
    year, wages, charts, titles, credit = stored
    errors = _chart_errors(
        charts[measure], measure, year, titles[measure], wages, credit
    )

    assert not errors, f"{len(errors)} stored points differ:\n" + "\n".join(errors[:20])


def _mutated(chart, change):
    chart = json.loads(json.dumps(chart))
    change(chart)
    return chart


def _set_point(trace, index, value):
    trace["y"][index] = value


def _swap_slider_frames(chart):
    steps = chart["layout"]["sliders"][0]["steps"]
    steps[0]["args"][0], steps[1]["args"][0] = steps[1]["args"][0], steps[0]["args"][0]


@pytest.mark.parametrize(
    "measure, change",
    [
        # A curve stored in reverse order.
        ("eitc", lambda chart: chart["frames"][1]["data"][2]["y"].reverse()),
        ("mtr", lambda chart: chart["data"][1]["y"].reverse()),
        # A wage axis that no longer matches the simulated grid.
        ("eitc", lambda chart: chart["frames"][0]["data"][0]["x"].__setitem__(0, 1e6)),
        ("eitc", lambda chart: chart["data"][3]["x"].pop()),
        # Credits missing from a curve.
        ("eitc", lambda chart: chart["data"][2].__setitem__("y", [])),
        ("mtr", lambda chart: chart["frames"][1]["data"][0]["y"].pop()),
        # One point off by a few dollars, as the stale joint-bonus frames
        # were, or by a single dollar.
        ("eitc", lambda chart: _set_point(chart["frames"][1]["data"][0], 152, 552)),
        (
            "eitc",
            lambda chart: _set_point(
                chart["data"][1], 300, chart["data"][1]["y"][300] + 1
            ),
        ),
        # A duplicated curve in place of another child count.
        (
            "eitc",
            lambda chart: chart["frames"][1]["data"].__setitem__(
                3, chart["frames"][1]["data"][2]
            ),
        ),
        # Curves out of order, which plotly would pair with the wrong colour.
        ("mtr", lambda chart: chart["frames"][0]["data"].reverse()),
        # Labels that misdescribe the curves.
        ("eitc", _swap_slider_frames),
        ("eitc", lambda chart: chart["layout"]["sliders"][0]["steps"].pop()),
        (
            "mtr",
            lambda chart: chart["frames"][1]["data"][0].__setitem__(
                "hovertemplate", "Children=0<br>Adults=1<br>%{y}"
            ),
        ),
        (
            "eitc",
            lambda chart: chart["layout"]["title"].__setitem__(
                "text", "Earned income tax credit, 2021"
            ),
        ),
        (
            "eitc",
            lambda chart: chart["layout"]["title"].__setitem__(
                "text", "EITC for single filers by number of qualifying children, 2022"
            ),
        ),
    ],
)
def test_chart_check_rejects_corrupted_charts(stored, measure, change):
    year, wages, charts, titles, credit = stored
    chart = _mutated(charts[measure], change)

    assert _chart_errors(chart, measure, year, titles[measure], wages, credit)

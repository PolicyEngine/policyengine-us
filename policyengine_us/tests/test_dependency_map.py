from pathlib import Path

from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.tools.dependency_map import (
    DEFAULT_TESTS_ROOT,
    iter_yaml_tests,
    merge_edges,
    trace_yaml_tests,
)

CTC_TESTS = DEFAULT_TESTS_ROOT / "gov" / "irs" / "credits" / "ctc"


def reachable(consumers: dict[str, set[str]], start: str) -> set[str]:
    seen: set[str] = set()
    frontier = [start]
    while frontier:
        name = frontier.pop()
        for user in consumers.get(name, ()):
            if user not in seen:
                seen.add(user)
                frontier.append(user)
    return seen


def test_ctc_tests_record_bracket_parameter_reads_and_variable_edges():
    (readers, consumers), stats = trace_yaml_tests(
        CountryTaxBenefitSystem(), [CTC_TESTS]
    )

    assert stats["tests"] > 0
    # p.base.calc(age) is a scale read: recorded at the scale node.
    assert "ctc_child_individual_maximum" in readers["gov.irs.credits.ctc.amount.base"]
    # A yearly formula read, which core's tracer misses without the workaround.
    assert (
        "refundable_ctc" in readers["gov.irs.credits.ctc.refundable.fully_refundable"]
    )
    # The maximum feeds both credit outputs a few formula hops downstream.
    downstream = reachable(consumers, "ctc_maximum")
    assert {"ctc", "refundable_ctc"} <= downstream
    # Neutralisation switches are noise, not reform levers.
    assert not any(path.startswith("gov.abolitions.") for path in readers)


def test_iter_yaml_tests_skips_reforms_inline_changes_and_covered_outputs(
    tmp_path: Path,
):
    (tmp_path / "cases.yaml").write_text(
        """
- name: plain
  period: 2024
  input: {age: 30}
  output: {is_adult: true}
- name: with reform
  period: 2024
  reforms: policyengine_us.reforms.some_reform
  input: {age: 30}
  output: {is_adult: true}
- name: inline parameter change
  period: 2024
  input: {age: 30, gov.irs.credits.ctc.amount.adult_dependent: 1000}
  output: {is_adult: true}
- name: no output
  period: 2024
  input: {age: 30}
- name: same output again
  period: 2024
  input: {age: 12}
  output: {is_adult: false}
- name: new output
  period: 2024
  input: {age: 12}
  output: {is_adult: false, is_child: true}
"""
    )

    names = [test["name"] for _, test in iter_yaml_tests([tmp_path])]
    every = [test["name"] for _, test in iter_yaml_tests([tmp_path], every_test=True)]

    assert names == ["plain", "new output"]
    assert every == ["plain", "same output again", "new output"]


def test_merge_edges_unions_both_sides():
    readers, consumers = merge_edges(
        ({"gov.a": {"x"}}, {"x": {"y"}}),
        ({"gov.a": {"z"}, "gov.b": {"w"}}, {"x": {"q"}}),
    )

    assert readers == {"gov.a": {"x", "z"}, "gov.b": {"w"}}
    assert consumers == {"x": {"y", "q"}}

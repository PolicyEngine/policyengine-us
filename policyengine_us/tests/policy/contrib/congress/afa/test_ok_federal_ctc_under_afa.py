"""The AFA contrib reform removes non_refundable_ctc from the federal
non-refundable credit list (fully-refundable restructure). Oklahoma's
ok_federal_ctc used to .index() that entry unconditionally, so any Oklahoma
simulation under the AFA raised ValueError. The formula now treats an
absent non-refundable CTC as fully refundable — this test locks that in
through the same Reform.from_dict path production traffic uses."""

from policyengine_core.reforms import Reform
from policyengine_us import Simulation


def test_ok_federal_ctc_computes_under_afa():
    reform = Reform.from_dict(
        {"gov.contrib.congress.afa.in_effect": {"2026-01-01.2100-12-31": True}},
        country_id="us",
    )
    situation = {
        "people": {
            "parent": {
                "age": {2026: 35},
                "employment_income": {2026: 30_000},
            },
            "child": {"age": {2026: 4}},
        },
        "tax_units": {"tax_unit": {"members": ["parent", "child"]}},
        "spm_units": {"spm_unit": {"members": ["parent", "child"]}},
        "households": {
            "household": {
                "members": ["parent", "child"],
                "state_name": {2026: "OK"},
            }
        },
    }
    sim = Simulation(situation=situation, reform=reform)
    ok_federal_ctc = sim.calculate("ok_federal_ctc", 2026)[0]
    refundable_ctc = sim.calculate("refundable_ctc", 2026)[0]
    # With the CTC fully refundable there is no non-refundable portion, so
    # the credit allowed for the Oklahoma calculation is the refundable CTC.
    assert ok_federal_ctc == refundable_ctc
    assert refundable_ctc > 0

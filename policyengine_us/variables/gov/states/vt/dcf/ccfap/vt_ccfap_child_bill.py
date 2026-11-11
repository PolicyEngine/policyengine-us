from policyengine_us.model_api import *


class vt_ccfap_child_bill(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Vermont CCFAP monthly bill for the child's care"
    documentation = (
        "What the person's child care provider charges for the person, by the "
        "month: the person's share of the SPM unit's pre-subsidy bill, plus an "
        "even part of the shares of the members not in care. Zero for a member "
        "not in care."
    )
    reference = (
        # PDF page 1
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Memo-UPK-and-CCFAP-family-tuition-Summer-2026-Update.pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/Act76/Memo-Act-76-CCFAP-Rule-Revision.pdf#page=11",
    )

    def formula(person, period, parameters):
        # The children in care carry the bill shares of the members not in
        # care, so the bill follows the care.
        in_care = person("vt_ccfap_in_care", period)
        bill_share = person("pre_subsidy_childcare_expenses", period.this_year)
        is_child = person("is_child", period.this_year)
        count_in_care = max_(person.spm_unit.sum(in_care), 1)
        share_not_in_care = person.spm_unit.sum(where(in_care, 0, bill_share))
        kept = bill_share + share_not_in_care / count_in_care
        # pre_subsidy_childcare_expenses splits the bill over members under 18,
        # so an 18-year-old in care, with special needs or under court
        # supervision, gets none of it. Then the members in care split the
        # whole bill evenly.
        skipped = person.spm_unit.any(in_care & ~is_child & (bill_share == 0))
        even = person.spm_unit.sum(bill_share) / count_in_care
        annual_bill = where(in_care, where(skipped, even, kept), 0)
        return annual_bill / MONTHS_IN_YEAR

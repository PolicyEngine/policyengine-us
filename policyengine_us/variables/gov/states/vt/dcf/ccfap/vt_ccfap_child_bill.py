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
        "month: the person's share of the SPM unit's pre-subsidy bill, plus the "
        "shares of the members not in care. Zero for a member not in care."
    )
    reference = (
        # PDF pages 1, 6
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Memo-UPK-and-CCFAP-family-tuition%20(1).pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/Act76/Memo-Act-76-CCFAP-Rule-Revision.pdf#page=11",
    )

    def formula(person, period, parameters):
        # Once a child in the SPM unit has care hours, the children in care
        # carry the bill shares of the members not in care.
        in_care = person("vt_ccfap_in_care", period)
        bill_share = person("pre_subsidy_childcare_expenses", period.this_year)
        hours = person("childcare_hours_per_week", period.this_year)
        # A member in care who has hours is a child with hours, so this asks
        # whether any child in the unit has care hours.
        unit_has_hours = person.spm_unit.any(in_care & (hours > 0))
        share_not_in_care = person.spm_unit.sum(where(in_care, 0, bill_share))
        count_in_care = person.spm_unit.sum(in_care)
        moved_share = share_not_in_care / max_(count_in_care, 1)
        annual_bill = where(in_care, bill_share + moved_share * unit_has_hours, 0)
        return annual_bill / MONTHS_IN_YEAR

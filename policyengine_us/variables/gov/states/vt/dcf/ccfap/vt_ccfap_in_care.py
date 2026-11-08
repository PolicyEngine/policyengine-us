from policyengine_us.model_api import *


class vt_ccfap_in_care(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "In child care for the Vermont CCFAP payment"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=13",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/Act76/Memo-Act-76-CCFAP-Rule-Revision.pdf#page=11",
    )

    def formula(person, period, parameters):
        # Section V pays only for weeks of attendance, in the 2009 text and as
        # the division revised it effective June 30, 2024, so a child who
        # attends no provider draws nothing. With no attendance record, a
        # child's care hours stand in for attendance. An adult's hours say
        # nothing about which child attends. When no child in the SPM unit has
        # care hours, each child's share of the bill stands in instead;
        # pre_subsidy_childcare_expenses splits that bill evenly across the
        # unit's children.
        eligible_child = person("vt_ccfap_eligible_child", period)
        is_child = person("is_child", period.this_year)
        bill_share = person("pre_subsidy_childcare_expenses", period.this_year)
        hours = person("childcare_hours_per_week", period.this_year)
        child_has_hours = (hours > 0) & (is_child | eligible_child)
        unit_has_hours = person.spm_unit.any(child_has_hours)
        return where(unit_has_hours, child_has_hours, bill_share > 0)

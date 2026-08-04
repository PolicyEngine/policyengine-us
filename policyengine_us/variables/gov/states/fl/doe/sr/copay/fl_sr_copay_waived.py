from policyengine_us.model_api import *


class fl_sr_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida School Readiness parent copay waived"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.fldoe.org/file/20628/2025-2027CCDFStatePlan.pdf#page=52",
        "https://flrules.elaws.us/fac/6m-4.400",
        "https://www.flsenate.gov/laws/statutes/2025/1002.84",
    )

    def formula(spm_unit, period, parameters):
        # FFY2025-27 CCDF State Plan s. 3.3.1: Florida waives the parent copay
        # for families that are (i)-(ii) at or below 150% FPL, (iii) homeless,
        # (iv) have a child with a disability, (v) enrolled in Head Start /
        # Early Head Start, or (vi) have a child in foster care. The case-by-case
        # at-risk / protective-services waiver (6M-4.400(6)(a)) and the
        # coalition-defined "other criteria" (s. 1002.84(9)) are determined per
        # family and are not derivable, so they are not modeled at the moment.
        p = parameters(period).gov.states.fl.doe.sr.copay.waiver
        person = spm_unit.members

        # (i)-(ii) Income at or below 150% FPL. spm_unit_fpg is YEAR-defined;
        # the bare monthly period auto-divides it to a monthly value, matching
        # the monthly countable income (no annualization needed).
        countable_income = max_(spm_unit("fl_sr_countable_income", period), 0)
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        income_fpl_ratio = where(monthly_fpg > 0, countable_income / monthly_fpg, 0)
        low_income = income_fpl_ratio <= p.income_fpl_limit

        # (iii) Family experiencing homelessness.
        homeless = spm_unit.household("is_homeless", period.this_year)
        # (iv) A child with a disability.
        has_disabled_child = spm_unit.any(
            person("is_child", period.this_year)
            & person("is_disabled", period.this_year)
        )
        # (v) Enrolled in Head Start or Early Head Start.
        has_head_start = spm_unit.any(
            person("is_enrolled_in_head_start", period.this_year)
        )
        # (vi) A child in foster care (kinship care and case-by-case protective
        # services are not derivable -- see comment above).
        has_foster_child = spm_unit.any(person("is_in_foster_care", period.this_year))

        return (
            low_income
            | homeless
            | has_disabled_child
            | has_head_start
            | has_foster_child
        )

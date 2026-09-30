from policyengine_us.model_api import *


class ne_liheap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nebraska LIHEAP gross countable household income"
    defined_for = StateCode.NE
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/NE_Plan_2026.pdf#page=7"

    def formula_2026(spm_unit, period, parameters):
        # 476 NAC 2-002.01 incorporates SNAP's income treatment, but not
        # SNAP's net-income deductions or student/work eligibility tests.
        p = parameters(period).gov.usda.snap.income.sources
        person = spm_unit.members
        included = person("is_snap_immigration_status_eligible", period.first_month)
        size = spm_unit("ne_liheap_household_size", period)
        fraction = size / max_(spm_unit("spm_unit_size", period), 1)
        share = where(included, 1, spm_unit.project(fraction))
        unearned = max_(add(person, period, p.unearned), 0)
        unit_unearned = add(spm_unit, period, p.unearned_spm_unit)
        earned = spm_unit("ne_liheap_earned_income", period)
        # Annual inputs approximate the agency's anticipated income at the
        # application date. Existing SNAP source omissions also apply here.
        return earned + spm_unit.sum(unearned * share) + max_(unit_unearned, 0)

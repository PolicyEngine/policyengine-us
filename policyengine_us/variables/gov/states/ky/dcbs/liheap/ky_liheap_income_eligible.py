from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ky_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kentucky LIHEAP income eligibility"
    defined_for = StateCode.KY
    reference = "https://www.capky.org/wp-content/uploads/2026/01/2025-2026-LIHEAP-Fact-Sheet-V2.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.liheap
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        table_size = clip(size, 1, p.maximum_table_size)
        additional_people = max_(size - p.maximum_table_size, 0)
        guideline = fpg(
            table_size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        additional_guideline = (
            fpg(
                table_size + 1,
                state_group,
                period,
                parameters,
                year_lag=p.fpg_year_lag,
            )
            - guideline
        )
        # The fact sheet states "Add $688 for each additional family member"
        # without a derivation. Rounding the additional-person guideline up at
        # the income limit rate reproduces $688 for FY2026 and all eight
        # published limits. The workbook's own table for sizes 9-14 rounds each
        # whole limit instead and differs by up to $3 (for example $8,144
        # against $8,145 at size 10); the fact sheet is followed.
        monthly_limit = np.ceil(guideline * p.income_limit / MONTHS_IN_YEAR)
        monthly_increment = np.ceil(
            additional_guideline * p.income_limit / MONTHS_IN_YEAR
        )
        income = spm_unit("ky_liheap_income", period) / MONTHS_IN_YEAR
        return income <= monthly_limit + additional_people * monthly_increment

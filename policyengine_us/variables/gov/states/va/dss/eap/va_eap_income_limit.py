from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class va_eap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Virginia EAP annual income limit"
    documentation = "Twelve times the maximum monthly countable income for the household size: 150% of the federal poverty guideline floored to whole monthly dollars for sizes up to 20, plus the floored monthly increment for each member over 20."
    reference = (
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=28",
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/VA_BenefitMatrix_2026.pdf#page=1",
        "https://law.lis.virginia.gov/admincodefull/title22/agency40/chapter680/",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap.eligibility
        size = spm_unit("va_eap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        capped_size = clip(size, 1, p.max_table_size)
        guideline = fpg(
            capped_size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        additional_guideline = (
            fpg(
                capped_size + 1,
                state_group,
                period,
                parameters,
                year_lag=p.fpg_year_lag,
            )
            - guideline
        )
        # Manual B.6.a prints monthly limits for sizes 1 to 20 and "for each
        # extra member over 20, add $687". Flooring 150% of the 2025 guideline
        # over twelve months reproduces every printed amount and the $687
        # increment; this is a reconciled numerical pattern, not an express
        # rounding rule.
        monthly_limit = np.floor(p.fpg_rate * guideline / MONTHS_IN_YEAR)
        monthly_increment = np.floor(p.fpg_rate * additional_guideline / MONTHS_IN_YEAR)
        additional_people = max_(size - p.max_table_size, 0)
        return (monthly_limit + additional_people * monthly_increment) * MONTHS_IN_YEAR

from policyengine_us.model_api import *


class or_wfhdc_household_size_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Household size eligible for the Oregon working family household and dependent care credit"
    documentation = "Oregon Working Family Household and Dependent Care Credit household eligibility"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc
        # Over two individuals have to be present in the tax unit.
        return tax_unit("tax_unit_size", period) >= p.min_tax_unit_size

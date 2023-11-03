from policyengine_us.model_api import *


class hi_cdcc_min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii minimum income between head and spouse for the CDCC"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29"
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41"
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2"
    )

    def formula(tax_unit, period, parameters):
        # Schedule X PART II:
        # line 8 & line 9
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        hi_cdcc_earned_income = person("hi_cdcc_earned_income", period)
        # remove impact of dependent income by assigning np.inf
        return tax_unit.min(
            where(head_or_spouse, hi_cdcc_earned_income, np.inf)
        )

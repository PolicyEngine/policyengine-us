from policyengine_us.model_api import *


class ky_family_size_tax_credit_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky family size tax credit rate"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188"
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        income = tax_unit("ky_modified_agi", period)
        fpg = parameters(period).gov.hhs.fpg
        # This will be CONTIGUOUS_US for Kentucky.
        state_group = tax_unit.household("state_group", period)
        p1 = fpg.first_person[state_group]
        padd = fpg.additional_person[state_group]
        family_size = tax_unit("tax_unit_size", period)
        # No more than 4 people are accounted for in the credit
        p = parameters(period).gov.states.ky.tax.income.credits.family_size
        capped_family_size = min_(family_size, p.family_size_cap)
        poverty_index = p1 + padd * (capped_family_size - 1)
        share = income / poverty_index
        return p.rate.calc(share, right=True)

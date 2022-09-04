from openfisca_us.model_api import *


class ny_college_tuition_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY college tuition credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (t)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        tuition = add(tax_unit, period, ["qualified_tuition_expenses"])
        p = parameters(period).gov.states.ny.tax.income.credits.college_tuition
        amount = p.rate.calc(tuition) * p.applicable_percentage
        itemizes = tax_unit("ny_itemizes", period)
        return ~itemizes * amount

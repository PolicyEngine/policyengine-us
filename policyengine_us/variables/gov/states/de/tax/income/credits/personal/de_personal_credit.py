from policyengine_us.model_api import *


class de_personal_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware personal credit"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.credits
        exemptions_count = tax_unit("exemptions_count", period)
        return p.personal_credits.personal * exemptions_count

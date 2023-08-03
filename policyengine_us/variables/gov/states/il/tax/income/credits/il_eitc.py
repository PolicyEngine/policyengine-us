from policyengine_us.model_api import *


class il_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www2.illinois.gov/rev/programs/EIC/Pages/default.aspx"

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.il.tax.income.credits.eitc.match
        return eitc * rate

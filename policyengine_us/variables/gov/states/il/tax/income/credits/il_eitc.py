from policyengine_us.model_api import *


class il_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www2.illinois.gov/rev/programs/EIC/Pages/default.aspx"

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        match = parameters(period).gov.states.il.tax.income.credits.eitc.match
        return federal_eitc * match

from policyengine_us.model_api import *


class pa_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania Working Pennsylvanians Tax Credit"
    defined_for = StateCode.PA
    unit = USD
    definition_period = YEAR
    reference = "https://www.palegis.us/legislation/bills/text/PDF/2025/0/HB0416/PN2576#page=50"  # Article XVI-W.2

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.pa.tax.income.credits.eitc
        return federal_eitc * p.match

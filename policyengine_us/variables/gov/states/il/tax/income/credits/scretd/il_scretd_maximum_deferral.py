from policyengine_us.model_api import *


class il_scretd_maximum_deferral(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Senior Citizens Real Estate Tax Deferral maximum annual deferral"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.ilga.gov/legislation/ilcs/documents/032000300K3.htm",
        "https://tax.illinois.gov/research/publications/pio-64.html",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.scretd
        eligible = tax_unit("il_scretd_eligible", period)
        return where(eligible, p.max_annual_deferral, 0)

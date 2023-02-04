from policyengine_us.model_api import *


class ma_wftc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO WFTC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl="
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.mo.tax.income.credits.wftc.eitc_match
        return eitc * rate

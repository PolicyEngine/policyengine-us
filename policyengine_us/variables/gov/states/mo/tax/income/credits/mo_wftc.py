from policyengine_us.model_api import *


class mo_wftc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri Working Families Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl="
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        rate = parameters(period).gov.states.mo.tax.income.credits.wftc.match
        return federal_eitc * rate

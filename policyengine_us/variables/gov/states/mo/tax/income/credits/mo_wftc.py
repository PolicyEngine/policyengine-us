from policyengine_us.model_api import *


class mo_wftc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri Working Families Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl="
    defined_for = StateCode.MO

    def formula_2023(tax_unit, period, parameters):
        federal_eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(
            period
        ).gov.states.mo.tax.income.credits.wftc.eitc_match
        return federal_eitc * rate

from policyengine_us.model_api import *


class vt_low_income_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont low-income child care and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2021.pdf#page=2"
        "https://tax.vermont.gov/coronavirus"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc.low_income
        federal_capped_cdcc = tax_unit("capped_cdcc", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = federal_agi <= p.federal_agi_threshold
        low_income_cdcc = p.rate * federal_capped_cdcc
        return low_income_cdcc * agi_eligible

from policyengine_us.model_api import *


class ri_high_earner_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island high-income surtax"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR
    reference = "https://webserver.rilegislature.gov/BillText/BillText26/HouseText26/H7127Aaa.html#:~:text=High-income%20surtax"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.high_earner_tax
        taxable_income = tax_unit("ri_taxable_income", period)
        taxable_income_above_threshold = max_(
            taxable_income - p.threshold,
            0,
        )
        return taxable_income_above_threshold * p.rate

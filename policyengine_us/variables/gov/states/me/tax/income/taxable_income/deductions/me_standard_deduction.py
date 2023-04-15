from policyengine_us.model_api import *


class me_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_item_stand_%20ded_phaseout_wksht.pdf"
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5124-C.html"
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Get standard deduction part of parameters tree
        p = parameters(period).gov.states.me.tax.income.deductions.standard

        # Get standard deduction for filing status
        return p.amount[filing_status]

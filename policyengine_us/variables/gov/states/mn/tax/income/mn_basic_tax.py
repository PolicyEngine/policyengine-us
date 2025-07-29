from policyengine_us.model_api import *


class mn_basic_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota basic tax calculated using tax rate schedules"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("mn_taxable_income", period)
        p = parameters(period).gov.states.mn.tax.income.rates

        return select_filing_status_value(filing_status, p, taxable_income)

from policyengine_us.model_api import *


class mn_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("mn_taxable_income", period)
        p = parameters(period).gov.states.mn.tax.income.rates
        tax = where(
            filing_status == filing_status.possible_values.JOINT,
            p.joint.calc(taxable_income),
            p.other.calc(taxable_income),
        )
        zero_tax_taxinc = p.zero_tax_threshold[filing_status]
        return where(taxable_income <= zero_tax_taxinc, 0, tax)

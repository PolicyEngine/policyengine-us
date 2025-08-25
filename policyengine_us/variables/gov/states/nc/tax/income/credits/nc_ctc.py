from policyengine_us.model_api import *


class nc_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina credit for children"
    definition_period = YEAR
    unit = USD
    reference = "https://www.ncdor.gov/taxes-forms/individual-income-tax/credit-children"
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        ctc_qualifying_children = tax_unit("ctc_qualifying_children", period)
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.nc.tax.income.credits.ctc
        status = filing_status.possible_values
        credit_amount = select_filing_status_value(
            filing_status,
            p,
            income,
        )
        return ctc_qualifying_children * credit_amount

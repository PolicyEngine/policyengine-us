from policyengine_us.model_api import *


class nc_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina CTC"
    definition_period = YEAR
    unit = USD
    documentation = "North Carolina Tax Credit"
    reference = "https://www.ncdor.gov/taxes-forms/individual-income-tax/credit-children"
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        children = tax_unit("tax_unit_children", period)
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.nc.tax.income.credits.ctc
        status = filing_status.possible_values
        credit_amount = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.JOINT,
            ],
            [
                p.single.calc(income),
                p.head_of_household.calc(income),
                p.married.calc(income),
            ],
        )
        return children * credit_amount

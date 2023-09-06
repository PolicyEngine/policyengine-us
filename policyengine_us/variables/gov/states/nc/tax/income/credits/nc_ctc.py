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
        credit_amount = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.JOINT,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(income),
                p.head_of_household.calc(income),
                p.joint.calc(income),
                p.widow.calc(income),
                p.separate.calc(income),
            ],
        )
        return ctc_qualifying_children * credit_amount

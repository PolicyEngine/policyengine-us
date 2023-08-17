from policyengine_us.model_api import *


class hi_cdcc(Variable):
    value_type = int
    entity = TaxUnit
    label = "Hawaii CDCC"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc

        # if no section B
        qualified_expenses_sum = 100  # line 21(d)??
        exemptions_num = tax_unit("exemptions", period)
        expenses_amount = select(
            [
                exemptions_num == 1,
                exemptions_num > 1,
            ],
            [
                min_(qualified_expenses_sum, 2400),
                min_(qualified_expenses_sum, 4800),
            ],
        )

        earned_income = 100  # line 23

        filing_status = tax_unit(
            "filing_status", period
        )  # line 24: disable? student?
        status = filing_status.possible_values
        joint_income = select(
            [
                filing_status == status.JOINT,
                filing_status != status.JOINT,
            ],
            [
                100,  # spouse income??
                earned_income,
            ],
        )

        income = tax_unit("adjusted_gross_income", period)
        rate = p.rates.calc(income)

        return rate * min_(expenses_amount, earned_income, joint_income)

from policyengine_us.model_api import *


class vt_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        income = tax_unit("vt_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.vt.tax.income.rates
        income_tax = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(income),
                p.joint.calc(income),
                p.separate.calc(income),
                p.widow.calc(income),
                p.head_of_household.calc(income),
            ],
        )
        # If agi is bigger than threshold, than we need to further compare 3% of Adjusted Gross Income less interest from U.S. obligations and Tax Rate Schedule calculation
        federal_agi = tax_unit("adjusted_gross_income", period)
        above_threshold = federal_agi > p.threshold
        us_govt_interest = tax_unit("us_govt_interest", period)
        return where(
            above_threshold,
            max_((p.rate * federal_agi) - us_govt_interest, income_tax),
            income_tax,
        )

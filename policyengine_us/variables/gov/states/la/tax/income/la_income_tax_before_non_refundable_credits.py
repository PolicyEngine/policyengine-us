from policyengine_us.model_api import *


class la_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana income tax before non-refundable credits"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=101946"

    def formula(tax_unit, period, parameters):
        income = tax_unit("la_taxable_income", period)
        p = parameters(period).gov.states.la.tax.income.main
        if p.flat.applies:
            return income * p.flat.rate
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        # The exemption amount is applied to the bottom tax rate and to the top tax rate
        exemptions = tax_unit("la_exemptions", period)
        bottom_tax_rate = p.by_filing_status.single.rates[0]
        exempt_income_tax = exemptions * bottom_tax_rate
        pre_exemption_tax_amount = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.by_filing_status.single.calc(income),
                p.by_filing_status.joint.calc(income),
                p.by_filing_status.separate.calc(income),
                p.by_filing_status.surviving_spouse.calc(income),
                p.by_filing_status.head_of_household.calc(income),
            ],
        )
        return max_(pre_exemption_tax_amount - exempt_income_tax, 0)

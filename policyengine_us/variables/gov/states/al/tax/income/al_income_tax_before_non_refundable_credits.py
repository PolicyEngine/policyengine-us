from policyengine_us.model_api import *


class al_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama income tax before non-refundable credits"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    # The Code of Alabama 1975 Section 40-18-5
    reference = " https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("al_taxable_income", period)
        p = parameters(period).gov.states.al.tax.income.rates

        statuses = filing_status.possible_values

        return select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.SURVIVING_SPOUSE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.surviving_spouse.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
            ],
        )

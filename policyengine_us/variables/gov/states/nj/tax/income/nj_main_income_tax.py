from policyengine_us.model_api import *


class nj_main_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-2-1/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("nj_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        # Get main nj tax parameter tree.
        p = parameters(period).gov.states.nj.tax.income.main

        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
                p.widow.calc(taxable_income),
                p.separate.calc(taxable_income),
            ],
        )

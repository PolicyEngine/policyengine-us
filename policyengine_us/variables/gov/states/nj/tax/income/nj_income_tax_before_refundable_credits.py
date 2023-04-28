from policyengine_us.model_api import *


class nj_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
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
                p.single_separate.calc(taxable_income),
                p.joint_hoh_spouse.calc(taxable_income),
                p.joint_hoh_spouse.calc(taxable_income),
                p.joint_hoh_spouse.calc(taxable_income),
                p.single_separate.calc(taxable_income),
            ],
        )

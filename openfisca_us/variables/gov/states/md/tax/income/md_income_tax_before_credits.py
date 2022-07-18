from openfisca_us.model_api import *


class md_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax before credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        # Get possible values for filing_status
        filing_statuses = filing_status.possible_values
        taxable_income = tax_unit("md_taxable_income", period)
        p = parameters(period).gov.states.md.tax.income.rate_schedule
        single_separate = p.single_separate.calc(taxable_income)
        joint_head_widow = p.joint_head_widow.calc(taxable_income)
        is_single_separate = (filing_status == filing_statuses.SINGLE) | (
            filing_status == filing_statuses.SEPARATE
        )
        return where(is_single_separate, single_separate, joint_head_widow)

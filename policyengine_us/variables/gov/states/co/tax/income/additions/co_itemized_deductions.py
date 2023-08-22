from policyengine_us.model_api import *


class co_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "",
        ""
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.additions.co_itemized_deductions
        agi_eligiblity = tax_unit("adjusted_gross_income", period) > p.agi_threshold
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        limit = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.WIDOW,
            ],
            [
                p.limits.single,
                p.limits.joint,
                p.limits.head_of_household,
                p.limits.separate,
                p.limits.widow,
            ],
        )
        federal_itemized_duction = tax_unit("itemized_taxable_income_deductions", period)
        return max_(0, federal_itemized_duction-limit) * agi_eligiblity
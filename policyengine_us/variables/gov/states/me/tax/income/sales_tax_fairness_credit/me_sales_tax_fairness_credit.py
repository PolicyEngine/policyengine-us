from policyengine_us.model_api import *


class me_sales_tax_fairness_credit(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine sales tax fairness credit"
    definition_period = YEAR
    reference = "https://legislature.maine.gov/statutes/36/title36sec5213-A.html"  # B. 4
    defined_for = "me_sales_tax_fairness_credit"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.sales_tax_fairness
        children = tax_unit("ctc_qualifying_children", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        base = p.amount.base[filing_status]
        additional_amount = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
            ],
            [
                0,
                p.amount.additional.joint.calc(children),
                p.amount.additional.head_of_household.calc(children),
                0,
                p.amount.additional.widow.calc(children),
            ],
        )
        max_credit = base + additional_amount
        reduction_start = p.reduction.start[filing_status]
        increment = p.reduction.increment[filing_status]
        reduction_per_increment = p.reduction.amount[filing_status]
        income = tax_unit("me_property_tax_fairness_credit_income", period)
        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / increment)
        reduction = increments * reduction_per_increment
        return max_(max_credit - reduction, 0)

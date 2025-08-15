from policyengine_us.model_api import *


class me_sales_tax_fairness_credit(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine sales tax fairness credit"
    definition_period = YEAR
    reference = "https://legislature.maine.gov/statutes/36/title36sec5213-A.html"  # B. 4
    defined_for = "me_sales_tax_fairness_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.sales_tax
        children = tax_unit("ctc_qualifying_children", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        base = p.amount.base[filing_status]
        # Create a dictionary for the additional amount parameter structure
        additional_params = {
            "joint": p.amount.additional.joint,
            "head_of_household": p.amount.additional.head_of_household,
            "surviving_spouse": p.amount.additional.surviving_spouse,
            "single": lambda x: 0,  # No additional amount for single filers
            "separate": lambda x: 0,  # No additional amount for separate filers
        }
        additional_amount = select_filing_status_value(
            filing_status, additional_params, children
        )
        max_credit = base + additional_amount
        reduction_start = p.reduction.start[filing_status]
        increment = p.reduction.increment[filing_status]
        reduction_per_increment = p.reduction.amount[filing_status]
        income = tax_unit(
            "me_sales_and_property_tax_fairness_credit_income", period
        )
        excess = max_(income - reduction_start, 0)
        # Increment should never be zero, but if it is, we assume the number
        # of increments is 0 to avoid a divide-by-zero warning.
        increments = np.zeros_like(increment)
        mask = increment != 0
        increments[mask] = np.ceil(excess[mask] / increment[mask])
        reduction = increments * reduction_per_increment
        return max_(max_credit - reduction, 0)

from policyengine_us.model_api import *


class me_sales_and_property_tax_fairness_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine sales and property tax fairness credit total income"
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",  # 1. D.
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",  # 1. B.
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # 36 M.R.S. 5213-A(1)(B) and 5219-KK(1)(D): federal adjusted gross
        # income increased by interest received to the extent not included in
        # it. Federal AGI is the head's and spouse's, so the interest is too: a
        # tax unit dependent's is on the dependent's own return.
        p = parameters(period).gov.states.me.tax.income.credits.fairness
        return tax_unit_non_dep_add(tax_unit, period, p.income_sources)

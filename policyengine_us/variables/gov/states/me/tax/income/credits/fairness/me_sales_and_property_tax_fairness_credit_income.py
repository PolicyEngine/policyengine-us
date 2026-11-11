from policyengine_us.model_api import *


class me_sales_and_property_tax_fairness_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine sales and property tax fairness credit total income"
    documentation = (
        "The filers' income for the sales and property tax fairness credits: "
        "their own income plus their own interest and Social Security left out "
        "of federal adjusted gross income. A tax unit dependent's benefits and "
        "interest are the dependent's own."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",  # 1. D.
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",  # 1. B.
        # Rule 813 .03: "The income of the taxpayer is equal to the
        # taxpayer's federal adjusted gross income increased by" interest and
        # Social Security left out of it.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/Rule_813_May_2023.pdf#page=4",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.fairness
        # Person-level sources are summed over the head and spouse.
        return tax_unit_non_dep_add(tax_unit, period, p.income_sources)

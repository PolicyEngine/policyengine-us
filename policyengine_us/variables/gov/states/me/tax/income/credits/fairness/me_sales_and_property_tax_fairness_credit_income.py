from policyengine_us.model_api import *


class me_sales_and_property_tax_fairness_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine sales and property tax fairness credit total income"
    definition_period = YEAR
    reference = "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html"  # 1. D.
    defined_for = StateCode.ME

    adds = "gov.states.me.tax.income.credits.fairness.income_sources"

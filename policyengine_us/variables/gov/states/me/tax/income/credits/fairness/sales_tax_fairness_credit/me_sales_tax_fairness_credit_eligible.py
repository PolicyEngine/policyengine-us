from policyengine_us.model_api import *


class me_sales_tax_fairness_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Maine sales tax fairness credit"
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html"
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return ~dependent_elsewhere & ~separate

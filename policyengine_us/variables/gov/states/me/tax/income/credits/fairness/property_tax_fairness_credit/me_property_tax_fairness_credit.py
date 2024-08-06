from policyengine_us.model_api import *


class me_property_tax_fairness_credit(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = "me_property_tax_fairness_credit_eligible"
    reference = (
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/23_1040me_sched_pstfc_ff.pdf#page=1",
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",
    )

    def formula(tax_unit, period, parameters):
        property_tax_fairness_credit_cap = tax_unit(
            "me_property_tax_fairness_credit_cap", period
        )
        countable_rent_property_tax = tax_unit(
            "me_property_tax_fairness_credit_countable_rent_property_tax",
            period,
        )
        return min_(
            countable_rent_property_tax, property_tax_fairness_credit_cap
        )

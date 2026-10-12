from policyengine_us.model_api import *


class de_income_tax_before_refundable_credits_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware income tax before refundable credits on the joint path"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=10"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # Joint/combined path: non-refundable credits are pooled at the
        # tax-unit level and applied against the combined pre-credit tax.
        before_credits = tax_unit(
            "de_income_tax_before_non_refundable_credits_unit", period
        )
        non_refundable_credits = tax_unit("de_non_refundable_credits", period)
        return max_(before_credits - non_refundable_credits, 0)

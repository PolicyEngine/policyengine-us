from policyengine_us.model_api import *


class eligible_for_refundable_credits(Variable):
    value_type = bool
    entity = TaxUnit
    label = "eligible for refundable tax credits"
    documentation = """
    Whether this tax unit is eligible for any refundable federal tax credits
    (EITC, refundable CTC, etc.) that would create an incentive to file even
    if not legally required.
    """
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Check if would receive any refundable credits
        # This is a simplified check - the actual credits themselves handle
        # detailed eligibility
        eitc = tax_unit("eitc", period)
        refundable_ctc = tax_unit("refundable_ctc", period)
        return (eitc > 0) | (refundable_ctc > 0)

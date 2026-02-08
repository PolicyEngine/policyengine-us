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
        eitc = tax_unit("eitc", period)
        refundable_ctc = tax_unit("refundable_ctc", period)
        return (eitc + refundable_ctc) > 0

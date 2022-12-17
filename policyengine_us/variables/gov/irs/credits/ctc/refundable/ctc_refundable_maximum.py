from policyengine_us.model_api import *


class ctc_refundable_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum refundable CTC"
    unit = USD
    documentation = "The maximum refundable CTC for this person."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Use either normal or ARPA CTC maximums.
        child_amount = max_(
            person("ctc_child_individual_maximum", period),
            person("ctc_child_individual_maximum_arpa", period),
        )
        ctc = parameters(period).gov.irs.credits.ctc
        if ctc.refundable.fully_refundable:
            # Adult CTC is only refundable if the full credit is.
            adult_amount = person("ctc_adult_individual_maximum", period)
            amount = child_amount + adult_amount
            return tax_unit.sum(amount)
        return tax_unit.sum(min_(child_amount, ctc.refundable.individual_max))

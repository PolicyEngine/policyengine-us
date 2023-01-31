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
        "https://www.irs.gov/pub/irs-prior/f1040--2021.pdf",
        "https://www.irs.gov/pub/irs-prior/f1040s8--2021.pdf",
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
            # Fully refundable CTC does not affect the adult CTC.
            return tax_unit.sum(child_amount)
        return tax_unit.sum(min_(child_amount, ctc.refundable.individual_max))

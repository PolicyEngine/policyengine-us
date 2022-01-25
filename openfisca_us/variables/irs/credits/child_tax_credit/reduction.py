from openfisca_us.model_api import *


class ctc_percent_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC percent reduction"
    documentation = "Used to reduce the CTC adult and child amounts by the same percentage."
    definition_period = YEAR
    unit = PERCENT
    reference = "https://www.law.cornell.edu/uscode/text/26/24#b"

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        agi = tax_unit("adjusted_gross_income", period)
        mars = tax_unit("mars", period)
        excess = max_(0, agi - ctc.phaseout.threshold[mars])
        reduction = excess * ctc.phaseout.rate
        maximum_ctc = add(
            tax_unit, period, ["ctc_child_maximum", "ctc_adult_maximum"]
        )
        uncapped_percentage = where(
            maximum_ctc != 0,
            reduction / where(maximum_ctc == 0, 1, maximum_ctc),
            0,
        )
        return min_(uncapped_percentage, 1)

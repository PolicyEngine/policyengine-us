from openfisca_us.model_api import *


class ctc_child_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC maximum amount (children)"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/24#a"

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        children = tax_unit("ctc_eligible_children", period)
        return ctc.amount.child * children

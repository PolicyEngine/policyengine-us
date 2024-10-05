from policyengine_us.model_api import *


class id_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho Child Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Get relevant parameter subtree.
        p = parameters(period).gov.states.id.tax.income.credits.ctc
        # "the term "qualifying child" has the meaning as defined in section 24(c) of the Internal Revenue Code."
        # IRC 24(c) defines eligible children under the federal CTC.
        eligible_children = tax_unit("ctc_qualifying_children", period)
        # Multiply by the amount per child.
        return eligible_children * p.amount

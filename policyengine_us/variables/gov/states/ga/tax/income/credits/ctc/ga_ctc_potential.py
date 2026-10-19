from policyengine_us.model_api import *


class ga_ctc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia Child Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://legiscan.com/GA/text/HB136/id/3204611/Georgia-2025-HB136-Enrolled.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.credits.ctc
        eligible_children = add(tax_unit, period, ["ga_ctc_eligible_child"])

        return eligible_children * p.amount

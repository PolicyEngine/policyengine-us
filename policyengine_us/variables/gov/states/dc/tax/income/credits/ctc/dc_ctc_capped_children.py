from policyengine_us.model_api import *


class dc_ctc_capped_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Capped number of DC CTC eligible children"
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits.ctc.child
        eligible_children = add(tax_unit, period, ["dc_ctc_eligible_child"])
        return min_(p.child_cap, eligible_children)

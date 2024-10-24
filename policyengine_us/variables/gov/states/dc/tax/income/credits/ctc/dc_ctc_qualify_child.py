from policyengine_us.model_api import *


class dc_ctc_eligible_children_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC CTC eligible children count"
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits.ctc.child
        person = tax_unit.members
        age = person("age", period)
        age_qualify = age < p.age_threshold
        is_dependent = person("is_tax_unit_dependent", period)
        ctc_eligible_children = age_qualify & is_dependent
        return tax_unit.sum(ctc_eligible_children)

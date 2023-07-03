from policyengine_us.model_api import *


class in_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Child-level eligiblity for parents filing Indiana EIC"
    documentation = "Whether a child whose parent filing for Indiana EIC meets the demographic requirements."

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        eligible_children = tax_unit.sum(person("is_child_eligible_eitc", period))
        p = parameters(period).gov.states["in"].tax.icnome.credits
        
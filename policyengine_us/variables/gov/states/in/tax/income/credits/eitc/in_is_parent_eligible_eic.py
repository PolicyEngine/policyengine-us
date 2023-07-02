from policyengine_us.model_api import *


class is_parent_eligible_eic(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Parent-level eligiblity for those filing Indiana EIC"
    documentation = "Whether a parent's income + # of qualifying children meets the requirements for Indiana's EIC."

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.credits.eic
        )
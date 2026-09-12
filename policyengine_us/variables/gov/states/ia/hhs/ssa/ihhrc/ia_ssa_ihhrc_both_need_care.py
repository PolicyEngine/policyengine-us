from policyengine_us.model_api import *


class ia_ssa_ihhrc_both_need_care(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA IHHRC both spouses need in-home health-related care"
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=2"
    )

    def formula(person, period, parameters):
        arrangement_input = person("ia_ssa_living_arrangement_input", period)
        needs_care = (
            arrangement_input
            == arrangement_input.possible_values.IN_HOME_HEALTH_RELATED_CARE
        )
        return person.marital_unit.sum(needs_care) == 2

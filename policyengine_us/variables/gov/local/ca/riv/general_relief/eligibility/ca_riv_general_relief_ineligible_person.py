from policyengine_us.model_api import *


class ca_riv_general_relief_ineligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Ineligible person for the Riverside County General Relief"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(person, period, parameters):
        receives_ssi_or_tanf = (
            add(person.spm_unit, period, ["ssi", "ca_tanf"]) > 0
        )
        immigration_status_eligible = person(
            "ca_riv_general_relief_immigration_status_eligible", period
        )
        meets_work_requirement = person(
            "ca_riv_general_relief_meets_work_requirements", period
        )
        return (
            receives_ssi_or_tanf
            | ~immigration_status_eligible
            | ~meets_work_requirement
        )

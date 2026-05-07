from policyengine_us.model_api import *


class ca_riv_general_relief_ineligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Ineligible person for the Riverside County General Relief"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(person, period, parameters):
        # SSI is person-level: only the individual receiving SSI is excluded
        receives_ssi = person("ssi", period) > 0
        # TANF (CalWORKs) is unit-level: if unit receives TANF, members are excluded
        receives_tanf = person.spm_unit("ca_tanf", period) > 0
        receives_ssi_or_tanf = receives_ssi | receives_tanf
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

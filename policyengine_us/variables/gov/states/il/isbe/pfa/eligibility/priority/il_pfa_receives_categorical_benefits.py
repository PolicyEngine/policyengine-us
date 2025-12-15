from policyengine_us.model_api import *


class il_pfa_receives_categorical_benefits(Variable):
    value_type = bool
    entity = Person
    label = (
        "Child's family receives categorical benefits (risk factor for IL PFA)"
    )
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Check for participation in categorical benefit programs
        # SNAP and TANF are defined at SPM unit level
        snap = person.spm_unit("snap", period) > 0
        tanf = person.spm_unit("tanf", period) > 0
        wic = add(person.spm_unit, period, ["wic"]) > 0
        medicaid = person("is_medicaid_eligible", period)
        return snap | tanf | wic | medicaid

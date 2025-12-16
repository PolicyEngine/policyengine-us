from policyengine_us.model_api import *


class il_pi_receives_categorical_benefits(Variable):
    value_type = bool
    entity = Person
    label = "Family receives categorical benefits (risk factor for IL PI)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/prevention-initiative-manual.pdf"
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        # Check for participation in categorical benefit programs.
        snap = spm_unit("snap", period) > 0
        tanf = spm_unit("tanf", period) > 0
        wic = add(spm_unit, period, ["wic"]) > 0
        medicaid = person("is_medicaid_eligible", period)
        return snap | tanf | wic | medicaid

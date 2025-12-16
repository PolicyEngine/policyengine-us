from policyengine_us.model_api import *


class il_pi_receives_categorical_benefits(Variable):
    value_type = bool
    entity = Person
    label = (
        "Family receives categorical benefits (income verification for IL PI)"
    )
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=1",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        # Public benefits used for income verification per eligibility form:
        # WIC (185% FPL), Medicaid (138% FPL), SNAP (130% FPL), TANF (50% FPL).
        snap = spm_unit("snap", period) > 0
        tanf = spm_unit("tanf", period) > 0
        wic = add(spm_unit, period, ["wic"]) > 0
        medicaid = person("is_medicaid_eligible", period)
        return snap | tanf | wic | medicaid

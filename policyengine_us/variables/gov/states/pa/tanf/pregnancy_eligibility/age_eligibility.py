from policyengine_us.model_api import *


class pa_tanf_age_eligible_on_pregnant_women_limitation(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF age eligibility on pregnant women requirement"
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.pa.tanf.pregnancy_eligibility
        age = person("age", period)
        is_eligible_age = age < p.age_limit
        is_pregnant = person("is_pregnant", period)
        children_number_receiving_tanf = person(
            "children_recieving_tanf_number", period
        )
        is_receiving_tanf_children = children_number_receiving_tanf <= 0
        return spm_unit.any(
            (
                (1 - is_eligible_age)
                * is_pregnant
                * (1 - children_number_receiving_tanf)
            )
            or (is_eligible_age * is_pregnant)
        )

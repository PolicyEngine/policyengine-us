from policyengine_us.model_api import *


class ny_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF grant standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period.this_year)
        capped_people = min_(people, 6).astype(int)
        additional_people = people - capped_people
        p = parameters(period).gov.states.ny.otda.tanf.grant_standard
        base = p.main[capped_people]
        additional_grant_standard = p.additional * additional_people
        return base + additional_grant_standard

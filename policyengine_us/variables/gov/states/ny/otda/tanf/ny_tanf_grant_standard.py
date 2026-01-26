from policyengine_us.model_api import *


class ny_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF grant standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-352.1"
    )

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.ny.otda.tanf
        capped_people = min_(people, p.max_table_size).astype(int)
        additional_people = people - capped_people
        base = p.grant_standard.main[capped_people]
        additional_grant_standard = (
            p.grant_standard.additional * additional_people
        )
        return base + additional_grant_standard

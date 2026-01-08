from policyengine_us.model_api import *


class md_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA maximum benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.17.aspx"

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.md.tanf.maximum_benefit
        capped_people = min_(people, p.max_unit_size).astype(int)
        additional_people = people - capped_people
        base = p.main[capped_people]
        return base + p.additional * additional_people

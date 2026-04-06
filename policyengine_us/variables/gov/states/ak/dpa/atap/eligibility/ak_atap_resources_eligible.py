from policyengine_us.model_api import *


class ak_atap_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alaska ATAP resources eligible"
    definition_period = MONTH
    reference = (
        "https://www.akleg.gov/basis/statutes.asp#47.27.010",
        "https://health.alaska.gov/en/services/alaska-temporary-assistance/",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.atap.resource_limit
        resources = spm_unit("spm_unit_assets", period.this_year)

        # Higher limit if household has elderly member (age 60+)
        person = spm_unit.members
        age = person("age", period.this_year)
        has_elderly = spm_unit.any(age >= p.elderly.age_threshold)

        limit = where(has_elderly, p.elderly.amount, p.standard.amount)
        return resources <= limit

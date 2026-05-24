from policyengine_us.model_api import *


class capped_self_employed_pension_contributions(Variable):
    value_type = float
    entity = Person
    label = "capped self-employed pension contributions"
    unit = USD
    documentation = (
        "Self-employed pension contributions after applying the section "
        "415(c) annual additions limit."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/415#c"

    def formula(person, period, parameters):
        desired = person("self_employed_pension_contributions_desired", period)
        legacy_desired = person("self_employed_pension_contributions", period)
        contributions = where(desired > 0, desired, legacy_desired)
        limit = person("self_employed_pension_contribution_limit", period)
        return min_(contributions, limit)

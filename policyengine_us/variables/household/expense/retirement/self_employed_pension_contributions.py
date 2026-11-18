from policyengine_us.model_api import *


class self_employed_pension_contributions(Variable):
    value_type = float
    entity = Person
    label = "Self-employed pension contributions"
    unit = USD
    documentation = (
        "Self-employed SEP, SIMPLE and qualified plan contributions after "
        "applying the Pub. 560 maximum deductible contribution, which "
        "includes the section 415(c) annual additions limit."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/415#c",
        "https://www.law.cornell.edu/uscode/text/26/404#a_8_C",
    )

    def formula(person, period, parameters):
        contributions = person("self_employed_pension_contributions_desired", period)
        limit = person("self_employed_pension_contribution_limit", period)
        return min_(contributions, limit)

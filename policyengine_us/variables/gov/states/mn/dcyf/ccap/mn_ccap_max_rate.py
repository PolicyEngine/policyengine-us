from policyengine_us.model_api import *


class mn_ccap_max_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = (
        "Minnesota CCAP maximum monthly rate per child including quality differential"
    )
    definition_period = MONTH
    defined_for = "mn_ccap_eligible_child"
    reference = (
        # Minn. Stat. 142E.17 subd. 1, 4-5 — maximum rates and quality
        # differentials.
        "https://www.revisor.mn.gov/statutes/cite/142E.17",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.ccap
        provider_rate = person("mn_ccap_provider_rate", period)
        quality_rating = person("mn_ccap_quality_rating", period)
        # Higher-quality providers receive a 15% or 20% differential above the
        # standard maximum rate. The differential is capped at the provider's
        # actual charge downstream, where the benefit is capped at the family's
        # pre-subsidy child care expenses.
        differential = p.quality_differential[quality_rating]
        return provider_rate * (1 + differential)

from policyengine_us.model_api import *


class md_paa_provider_rate(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA provider rate"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Action%20Transmittals-AT%20-%20Information%20Memo-IM/AT-IM2023/23-02%20AT%20-%20COLA%20Mass%20Mod%20FFY23.pdf#page=3",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-09",
    )

    def formula(person, period, parameters):
        living_arrangement = person("md_paa_living_arrangement", period)
        return parameters(period).gov.states.md.dhs.fia.paa.provider_rate[
            living_arrangement
        ]

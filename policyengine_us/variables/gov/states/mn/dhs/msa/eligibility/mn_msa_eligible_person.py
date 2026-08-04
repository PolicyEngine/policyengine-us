from policyengine_us.model_api import *


class mn_msa_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Minnesota Supplemental Aid"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 1: aged 65+, blind, or 18+ with a
        # disability; resource/gross/net income tests; MN resident; citizen
        # or qualified noncitizen; in a qualifying living arrangement.
        age = person("age", period.this_year)
        aged = person("is_ssi_aged", period.this_year)
        blind = person("is_blind", period.this_year)
        disabled_adult = (age >= 18) & person("is_ssi_disabled", period.this_year)
        arrangement = person("mn_msa_payment_category", period)
        return (
            (arrangement != arrangement.possible_values.NONE)
            & (aged | blind | disabled_adult)
            & person("mn_msa_resource_eligible", period)
            & person("mn_msa_gross_income_eligible", period)
            & person("mn_msa_net_income_eligible", period)
            & person("is_citizen_or_legal_immigrant", period.this_year)
        )

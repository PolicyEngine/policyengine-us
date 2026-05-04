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
        # Per Minn. Stat. § 256D.44 Subd. 1, MSA recipients must be
        # categorically aged/blind/disabled, meet the resource and
        # gross/net income tests, and reside in Minnesota with a
        # qualifying immigration status (citizen or qualified noncitizen).
        arrangement = person("mn_msa_payment_category", period)
        qualifies_arrangement = arrangement != arrangement.possible_values.NONE
        age = person("age", period.this_year)
        aged = person("is_ssi_aged", period.this_year)
        blind = person("is_blind", period.this_year)
        disabled_adult = (age >= 18) & person("is_ssi_disabled", period.this_year)
        categorically_eligible = aged | blind | disabled_adult
        resource_eligible = person("mn_msa_resource_eligible", period)
        gross_income_eligible = person("mn_msa_gross_income_eligible", period)
        net_income_eligible = person("mn_msa_net_income_eligible", period)
        meets_immigration = person("is_citizen_or_legal_immigrant", period.this_year)
        return (
            qualifies_arrangement
            & categorically_eligible
            & resource_eligible
            & gross_income_eligible
            & net_income_eligible
            & meets_immigration
        )

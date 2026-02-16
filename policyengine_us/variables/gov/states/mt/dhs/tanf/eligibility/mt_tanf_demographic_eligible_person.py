from policyengine_us.model_api import *


class mt_tanf_demographic_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Montana Temporary Assistance for Needy Families (TANF) based on demographics"
    reference = (
        "https://dphhs.mt.gov/HCSD/tanf",
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.206",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        tanf_eligible_child = person("mt_tanf_eligible_child", period)
        related_to_head_or_spouse = person(
            "is_related_to_head_or_spouse", period.this_year
        )
        pregnant = person("is_pregnant", period.this_year)
        immigration_status_eligible = person(
            "mt_tanf_immigration_status_eligible_person", period
        )

        return (tanf_eligible_child & related_to_head_or_spouse) | (
            pregnant & immigration_status_eligible
        )

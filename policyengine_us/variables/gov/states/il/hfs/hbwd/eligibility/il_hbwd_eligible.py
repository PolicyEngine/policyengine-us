from policyengine_us.model_api import *


class il_hbwd_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
        "https://hfs.illinois.gov/medicalprograms/hbwd.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        age_eligible = person("il_hbwd_age_eligible", period)
        disability_eligible = person("il_hbwd_disability_eligible", period)
        employment_eligible = person("il_hbwd_employment_eligible", period)
        income_eligible = person("il_hbwd_income_eligible", period)
        asset_eligible = person("il_hbwd_asset_eligible", period)
        immigration_eligible = person(
            "il_hfs_immigration_status_eligible", period
        )

        return (
            age_eligible
            & disability_eligible
            & employment_eligible
            & income_eligible
            & asset_eligible
            & immigration_eligible
        )

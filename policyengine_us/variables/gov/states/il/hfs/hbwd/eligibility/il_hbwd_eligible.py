from policyengine_us.model_api import *


class il_hbwd_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities eligible"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
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
            "il_hbwd_immigration_status_eligible", period
        )

        return (
            age_eligible
            & disability_eligible
            & employment_eligible
            & income_eligible
            & asset_eligible
            & immigration_eligible
        )

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
        "https://www.law.cornell.edu/cfr/text/42/435.121",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        age_eligible = person("il_hbwd_age_eligible", period)
        disability_eligible = person("il_hbwd_disability_eligible", period)
        employment_eligible = person("il_hbwd_employment_eligible", period)
        income_eligible = person("il_hbwd_income_eligible", period)
        asset_eligible = person("il_hbwd_asset_eligible", period)
        immigration_eligible = person("il_hfs_immigration_status_eligible", period)
        # 89 Ill. Adm. Code 120.510(b) bars a person who is otherwise eligible for
        # medical assistance without a spenddown. Under 120.510(c) a person
        # eligible only with a spenddown may still choose this program, so
        # medically needy coverage does not count. Nor does the SSI recipient
        # group for a person it covers only after a spenddown (42 CFR
        # 435.121(e)(5)), so an SSI recipient counts only with income within
        # the limit before any spenddown.
        year = period.this_year
        categories = parameters(period).gov.hhs.medicaid.eligibility.categories.covered
        without_spenddown = [
            category
            for category in categories
            if category
            not in (
                "is_medically_needy_for_medicaid",
                "is_ssi_recipient_for_medicaid",
                "is_working_disabled_buy_in_for_medicaid",
            )
        ]
        ssi_recipient_without_spenddown = (
            ("is_ssi_recipient_for_medicaid" in categories)
            & person("is_ssi_recipient_for_medicaid", year)
            & person("is_optional_senior_or_disabled_income_eligible", year)
        )
        otherwise_eligible = (
            (add(person, year, without_spenddown) > 0) | ssi_recipient_without_spenddown
        ) & person("is_medicaid_immigration_status_eligible", year)

        return (
            age_eligible
            & disability_eligible
            & employment_eligible
            & income_eligible
            & asset_eligible
            & immigration_eligible
            & ~otherwise_eligible
        )

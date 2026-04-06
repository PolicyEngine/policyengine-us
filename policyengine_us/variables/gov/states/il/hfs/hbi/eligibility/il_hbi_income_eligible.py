from policyengine_us.model_api import *


class il_hbi_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Illinois Health Benefits for Immigrants income eligibility"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html",
        "https://www.dhs.state.il.us/page.aspx?item=161600",
        "https://hfs.illinois.gov/medicalprograms/allkids/about.html",
    )
    # Illinois HBI has different income limits and methodologies by age group:
    # - Children (0-18): Up to 318% FPL (All Kids, uses MAGI)
    # - Adults (42-64): Up to 138% FPL (HBIA, uses MAGI)
    # - Seniors (65+): Up to 100% FPL (HBIS, uses AABD methodology)
    #
    # Per Illinois DHS, HBIS follows AABD community eligibility criteria
    # for income counting, which differs from MAGI.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbi.eligibility

        age = person("age", period)

        # Age thresholds
        is_child = age <= p.child.max_age
        is_adult = (age >= p.adult.min_age) & (age <= p.adult.max_age)
        is_senior = age >= p.senior.min_age

        # Get appropriate income level based on age group
        # Children and adults use MAGI, seniors use AABD methodology
        magi_income_level = person("medicaid_income_level", period)
        aabd_income_level = person("il_hbi_senior_income_level", period)

        income_level = where(is_senior, aabd_income_level, magi_income_level)

        # Select appropriate income limit based on age
        income_limit = select(
            [is_child, is_adult, is_senior],
            [
                p.child.income_limit,
                p.adult.income_limit,
                p.senior.income_limit,
            ],
            default=0,  # Ages 19-41 not covered
        )

        return income_level <= income_limit

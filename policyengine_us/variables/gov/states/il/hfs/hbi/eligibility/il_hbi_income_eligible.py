from policyengine_us.model_api import *


class il_hbi_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Illinois Health Benefits for Immigrants income eligibility"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = [
        "https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html",
        "https://www.dhs.state.il.us/page.aspx?item=161600",
        "https://hfs.illinois.gov/medicalprograms/allkids/about.html",
    ]
    documentation = """
    Illinois HBI has different income limits based on age group:
    - Children (0-18): Up to 318% FPL (All Kids)
    - Adults (42-64): Up to 138% FPL (HBIA, uses MAGI)
    - Seniors (65+): Up to 100% FPL (HBIS)
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbi.eligibility

        income_level = person("medicaid_income_level", period)
        age = person("age", period)

        # Age thresholds
        child_max_age = p.child_max_age
        adult_min_age = p.adult_min_age
        adult_max_age = p.adult_max_age
        senior_min_age = p.senior_min_age

        # Determine age category
        is_child = age <= child_max_age
        is_adult = (age >= adult_min_age) & (age <= adult_max_age)
        is_senior = age >= senior_min_age

        # Income limits by age group
        child_limit = p.child_income_limit
        adult_limit = p.adult_income_limit
        senior_limit = p.senior_income_limit

        # Select appropriate income limit based on age
        income_limit = select(
            [is_child, is_adult, is_senior],
            [child_limit, adult_limit, senior_limit],
            default=0,  # Ages 19-41 not covered
        )

        return income_level <= income_limit

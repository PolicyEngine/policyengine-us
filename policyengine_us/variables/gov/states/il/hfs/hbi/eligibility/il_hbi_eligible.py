from policyengine_us.model_api import *


class il_hbi_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Illinois Health Benefits for Immigrants"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html",
        "https://www.dhs.state.il.us/page.aspx?item=161600",
        "https://hfs.illinois.gov/medicalprograms/allkids/about.html",
    )
    # Illinois Health Benefits for Immigrants (HBI) is a state-funded program
    # providing health coverage to income-eligible residents who are not eligible
    # for federal Medicaid due to their immigration status.
    #
    # The program includes three components:
    # - All Kids: Children 0-18 up to 318% FPL
    # - HBIA (Health Benefits for Immigrant Adults): Ages 42-64 up to 138% FPL
    # - HBIS (Health Benefits for Immigrant Seniors): Ages 65+ up to 100% FPL
    #
    # Note: Ages 19-41 are not covered.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbi.eligibility

        # Check base eligibility criteria
        immigration_eligible = person(
            "il_hbi_immigration_status_eligible", period
        )
        age_eligible = person("il_hbi_age_eligible", period)
        income_eligible = person("il_hbi_income_eligible", period)
        resource_eligible = person("il_hbi_resource_eligible", period)

        # Determine age group for program-specific in_effect checks
        age = person("age", period)
        is_child = age <= p.child.max_age
        is_adult = (age >= p.adult.min_age) & (age <= p.adult.max_age)
        is_senior = age >= p.senior.min_age

        # Check if the relevant program is in effect for each age group
        child_in_effect = p.child.in_effect
        adult_in_effect = p.adult.in_effect
        senior_in_effect = p.senior.in_effect

        program_in_effect = (
            (is_child & child_in_effect)
            | (is_adult & adult_in_effect)
            | (is_senior & senior_in_effect)
        )

        return (
            immigration_eligible
            & age_eligible
            & income_eligible
            & resource_eligible
            & program_in_effect
        )

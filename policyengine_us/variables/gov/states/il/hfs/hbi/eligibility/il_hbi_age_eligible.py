from policyengine_us.model_api import *


class il_hbi_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Illinois Health Benefits for Immigrants age eligibility"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html",
        "https://www.dhs.state.il.us/page.aspx?item=161600",
        "https://hfs.illinois.gov/medicalprograms/allkids/about.html",
    )
    # Illinois HBI covers specific age groups:
    # - Children: 0-18 (All Kids)
    # - Adults: 42-64 (HBIA)
    # - Seniors: 65+ (HBIS)
    #
    # Note: Ages 19-41 are NOT covered by any Illinois immigrant health program.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbi.eligibility

        age = person("age", period)

        # Determine if in a covered age group
        is_child = age <= p.child.max_age
        is_adult = (age >= p.adult.min_age) & (age <= p.adult.max_age)
        is_senior = age >= p.senior.min_age

        return is_child | is_adult | is_senior

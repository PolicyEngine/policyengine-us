from policyengine_us.model_api import *


class NMCCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class nm_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = NMCCAPAgeGroup
    default_value = NMCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "New Mexico CCAP child age group"
    defined_for = StateCode.NM
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
        "https://www.srca.nm.gov/parts/title08/08.009.0003.html",
        # PDF pages 3, 18
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/b0e207a9-a1a3-412d-9660-0a6e925f6f25/8.9.3.pdf#page=3",
    )

    def formula(person, period, parameters):
        # age is a YEAR variable; convert to months to look up the age group.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.nm.ececd.ccap.rates.age_group
        return p.months.calc(age_in_months)

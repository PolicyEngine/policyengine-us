from policyengine_us.model_api import *


class is_adult_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid adult non-financial criteria"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.119",
        "https://www.law.cornell.edu/uscode/text/42/1396a#a_10_A_i_VIII",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1865-000-00/1865-020-00/",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.adult
        age = person("age", period)
        age_eligible = ma.age_range.calc(age)
        # 42 CFR 435.119(b) limits the adult group to people not entitled to
        # or enrolled in Medicare Part A or B.
        medicare_enrolled = person("is_medicare_eligible", period)
        # SSI recipients are covered through mandatory non-MAGI pathways
        # instead (42 CFR 435.120); in 209(b) states such as Missouri, the
        # adult group applies an explicit SSI-receipt exclusion.
        receives_ssi = (person("ssi", period) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )
        return age_eligible & ~medicare_enrolled & ~receives_ssi

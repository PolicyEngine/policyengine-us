from policyengine_us.model_api import *


class ut_personal_exemption_additional_dependent_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Utah additional dependent personal exemption eligible"
    defined_for = StateCode.UT
    definition_period = YEAR
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html"  # 59-10-1018 (1)(g)

    def formula(person, period, parameters):
        # 59-10-1018(1)(g) adds "an additional qualifying dependent in the
        # year of a qualifying dependent's birth", so the newborn must be a
        # qualifying dependent: one for whom the claimant is allowed an IRC 24
        # credit, which a return on which a filer can be claimed as a
        # dependent has none of (IRC 152(b)(1)) outside the filing exception.
        qualifying_dependent = person("ut_qualifying_dependent", period)
        birth_year = person("birth_year", period)
        born_this_year = birth_year == period.start.year
        return qualifying_dependent & born_this_year

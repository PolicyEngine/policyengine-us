from policyengine_us.model_api import *


class KSCCAPRelativeAgeGroup(Enum):
    UNDER_18_MONTHS = "18 months and less"
    OVER_18_MONTHS = "Over 18 months"


class ks_ccap_relative_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = KSCCAPRelativeAgeGroup
    default_value = KSCCAPRelativeAgeGroup.OVER_18_MONTHS
    definition_period = MONTH
    label = "Kansas CCAP out-of-home relative age group"
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/appendix/c-18_providerratecht.pdf#page=8"
    )

    def formula(person, period, parameters):
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.ks.dcf.ccap.age_group
        return p.relative_months.calc(age_in_months)

from policyengine_us.model_api import *


class KSCCAPHomeAgeGroup(Enum):
    GROUP_0_17 = "0-17 months"
    GROUP_18_35 = "18-35 months"
    GROUP_36_59 = "36-59 months"
    GROUP_60_PLUS = "60 months and older"


class ks_ccap_home_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = KSCCAPHomeAgeGroup
    default_value = KSCCAPHomeAgeGroup.GROUP_60_PLUS
    definition_period = MONTH
    label = "Kansas CCAP licensed home age group"
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/appendix/c-18_providerratecht.pdf#page=8"
    )

    def formula(person, period, parameters):
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.ks.dcf.ccap.age_group
        return p.home_months.calc(age_in_months)

from policyengine_us.model_api import *


class NVCCDPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class nv_ccdp_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = NVCCDPAgeGroup
    default_value = NVCCDPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Nevada CCDP child age group"
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/ACF-118_CCDF_FFY_2025-2027_For_Nevada__3.pdf#page=54"

    def formula(person, period, parameters):
        # `monthly_age` reverses PolicyEngine's auto-division by 12, so it
        # returns age in YEARS; use the explicit age-in-months form instead.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.nv.dwss.ccdp.age_group
        # The months scale returns the integer index 0=INFANT, 1=TODDLER,
        # 2=PRESCHOOL, 3=SCHOOL_AGE, which maps directly onto the enum order.
        return p.months.calc(age_in_months)

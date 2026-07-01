from policyengine_us.model_api import *


class MTCCAPAgeGroup(Enum):
    INFANT_TODDLER = "Infant/Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class mt_ccap_child_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = MTCCAPAgeGroup
    default_value = MTCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    defined_for = StateCode.MT
    label = "Montana Best Beginnings Child Care Scholarship child age category"
    reference = "https://dphhs.mt.gov/assets/ecfsd/childcare/documentsandresources/BBSProviderRatesMonthly.pdf"

    def formula(person, period, parameters):
        # The published rate table lists three age groups but states no month
        # cutoffs. The Infant/Toddler cutoff (36mo) is a documented assumption;
        # the Preschool/School-Age cutoff (72mo) follows ARM 37.80.102, which
        # defines a school-age child as six years and older. See age_group/months.yaml:
        # 0-35mo Infant/Toddler, 36-71mo Preschool, 72mo+ School Age.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.mt.dphhs.ccap.age_group
        return p.months.calc(age_in_months)

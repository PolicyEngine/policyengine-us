from policyengine_us.model_api import *


class OHCCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School-Age"
    SCHOOL_AGE_SUMMER = "School-Age Summer"


class oh_ccap_child_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = OHCCAPAgeGroup
    default_value = OHCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Ohio CCAP child age group"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-01"

    def formula(person, period, parameters):
        # 5180:2-16-01: Infant under 18 months, Toddler 18 months to under
        # 3 years, Preschool 3 years to not school-age, School-age enrolled in
        # kindergarten or above. The months bracket maps age to the four base
        # groups (0=Infant, 1=Toddler, 2=Preschool, 3=School-Age); the
        # School-Age vs School-Age Summer split is applied below.
        p = parameters(period).gov.states.oh.dcy.ccap.age_group
        # age is a YEAR variable; multiply by MONTHS_IN_YEAR for month
        # thresholds (monthly_age returns years, not months).
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        base_group = p.months.calc(age_in_months)
        # 5180:2-16-01(Z): the school year runs the first Sunday in September
        # through the last Saturday in May. We approximate the non-school-year
        # window with the summer months June through August (parameterized);
        # school-age children outside the school year use the summer rate.
        month = period.start.month
        is_summer = (month >= p.school_age_summer.start_month) & (
            month <= p.school_age_summer.end_month
        )
        is_school_age = base_group == OHCCAPAgeGroup.SCHOOL_AGE.index
        return select(
            [
                base_group == OHCCAPAgeGroup.INFANT.index,
                base_group == OHCCAPAgeGroup.TODDLER.index,
                base_group == OHCCAPAgeGroup.PRESCHOOL.index,
                is_school_age & is_summer,
                is_school_age,
            ],
            [
                OHCCAPAgeGroup.INFANT,
                OHCCAPAgeGroup.TODDLER,
                OHCCAPAgeGroup.PRESCHOOL,
                OHCCAPAgeGroup.SCHOOL_AGE_SUMMER,
                OHCCAPAgeGroup.SCHOOL_AGE,
            ],
            default=OHCCAPAgeGroup.PRESCHOOL,
        )

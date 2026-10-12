from policyengine_us.model_api import *


class ORERDCAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL = "School"
    SPECIAL_NEEDS = "Special needs"


class or_erdc_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = ORERDCAgeGroup
    default_value = ORERDCAgeGroup.SCHOOL
    definition_period = MONTH
    label = "Oregon ERDC child age group"
    defined_for = "or_erdc_eligible_child"
    reference = "https://www.oregon.gov/delc/providers/Documents/Provider%20Rate%20Increase%20For%20Jan%202026_Phase%202_ENG.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].delc.erdc.age_group
        provider_type = person("or_erdc_provider_type", period)
        types = provider_type.possible_values
        # The Provider Guide Insert grants the infant window of 6 weeks through
        # 23 months only to "Registered or Certified Family care" (RFM, CFM);
        # it states no infant boundary for certified centers (CNT). We apply
        # the same 24-month cutoff to CNT pending DELC confirmation (a ~$96/mo
        # difference for children aged 12-23 months at certified centers).
        licensed = (
            (provider_type == types.REGISTERED_FAMILY)
            | (provider_type == types.CERTIFIED_FAMILY)
            | (provider_type == types.CERTIFIED_CENTER)
        )
        infant_max_months = where(
            licensed,
            p.licensed_infant_max_months,
            p.license_exempt_infant_max_months,
        )
        age = person("age", period.this_year)
        age_months = age * MONTHS_IN_YEAR
        # OAR 414-175-0024(1)(b) grants the special needs rate on request
        # with a verified disability; we proxy that determination with
        # disability status.
        special_needs = person("is_disabled", period.this_year)
        return select(
            [
                special_needs,
                age_months < infant_max_months,
                age_months < p.toddler_max_months,
                age < p.preschool_max_years,
                age >= p.preschool_max_years,
            ],
            [
                ORERDCAgeGroup.SPECIAL_NEEDS,
                ORERDCAgeGroup.INFANT,
                ORERDCAgeGroup.TODDLER,
                ORERDCAgeGroup.PRESCHOOL,
                ORERDCAgeGroup.SCHOOL,
            ],
            default=ORERDCAgeGroup.SCHOOL,
        )

from policyengine_us.model_api import *


class hi_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Hawaii CCAP"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=14"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.age
        age = person("age", period.this_year)
        # Under 13 (HAR 17-798.2-9(a)(1)).
        under_age_limit = age < p.child_limit
        # 13 through 17 with a physical or mental incapacity preventing
        # self-care (HAR 17-798.2-9(a)(2)). The disabled-child threshold is
        # inclusive (up through 17), so use <=.
        is_disabled = person("is_disabled", period.this_year)
        disabled_eligible = (
            is_disabled & (age >= p.child_limit) & (age <= p.disabled_child_limit)
        )
        # HAR 17-798.2-9(a)(3): a child receiving child protective services
        # whose court-ordered family case plan specifies child care. The case
        # plan's child-care content is treated as a verification detail, so
        # court supervision stands in for the court order. HAR 17-798.2-2
        # defines a child as a person under 18.
        protective_services = person(
            "receives_or_needs_protective_services", period.this_year
        )
        court_supervision = person("is_under_court_supervision", period.this_year)
        protective_care = (
            protective_services & court_supervision & (age < p.protective_child_limit)
        )
        age_eligible = under_age_limit | disabled_eligible | protective_care
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible

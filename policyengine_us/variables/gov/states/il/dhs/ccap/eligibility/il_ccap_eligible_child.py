from policyengine_us.model_api import *


class il_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Illinois Child Care Assistance Program (CCAP)"
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/policies/ACF-118%20CCDF%20FFY%202025-2027%20For%20Illinois%20Amend%202.pdf#page=18",
        "https://www.dhs.state.il.us/page.aspx?item=104995",
        "https://www.dhs.state.il.us/page.aspx?item=46885",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.age_limit
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # The approved FFY 2025-2027 plan, section 2.2.1(c), elects the
        # 45 CFR 98.20(a)(1)(ii) court-supervision extension through age 18.
        court_supervision = person("is_under_court_supervision", period.this_year)
        age_limit = where(
            is_disabled | court_supervision, p.special_needs_child, p.child
        )
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        # Citizenship and immigration status are not eligibility factors.
        # Under IDHS CCAP Policy 01.01.03, "Eligibility will not be denied
        # based on a child's citizenship status" and the parent's status
        # "cannot be considered"; Illinois pays for non-qualified-alien
        # children with State dollars instead of federal CCDF funds.
        return age_eligible & is_dependent

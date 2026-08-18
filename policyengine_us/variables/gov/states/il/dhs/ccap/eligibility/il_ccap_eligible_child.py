from policyengine_us.model_api import *


class il_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Illinois Child Care Assistance Program (CCAP)"
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=104995",
        "https://www.dhs.state.il.us/page.aspx?item=46885",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.age_limit
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.special_needs_child, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        # Citizenship and immigration status are not eligibility factors.
        # Under IDHS CCAP Policy 01.01.03, "Eligibility will not be denied
        # based on a child's citizenship status" and the parent's status
        # "cannot be considered"; Illinois pays for non-qualified-alien
        # children with State dollars instead of federal CCDF funds.
        return age_eligible & is_dependent

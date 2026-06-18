from policyengine_us.model_api import *


class mo_ccs_protective_services(Variable):
    value_type = bool
    entity = Person
    label = "Missouri Child Care Subsidy protective services category"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-050"

    def formula(person, period, parameters):
        # 5 CSR 25-200.060(7)(A) lists the protective-services categories —
        # children in DSS legal custody (proxied by foster care) and children
        # receiving or needing protective services; (7)(B) is what exempts those
        # categories from the income maximums and the financial-need test.
        # Homelessness is not a (7)(A) category; it is a separate valid need for
        # care (Manual sec. 6.8), so it is handled in mo_ccs_activity_eligible
        # and is still subject to the income test.
        is_foster = person("is_in_foster_care", period)
        needs_protective = person(
            "receives_or_needs_protective_services", period.this_year
        )
        return is_foster | needs_protective

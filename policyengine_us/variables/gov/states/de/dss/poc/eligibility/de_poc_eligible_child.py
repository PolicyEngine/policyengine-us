from policyengine_us.model_api import *


class de_poc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Delaware Purchase of Care"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = (
        "https://regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/11003.shtml",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=14",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.dss.poc.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_eligible = where(is_disabled, age < p.disabled_child, age < p.child)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        standard_eligible = age_eligible & is_dependent & immigration_eligible
        # Foster care, protective services (DFS referral), and homeless
        # children are eligible regardless of dependency or immigration
        # status (DSSM 11003.7).
        foster = person("is_in_foster_care", period)
        protective = person("receives_or_needs_protective_services", period)
        homeless = person.household("is_homeless", period.this_year)
        categorical_eligible = age_eligible & (foster | protective | homeless)
        return standard_eligible | categorical_eligible

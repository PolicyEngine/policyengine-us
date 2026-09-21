from policyengine_us.model_api import *


class de_poc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Delaware Purchase of Care"
    definition_period = MONTH
    defined_for = StateCode.DE
    reference = (
        "https://dhss.delaware.gov/wp-content/uploads/sites/2/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=79",
        "https://dhss.delaware.gov/wp-content/uploads/sites/2/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=14",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.dss.poc
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # The approved FFY 2025-2027 plan, section 2.2.1(c), elects the
        # 45 CFR 98.20(a)(1)(ii) court-supervision age extension through 18.
        # Ordinary income, activity and copay rules still apply.
        court_supervision = (
            person("is_under_court_supervision", period.this_year)
            & p.eligibility.court_supervision_extension
        )
        age_eligible = where(
            is_disabled | court_supervision,
            age < p.age_threshold.disabled_child,
            age < p.age_threshold.child,
        )
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
        referral = person("de_poc_has_dfs_referral", period)
        # A DFS child-care referral is a separate under-19 route that does
        # not depend on the court-supervision election, dependency or
        # immigration status.
        referred_eligible = referral & (age < p.age_threshold.disabled_child)
        return standard_eligible | categorical_eligible | referred_eligible

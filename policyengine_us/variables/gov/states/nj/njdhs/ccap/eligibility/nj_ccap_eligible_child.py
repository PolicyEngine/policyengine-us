from policyengine_us.model_api import *


class nj_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for New Jersey CCAP"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-15-5-2",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=20",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # The approved FFY 2025-2027 plan, section 2.2.1(c), elects the
        # 45 CFR 98.20(a)(1)(ii) court-supervision age extension through 18;
        # N.J.A.C. 10:15-1.3(a) lists only the under-13 and under-19 disabled
        # definitions. Ordinary income, activity and copay rules still apply.
        court_supervision = (
            person("is_under_court_supervision", period.this_year)
            & p.eligibility.court_supervision_extension
        )
        age_eligible = where(
            is_disabled | court_supervision,
            age < p.age_threshold.special_needs,
            age < p.age_threshold.child,
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        standard_eligible = age_eligible & is_dependent & immigration_eligible
        # CP&P (Child Protective & Permanency) children are eligible
        # regardless of dependency or immigration status.
        protective = person("receives_or_needs_protective_services", period)
        foster = person("is_in_foster_care", period)
        categorical_eligible = age_eligible & (protective | foster)
        referral = person("nj_ccap_has_cpp_referral", period)
        # A CP&P child-care referral is a separate under-19 route that does
        # not depend on the court-supervision election, dependency or
        # immigration status.
        referred_eligible = referral & (age < p.age_threshold.special_needs)
        return standard_eligible | categorical_eligible | referred_eligible

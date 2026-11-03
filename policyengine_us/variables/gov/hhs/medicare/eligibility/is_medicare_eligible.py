from policyengine_us.model_api import *


class is_medicare_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for Medicare"
    definition_period = YEAR
    documentation = (
        "CMS, Original Medicare (Part A and B) Eligibility and Enrollment\n"
        "https://www.cms.gov/medicare/enrollment-renewal/health-plans/original-part-a-b\n"
        "Above link includes the following text:\n"
        "  Part A coverage begins the month the individual turns age 65\n"
        "Only the age-65 and 24-month SSDI routes are modeled. The immediate "
        "entitlement routes for ALS (42 U.S.C. 426(h)) and ESRD "
        "(42 U.S.C. 426-1) are not, as the model has no inputs for those "
        "conditions. Everyone is treated as grandfathered under "
        "42 U.S.C. 1395mmm(b)(1) through 2026, as the model has no input for "
        "enrollment on July 4, 2025."
    )
    reference = (
        "https://www.cms.gov/medicare/enrollment-renewal/health-plans/original-part-a-b",
        "https://www.law.cornell.edu/uscode/text/42/1395o#a",
        "https://www.law.cornell.edu/uscode/text/8/1611#b_3",
        "https://www.law.cornell.edu/uscode/text/42/1395mmm",
        # PDF pages 249-250
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=249",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.eligibility
        is_age_eligible = person("age", period) >= p.min_age
        gets_ssdi = person("social_security_disability", period) > 0
        months = person("months_receiving_social_security_disability", period)
        is_disability_eligible = gets_ssdi & (
            months >= p.min_months_receiving_social_security_disability
        )
        status = person("immigration_status", period)
        statuses = status.possible_values
        # 42 U.S.C. 1395mmm(a) limits Medicare to the statuses listed from 2027, with
        # everyone treated as grandfathered under 1395mmm(b)(1) until then. The earlier
        # list follows 8 U.S.C. 1611(b)(3), which requires lawful presence.
        allowed = np.isin(status.decode_to_str(), p.immigration_statuses)
        # 42 U.S.C. 1395o(a)(2): at 65, a person without Part A may enroll in
        # Part B only as a citizen or a permanent resident of five years.
        is_long_term_resident = (status == statuses.LEGAL_PERMANENT_RESIDENT) & (
            person("years_since_us_entry", period) >= p.permanent_resident_years
        )
        # 42 U.S.C. 1395o(a)(1): entitlement to Part A opens Part B to anyone else
        # with an allowed status. Quarters stand in for entitlement on the person's
        # own or a spouse's record (42 U.S.C. 426(a)). The limit in 8 U.S.C. 1611(b)(3)
        # to wages from authorized employment isn't modeled.
        has_part_a_work_history = (
            person("medicare_quarters_of_coverage", period)
            >= parameters(
                period
            ).gov.hhs.medicare.part_a.premium_free_quarters_threshold
        )
        can_enroll_at_age = (
            (status == statuses.CITIZEN)
            | is_long_term_resident
            | (allowed & has_part_a_work_history)
        )
        return (is_age_eligible & can_enroll_at_age) | (
            is_disability_eligible & allowed
        )

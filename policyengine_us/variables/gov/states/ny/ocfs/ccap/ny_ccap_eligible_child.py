from policyengine_us.model_api import *


class ny_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    documentation = (
        "New York applies its age and income tests alongside federal asset "
        "and immigration tests for the Child Care Block Grant route. Foster "
        "children and families with an open protective-services case bypass "
        "the income test. Those families and families experiencing "
        "homelessness bypass the activity test. Preventive-service receipt "
        "alone waives the family share and leaves the block grant tests "
        "unchanged. A child also qualifies through Title XX when the district "
        "authorizes preventive child care after applying its funding, plan, "
        "need, priority, financial and provider conditions. PolicyEngine "
        "applies the 18 NYCRR 415.1(b) age test on that route, with its "
        "special-needs and court-supervision extensions. A child who turns 13 "
        "during a school year may continue through the end of that school year."
    )
    reference = (
        # PDF pages 2, 15, 17
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=2",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=9",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.2",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.1",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-404.5",
    )

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        age_eligible = person("ny_ccap_age_eligible", period.this_year)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        income_eligible = spm_unit("ny_ccap_income_eligible", period)
        meets_activity_test = spm_unit("ny_ccap_activity_eligible", period)
        protective_services = spm_unit(
            "ny_ccap_protective_services_case", period.this_year
        )
        in_foster_care = person("is_in_foster_care", period)
        homeless = spm_unit.household("is_homeless", period.this_year)
        # New York waives income limits for foster and protective cases.
        categorically_eligible = in_foster_care | protective_services
        reason_for_care_eligible = (
            meets_activity_test | protective_services | in_foster_care | homeless
        )
        block_grant_eligible = (
            age_eligible
            & asset_eligible
            & immigration_eligible
            & reason_for_care_eligible
            & (income_eligible | categorically_eligible)
        )
        preventive_services = person("ny_ccap_receives_preventive_services", period)
        title_xx_approved = person(
            "ny_ccap_title_xx_preventive_services_approved", period
        )
        # 18 NYCRR 415.1(b)(1) and 415.2(d)(4)(ii) let a Title XX or
        # preventive child who turns 13 during a school year continue through
        # the end of that school year, before the child turns 14. The
        # authorization input records whether that continuation still runs.
        p = parameters(period).gov.states.ny.ocfs.ccap.eligibility.age_limit
        age = person("age", period.this_year)
        school_year_continuation_age = (age >= p.base) & (age < p.base + 1)
        title_xx_age_eligible = age_eligible | school_year_continuation_age
        title_xx_eligible = (
            preventive_services & title_xx_approved & title_xx_age_eligible
        )
        return block_grant_eligible | title_xx_eligible

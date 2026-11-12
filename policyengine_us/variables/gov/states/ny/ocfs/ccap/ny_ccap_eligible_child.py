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
        "need, priority, financial, age and provider conditions."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=15",
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
        return block_grant_eligible | (preventive_services & title_xx_approved)

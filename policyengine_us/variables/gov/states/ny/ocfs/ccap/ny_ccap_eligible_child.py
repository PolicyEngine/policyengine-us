from policyengine_us.model_api import *


class ny_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    documentation = (
        "New York's eligibility test, which replaces the federal "
        "is_ccdf_eligible for CCAP. It keeps the federal asset and "
        "immigration tests, applies New York's own age limit and income "
        "limit, and adds the two categorical routes New York law requires: "
        "foster care and open child protective or preventive services cases "
        "are eligible without regard to income, and families experiencing "
        "homelessness are served without further activity requirements while "
        "remaining subject to the income test. The protective services route "
        "is family-level and the foster care route is child-level, following "
        "415.2(a)(2)(vi)(a)-(b)."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=15",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=9",
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
        # 415.2(a)(2)(vi) waives the income test for foster care placements
        # and open child protective or preventive services cases.
        categorically_eligible = in_foster_care | protective_services
        # Reason for care mirrors the federal test, which already accepts
        # protective services in place of the activity test, and adds the
        # foster care and homelessness routes.
        reason_for_care_eligible = (
            meets_activity_test | protective_services | in_foster_care | homeless
        )
        return (
            age_eligible
            & asset_eligible
            & immigration_eligible
            & reason_for_care_eligible
            & (income_eligible | categorically_eligible)
        )

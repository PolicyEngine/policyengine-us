from policyengine_us.model_api import *


class ny_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    documentation = (
        "New York's eligibility test, which replaces the federal "
        "is_ccdf_eligible for CCAP. It keeps the federal age and asset "
        "tests, applies New York's own income limit, and adds the two "
        "categorical routes New York law requires: foster care and open "
        "child protective or preventive services cases are eligible without "
        "regard to income, and families experiencing homelessness are served "
        "without further activity requirements while remaining subject to "
        "the income test."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=12",
        "https://dos.ny.gov/system/files/documents/2024/05/050124.pdf#page=12",
    )

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        age_eligible = person("is_ccdf_age_eligible", period.this_year)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        income_eligible = spm_unit("ny_ccap_income_eligible", period)
        meets_activity_test = spm_unit("meets_ccdf_activity_test", period.this_year)
        protective_services = person(
            "receives_or_needs_protective_services", period.this_year
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
            & reason_for_care_eligible
            & (income_eligible | categorically_eligible)
        )

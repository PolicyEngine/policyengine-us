from policyengine_us.model_api import *


class wi_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin TANF eligible"
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145",
        "https://docs.legis.wisconsin.gov/code/admin_code/dcf/"
        "101_199/101/09",
    )
    defined_for = StateCode.WI
    documentation = """
    Eligibility for Wisconsin Works (W-2) requires:
    - Age 18+ (or minor parent under special provisions)
    - Custodial parent of dependent child (under 18, or under 19 if
      full-time student)
    - U.S. citizen or qualified non-citizen
    - Wisconsin resident
    - Income <= 115% FPL for household size
    - Assets <= $2,500 combined equity value (after exclusions)
    - Not receiving SSI, state supplemental payments, or SSDI
    - Cooperation with child support enforcement

    For simplified implementation, we test income and resource
    eligibility, plus federal demographic eligibility baseline.

    NOTE: Cannot enforce time limits (48-month state, 60-month federal)
    in single-period architecture. Cannot model work requirements or
    placement assignment.
    """

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (age, custodial parent)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Wisconsin-specific financial eligibility
        income_eligible = spm_unit("wi_tanf_income_eligible", period)
        resources_eligible = spm_unit(
            "wi_tanf_resources_eligible", period.this_year
        )

        # Combine all eligibility checks
        return demographic_eligible & income_eligible & resources_eligible

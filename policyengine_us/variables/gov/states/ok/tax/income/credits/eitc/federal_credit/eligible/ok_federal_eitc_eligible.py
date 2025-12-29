from policyengine_us.model_api import *


class ok_federal_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for federal EITC for the Oklahoma EITC computation"
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    Overall eligibility for federal EITC using FROZEN 2020 parameters.

    This combines all eligibility tests for the Oklahoma EITC computation:
    1. Demographic eligibility (age requirements)
    2. Investment income eligibility (must be <= $3,650 in 2020)
    3. Filing status (separate filers generally not eligible in 2020)

    Note: Uses 2020 federal eligibility rules regardless of current tax year.
    """

    def formula(tax_unit, period, parameters):
        # Use FROZEN 2020 parameters per Oklahoma statute
        eitc = parameters.gov.irs.credits.eitc("2020-01-01")
        # Check investment income eligibility
        investment_income_eligible = tax_unit(
            "ok_federal_eitc_investment_income_eligible", period
        )
        # Check demographic (age) eligibility
        demographic_eligible = tax_unit(
            "ok_federal_eitc_demographic_eligible", period
        )
        # Define eligibility before considering separate filer limitation
        eligible = demographic_eligible & investment_income_eligible
        # This parameter is true if separate filers are eligible
        if eitc.eligibility.separate_filer:
            return eligible
        # If separate filers are not eligible, check if the filer is separate
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return eligible & ~separate

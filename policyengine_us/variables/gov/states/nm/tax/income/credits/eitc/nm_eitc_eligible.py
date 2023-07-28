from policyengine_us.model_api import *


class nm_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for New Mexico EITC"
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf"  # 7-2-18.15
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # Use federal EITC eligibility, but replace demographic eligibility
        # with NM version.
        eitc = parameters.gov.irs.credits.eitc(period)
        investment_income_eligible = tax_unit(
            "eitc_investment_income_eligible", period
        )
        demographic_eligible = tax_unit("nm_eitc_demographic_eligible", period)
        # Define eligibility before considering separate filer limitation.
        eligible = demographic_eligible & investment_income_eligible
        # This parameter is true if separate filers are eligible.
        if eitc.eligibility.separate_filer:
            return eligible
        # If separate filers are not eligible, check if the filer is separate.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return eligible & ~separate

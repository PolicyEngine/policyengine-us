from policyengine_us.model_api import *


class eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

    def formula(tax_unit, period, parameters):
        eitc = parameters.gov.irs.credits.eitc(period)
        investment_income_eligible = tax_unit(
            "eitc_investment_income_eligible", period
        )
        demographic_eligible = tax_unit("eitc_demographic_eligible", period)
        # Define eligibility before considering separate filer limitation.
        eligible = demographic_eligible & investment_income_eligible
        # This parameter is true if separate filers are eligible.
        if eitc.eligibility.separate_filer:
            return eligible
        # If separate filers are not eligible, check if the filer is separate.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return eligible & ~separate

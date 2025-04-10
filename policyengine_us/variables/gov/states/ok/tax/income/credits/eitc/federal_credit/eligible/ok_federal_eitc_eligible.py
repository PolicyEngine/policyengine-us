from policyengine_us.model_api import *


class ok_federal_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for federal EITC for the Oklahoma EITC computation"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        eitc = parameters.gov.irs.credits.eitc(f"2020-01-01")
        investment_income_eligible = tax_unit(
            "ok_federal_eitc_investment_income_eligible", period
        )
        demographic_eligible = tax_unit(
            "ok_federal_eitc_demographic_eligible", period
        )
        # Define eligibility before considering separate filer limitation.
        eligible = demographic_eligible & investment_income_eligible
        # This parameter is true if separate filers are eligible.
        if eitc.eligibility.separate_filer:
            return eligible
        # If separate filers are not eligible, check if the filer is separate.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return eligible & ~separate

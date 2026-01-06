from policyengine_us.model_api import *


class ok_federal_eitc_investment_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets investment income eligibility for EITC"
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    Investment income eligibility for EITC using FROZEN 2020 parameters.

    To be eligible for the EITC, investment income must not exceed the
    annual limit. Oklahoma uses the 2020 federal limit regardless of
    current tax year.

    2020 Investment income limit: $3,650

    Investment income includes:
    - Taxable interest
    - Tax-exempt interest
    - Dividends
    - Capital gains
    - Rental and royalty income
    """

    def formula(tax_unit, period, parameters):
        # Use FROZEN 2020 parameters per Oklahoma statute
        eitc = parameters.gov.irs.credits.eitc("2020-01-01")
        invinc = tax_unit("eitc_relevant_investment_income", period)
        return invinc <= eitc.phase_out.max_investment_income

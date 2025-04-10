from policyengine_us.model_api import *


class ok_federal_eitc_investment_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets investment income eligibility for EITC"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        eitc = parameters.gov.irs.credits.eitc(f"2020-01-01")
        invinc = tax_unit("eitc_relevant_investment_income", period)
        return invinc <= eitc.phase_out.max_investment_income

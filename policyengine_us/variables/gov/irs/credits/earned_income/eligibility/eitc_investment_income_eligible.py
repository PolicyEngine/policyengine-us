from policyengine_us.model_api import *


class eitc_investment_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets investment income eligibility for EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#i"

    def formula(tax_unit, period, parameters):
        eitc = parameters.gov.irs.credits.eitc(period)
        invinc = tax_unit("eitc_relevant_investment_income", period)
        return invinc <= eitc.phase_out.max_investment_income

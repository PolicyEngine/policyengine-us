from policyengine_us.model_api import *


class ar_aged_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas aged personal credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        us_aged = tax_unit.sum("is_aged", period)
        
        p_ar = parameters(
            period
        ).gov.states.ar.tax.income.credits.personal_credits
        return us_aged * p_ar

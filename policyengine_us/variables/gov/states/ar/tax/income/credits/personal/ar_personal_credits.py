from policyengine_us.model_api import *


class ar_personal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas personal credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    adds = [
        "ar_personal_credit_dependent",
        "ar_personal_credits_base",
        "ar_personal_credit_disabled_dependent",
    ]

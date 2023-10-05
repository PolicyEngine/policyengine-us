from policyengine_us.model_api import *


class ar_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=2"
    )
    defined_for = StateCode.AR

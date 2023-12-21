from policyengine_us.model_api import *


class ar_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf",
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf",
    )
    defined_for = StateCode.AR

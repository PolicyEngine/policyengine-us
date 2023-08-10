from policyengine_us.model_api import *


class ar_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/TaxBrackets_2022.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_Final_AR1000ES.pdf"
    )
    defined_for = StateCode.AR

from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas exemption for retirement or disability benefits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = StateCode.AR

    adds = "ar_retirement_or_disability_benefits_exemptions_indv"
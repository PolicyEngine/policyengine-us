from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas retirement or disability benefits exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        retirement_or_disability = add(tax_unit, period, ["ar_retirement_or_disability_benefits_exemption_indv"])
        military_retirement = tax_unit("ar_military_retirement", period)
        return max_(retirement_or_disability, military_retirement)



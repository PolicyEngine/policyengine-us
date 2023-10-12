from policyengine_us.model_api import *


class ar_military_retirement(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas military retirement exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period).astype(int)
        spouse = person("is_tax_unit_spouse", period).astype(int)
        return tax_unit("military_retirement_pay") * (head | spouse)
    
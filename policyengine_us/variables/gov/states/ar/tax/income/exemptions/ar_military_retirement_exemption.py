from policyengine_us.model_api import *


class ar_military_retirement_exemption(Variable):
    value_type = float
    entity = Person
    label = "Arkansas military retirement exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return person("military_retirement_pay", period) * head_or_spouse

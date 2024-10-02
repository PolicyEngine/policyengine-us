from policyengine_us.model_api import *


class ar_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas deduction when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        itemized = person("ar_itemized_deductions_joint", period)
        standard = person("ar_standard_deduction_joint", period)
        return max_(itemized, standard)

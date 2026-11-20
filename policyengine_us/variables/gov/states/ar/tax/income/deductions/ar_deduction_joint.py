from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class ar_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas deduction when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        itemized = person("ar_itemized_deductions_joint", period)
        standard = person("ar_standard_deduction_joint", period)
        method = person.tax_unit("state_deduction_method", period)
        itemizes = state_itemization_uses_itemized(method, itemized > standard)
        return where(itemizes, itemized, standard)

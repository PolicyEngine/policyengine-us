from policyengine_us.model_api import *


class ms_agi_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi adjusted gross income when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=14",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 66
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        ms_agi = person.tax_unit("ms_agi_joint", period)
        # Per the atx form, the exemption amount is split in half between the head
        # and the spouse of the household
        return head_or_spouse * (0.5 * ms_agi)

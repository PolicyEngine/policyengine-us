from policyengine_us.model_api import *


class ms_total_exemptions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi total exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf#page=1"

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        total_exemptions = person.tax_unit("ms_total_exemptions_joint", period)
        # Per the atx form, the exemption amount is split in half between the head
        # and the spouse of the household
        return head_or_spouse * (0.5 * total_exemptions)

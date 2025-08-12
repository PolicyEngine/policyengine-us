from policyengine_us.model_api import *


class ms_total_exemptions_joint(Variable):
    value_type = float
    entity = Person
    label = "Mississippi total exemptions when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=6"

    def formula(person, period, parameters):
        total_exemptions = person.tax_unit("ms_total_exemptions", period)
        prorate_fraction = person("ms_prorate_fraction", period)
        return prorate_fraction * total_exemptions

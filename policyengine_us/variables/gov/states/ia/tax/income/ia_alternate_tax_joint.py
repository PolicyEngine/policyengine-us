from policyengine_us.model_api import *


class ia_alternate_tax_joint(Variable):
    value_type = float
    entity = Person
    label = "Iowa alternate tax when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        alt_tax = person.tax_unit("ia_alternate_tax_unit", period)
        return alt_tax * person("is_tax_unit_head", period)

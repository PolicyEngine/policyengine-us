from policyengine_us.model_api import *


class ia_alternate_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Iowa alternate tax when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline#page=53",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline#page=53",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        alt_tax = person.tax_unit("ia_alternate_tax_unit", period)
        return alt_tax * person("ia_prorate_fraction", period)

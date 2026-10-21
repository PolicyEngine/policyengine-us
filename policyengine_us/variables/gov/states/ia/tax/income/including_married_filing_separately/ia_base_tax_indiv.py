from policyengine_us.model_api import *


class ia_base_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Iowa base tax when married couples file separately"
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
        reg_tax = person("ia_regular_tax_indiv", period)
        alt_tax = person("ia_alternate_tax_indiv", period)
        alt_tax_eligible = person.tax_unit("ia_alternate_tax_eligible", period)
        smaller_tax = min_(reg_tax, alt_tax)
        return where(alt_tax_eligible, smaller_tax, reg_tax)

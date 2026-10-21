from policyengine_us.model_api import *


class ia_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Iowa itemized deductions for joint couples"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        deductions = person.tax_unit("ia_itemized_deductions_unit", period)
        is_head = person("is_tax_unit_head", period)
        return deductions * is_head

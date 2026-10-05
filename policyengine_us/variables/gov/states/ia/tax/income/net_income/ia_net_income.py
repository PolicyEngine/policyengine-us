from policyengine_us.model_api import *


class ia_net_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa net income"
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
        gross_income = person("ia_gross_income", period)
        income_adjustments = person("ia_income_adjustments", period)
        net_income = gross_income - income_adjustments
        # allocate any dependent net_income to tax unit head
        is_dependent = person("is_tax_unit_dependent", period)
        sum_dep_net_income = person.tax_unit.sum(is_dependent * net_income)
        is_head = person("is_tax_unit_head", period)
        return ~is_dependent * net_income + is_head * sum_dep_net_income

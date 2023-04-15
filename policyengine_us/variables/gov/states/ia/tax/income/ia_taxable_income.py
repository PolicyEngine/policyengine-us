from policyengine_us.model_api import *


class ia_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        net_income = tax_unit("ia_net_income", period)
        p = parameters(period).gov.states.ia.tax.income
        deductions = add(tax_unit, period, p.deductions.sources)
        return max_(0, net_income - deductions)

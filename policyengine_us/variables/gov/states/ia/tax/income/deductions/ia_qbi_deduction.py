from policyengine_us.model_api import *


class ia_qbi_deduction(Variable):
    value_type = float
    entity = Person
    label = "Iowa deduction that is fraction of federal qualified business income deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        fed_indv_qbid = person("qbid_amount", period)
        tax_unit = person.tax_unit
        fed_unit_qbid = tax_unit("qualified_business_income_deduction", period)
        reduction_factor = where(
            fed_indv_qbid > 0, fed_unit_qbid / fed_indv_qbid, 1.0
        )
        fed_qbid = fed_indv_qbid * reduction_factor
        p = parameters(period).gov.states.ia.tax.income
        return fed_qbid * p.deductions.qualified_business_income.fraction

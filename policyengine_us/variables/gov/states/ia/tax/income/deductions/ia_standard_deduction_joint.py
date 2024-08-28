from policyengine_us.model_api import *


class ia_standard_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Iowa standard deduction when married couples file jointly"
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
        filing_status = person.tax_unit("filing_status", period)
        is_head = person("is_tax_unit_head", period)
        p = parameters(period).gov.states.ia.tax.income

        if p.deductions.standard.applies_federal:
            fed_p = parameters(period).gov.irs.deductions
            deduction = fed_p.standard.amount[filing_status]
        else:
            deduction = p.deductions.standard.amount[filing_status]

        return is_head * deduction

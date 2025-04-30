from policyengine_us.model_api import *


class ia_regular_tax_joint(Variable):
    value_type = float
    entity = Person
    label = "Iowa regular tax calculated using income tax rate schedule when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53"
        "https://tax.iowa.gov/sites/default/files/2023-11/IA1041Inst%2863002%29.pdf#page=4"
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        taxable_income = person("ia_taxable_income_joint", period)
        p = parameters(period).gov.states.ia.tax.income.rates
        if p.by_filing_status.active:
            filing_status = person.tax_unit(
                "filing_status",
                period,
            )
            joint = filing_status == filing_status.possible_values.JOINT
            return where(
                joint,
                p.by_filing_status.joint.calc(taxable_income),
                p.by_filing_status.other.calc(taxable_income),
            )
        return p.combined.calc(taxable_income)

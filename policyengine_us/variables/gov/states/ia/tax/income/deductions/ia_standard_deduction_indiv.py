from policyengine_us.model_api import *


class ia_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Iowa standard deduction when married couples file separately"
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
        us_filing_status = person.tax_unit("filing_status", period)
        fsvals = us_filing_status.possible_values
        filing_status = select(
            [
                us_filing_status == fsvals.JOINT,
                us_filing_status == fsvals.SINGLE,
                us_filing_status == fsvals.SEPARATE,
                us_filing_status == fsvals.HEAD_OF_HOUSEHOLD,
                us_filing_status == fsvals.WIDOW,
            ],
            [
                fsvals.SEPARATE,  # couples are filing separately on Iowa form
                fsvals.SINGLE,
                fsvals.SEPARATE,
                fsvals.HEAD_OF_HOUSEHOLD,
                fsvals.WIDOW,
            ],
        )
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        p = parameters(period).gov.states.ia.tax.income
        return (is_head | is_spouse) * p.deductions.standard[filing_status]

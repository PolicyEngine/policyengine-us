from policyengine_us.model_api import *


class ia_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Iowa tax return"
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
        p = parameters(
            period
        ).gov.states.ia.tax.income.married_filing_separately_on_same_return
        if p.availability:
            itax_indiv = tax_unit("ia_income_tax_indiv", period)
            itax_joint = tax_unit("ia_income_tax_joint", period)
            return itax_indiv < itax_joint
        return False

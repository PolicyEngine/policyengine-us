from policyengine_us.model_api import *


class ms_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Mississippi tax return"
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
        itax_indiv = add(
            tax_unit, period["ms_income_tax_before_credits_indiv"]
        )
        itax_joint = add(
            tax_unit, period["ms_income_tax_before_credits_joint"]
        )
        return itax_indiv < itax_joint

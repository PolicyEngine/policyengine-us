from policyengine_us.model_api import *


class ia_alternate_tax_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Iowa alternate tax eligible"
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        return filing_status != filing_status.possible_values.SINGLE

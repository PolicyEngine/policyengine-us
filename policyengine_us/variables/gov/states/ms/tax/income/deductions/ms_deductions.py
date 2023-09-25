from policyengine_us.model_api import *


class ms_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf#page=1"
        "https://www.law.cornell.edu/regulations/mississippi/35-Miss-Code-R-SS-3-02-11-103"
    )
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        itemized = tax_unit("ms_itemized_deductions", period)
        standard = tax_unit("ms_standard_deduction", period)
        return max_(itemized, standard)

from policyengine_us.model_api import *


class va_spouse_tax_adjustment_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Virginia's spouse tax adjustment"
    defined_for = StateCode.VA
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        exemptions = person("va_agi_less_exemptions_indiv", period)
        smaller_exemptions = tax_unit.min(exemptions)
        return smaller_exemptions > 0

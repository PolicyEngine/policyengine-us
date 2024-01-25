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
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        agi_less_exemptions_person = person(
            "va_agi_less_exemptions_person", period
        )
        agi_less_exemptions = where(
            head_or_spouse, agi_less_exemptions_person, np.inf
        )
        smaller_exemptions = tax_unit.min(agi_less_exemptions)
        joint = tax_unit("tax_unit_is_joint", period)
        return (smaller_exemptions > 0) & joint

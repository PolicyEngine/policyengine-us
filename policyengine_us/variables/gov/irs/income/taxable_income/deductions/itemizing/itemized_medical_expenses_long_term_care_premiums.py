from policyengine_us.model_api import *


class itemized_medical_expenses_long_term_care_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Long-term care premiums included in itemized medical expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/213#d_10",
        "https://www.irs.gov/instructions/i1040sca",
    )
    documentation = (
        "The eligible long-term care premiums inside itemized_medical_expenses. "
        "The computed subtotal counts health insurance premiums and other "
        "medical expenses only, so this is zero for it. A supplied subtotal "
        "is the Schedule A line 1 amount, which includes the members' "
        "eligible long-term care premiums. States that deduct long-term care "
        "premiums separately remove this amount from the subtotal first."
    )

    def formula(tax_unit, period, parameters):
        supplied = has_input_for_period(
            tax_unit.simulation, "itemized_medical_expenses", period
        )
        eligible = add(tax_unit, period, ["eligible_long_term_care_premiums"])
        return eligible * supplied

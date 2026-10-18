from policyengine_us.model_api import *


class itemized_medical_expenses_long_term_care_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Long-term care premiums in itemized medical expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/213#d_10",
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=2",
    )
    documentation = (
        "The eligible long-term care insurance premiums inside the Schedule A "
        "medical subtotal (itemized_medical_expenses): every member's "
        "premiums up to the 26 U.S.C. 213(d)(10) limit for that member's age, "
        "less the part the self-employed health insurance deduction took. "
        "The computed subtotal adds this amount, so supplying it sets the "
        "long-term care premiums the subtotal counts. A supplied subtotal "
        "bypasses this formula, and the amount is 0 unless it is supplied "
        "too: the long-term care premiums inside the supplied subtotal. "
        "States that deduct long-term care premiums separately take this "
        "amount out of the subtotal first."
    )

    def formula(tax_unit, period, parameters):
        if has_input_for_period(
            tax_unit.simulation, "itemized_medical_expenses", period
        ):
            return 0
        premiums = add(tax_unit, period, ["eligible_long_term_care_premiums"])
        excluded = tax_unit(
            "itemized_medical_expenses_excluded_long_term_care_premiums", period
        )
        return premiums - excluded

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
        "less the part the head's and spouse's self-employed health insurance "
        "deduction took and the long-term care part of each dependent's own "
        "deduction. "
        "The computed subtotal adds this amount, so supplying it sets the "
        "long-term care premiums the subtotal counts. A supplied subtotal "
        "bypasses this formula, and the amount is 0 unless it is supplied "
        "too: the long-term care premiums inside the supplied subtotal. With "
        "a supplied subtotal that leaves out premiums taken as the "
        "self-employed deduction, follow the split "
        "itemized_medical_expenses_applied_exclusion uses, whatever the return "
        "itself did: the eligible long-term care premiums less any part of "
        "that exclusion above the head's and spouse's medical insurance "
        "premiums. States that deduct long-term care premiums separately take "
        "this amount out of the subtotal first."
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
        # A dependent's own deduction, on the dependent's own return, took
        # its long-term care part (Form 7206 line 2) out of the dependent's
        # premiums (26 U.S.C. 162(l)(3)).
        person = tax_unit.members
        dependents_part = tax_unit.sum(
            person("self_employed_health_insurance_ald_long_term_care_part", period)
            * person("is_tax_unit_dependent", period)
        )
        return premiums - excluded - dependents_part

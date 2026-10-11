from policyengine_us.model_api import *


class itemized_medical_expenses_applied_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employed premium exclusion applied to Schedule A medical expenses"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
        "https://www.irs.gov/instructions/i1040sca",
    ]
    documentation = (
        "Premiums actually excluded by the federal medical expense formula. "
        "A caller-supplied subtotal bypasses that formula, so no exclusion "
        "was applied. States retaining gross paid medical costs restore this "
        "amount only for computed subtotals. Premium inputs use payer "
        "attribution, including family coverage paid by a filer. Correct "
        "provenance after deleting and recalculating a supplied subtotal "
        "requires policyengine-core>=3.32.27. Earlier cores retain the deleted "
        "input marker, so North Dakota's renter refund and New Mexico's senior "
        "medical credit and exemption can omit the computed exclusion add-back."
    )

    def formula(tax_unit, period, parameters):
        if has_input_for_period(
            tax_unit.simulation, "itemized_medical_expenses", period
        ):
            return 0
        return tax_unit("itemized_medical_expenses_excluded_premiums", period)

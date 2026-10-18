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
        "was applied, unless the caller also supplies this amount: the "
        "premiums a supplied Schedule A subtotal already leaves out because "
        "they were taken as the self-employed health insurance deduction. "
        "In a simulation with several tax units, supply it for each of them, "
        "since a formula variable supplied for some units is 0 for the rest. "
        "States retaining gross paid medical costs restore this amount; "
        "Montana's 2021-2023 schedule uses it to take only the premiums still "
        "inside the subtotal out of line 1. Premium inputs use payer "
        "attribution, including family coverage paid by a filer. The required "
        "policyengine-core>=3.32.27 clears input provenance on deletion, so "
        "recalculating a deleted subtotal also restores its applied exclusion."
    )

    def formula(tax_unit, period, parameters):
        if has_input_for_period(
            tax_unit.simulation, "itemized_medical_expenses", period
        ):
            return 0
        return tax_unit("itemized_medical_expenses_excluded_premiums", period)

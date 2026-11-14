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
        "Filer premiums and dependent medical premiums excluded by the "
        "federal medical expense formula. Dependent long-term care premiums "
        "remain outside this state addback, as under the existing state bases. "
        "A caller-supplied subtotal bypasses that formula. Supply this amount "
        "when that subtotal already leaves out premiums taken as the "
        "self-employed health insurance deduction. Include medical and "
        "long-term care premiums. Allocate the exclusion to the head's and "
        "spouse's medical premiums first. In a simulation with "
        "several tax units, supply it for each of them, since a formula "
        "variable supplied for some units is 0 for the rest. States retaining "
        "gross paid medical costs restore this amount; Montana's 2021-2023 "
        "schedule uses it to take only the medical premiums still inside the "
        "subtotal out of line 1. Premium inputs use payer attribution, "
        "including family coverage paid by a filer. "
        "For a computed subtotal, a supplied exclusion replaces only the "
        "filers' exclusion and excludes dependents' medical premiums. "
        "Montana restores the computed dependent amount separately. North "
        "Dakota and New Mexico use the supplied amount unchanged, so their "
        "full paid-cost bases require the derived exclusion or a supplied "
        "subtotal with its complete exclusion. A supplied exclusion for a "
        "supplied subtotal includes all premiums that subtotal leaves out, "
        "including dependents' medical premiums, for North Dakota and New "
        "Mexico's addbacks. Montana caps the medical part of any supplied "
        "exclusion at the filers' premiums. The required "
        "policyengine-core>=3.32.27 clears input provenance on deletion, so "
        "recalculating a deleted subtotal also restores its applied exclusion."
    )

    def formula(tax_unit, period, parameters):
        if has_input_for_period(
            tax_unit.simulation, "itemized_medical_expenses", period
        ):
            return 0
        # Medical insurance premiums and eligible long-term care premiums the
        # self-employed health insurance deduction took.
        return add(
            tax_unit,
            period,
            [
                "itemized_medical_expenses_excluded_premiums",
                "itemized_medical_expenses_excluded_long_term_care_premiums",
                "itemized_medical_expenses_excluded_dependent_premiums",
            ],
        )

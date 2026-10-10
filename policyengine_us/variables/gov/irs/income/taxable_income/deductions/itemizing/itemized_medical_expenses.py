from policyengine_us.model_api import *


class itemized_medical_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized medical expenses"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/213",
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
        "https://www.irs.gov/instructions/i1040sca",
    ]
    documentation = (
        "Medical expenses counted before applying the itemized medical "
        "expense deduction floor. IRC Section 213(d)(1) defines medical care "
        "to include amounts paid for diagnosis, cure, mitigation, treatment, "
        "or prevention of disease; transportation primarily for essential "
        "medical care; qualified long-term care services; and insurance "
        "premiums covering medical care. Current modeling uses health "
        "insurance premiums and other medical expenses, excluding general "
        "over-the-counter health expenses. Premiums deducted through the "
        "filer's self-employed health insurance deduction are excluded under "
        "IRC Section 162(l)(3) before the medical expense floor is applied. "
        "Premium inputs use payer attribution: each person reports premiums "
        "that person paid, including the full cost of family coverage regardless "
        "of whom it covers. A parent-paid dependent policy belongs on the parent. "
        "The exclusion is bounded to filer-paid premiums; beneficiary-attributed "
        "inputs with an ALD exceeding that pool are inconsistent with this contract "
        "and cannot establish conservation of the supplied ALD."
    )

    def formula(tax_unit, period, parameters):
        premiums = add(tax_unit, period, ["medical_expense_health_insurance_premiums"])
        # The federal ALD covers the head and spouse; dependents take their
        # own SE deductions on their own returns. Bound the exclusion to the
        # corresponding filer premiums, leaving other medical costs intact.
        excluded_premiums = tax_unit(
            "itemized_medical_expenses_excluded_premiums", period
        )
        other_expenses = add(tax_unit, period, ["other_medical_expenses"])
        return premiums - excluded_premiums + other_expenses

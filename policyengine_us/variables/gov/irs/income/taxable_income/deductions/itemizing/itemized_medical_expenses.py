from policyengine_us.model_api import *


class itemized_medical_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized medical expenses"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partVII-sec213.htm",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partVI-sec162.htm",
        "https://www.ecfr.gov/current/title-26/section-1.213-1#p-1.213-1(a)(1)",
        "https://www.irs.gov/instructions/i1040sca",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=2",
    ]
    documentation = (
        "Medical expenses counted before applying the itemized medical "
        "expense deduction floor. IRC Section 213(d)(1) defines medical care "
        "to include amounts paid for diagnosis, cure, mitigation, treatment, "
        "or prevention of disease; transportation primarily for essential "
        "medical care; qualified long-term care services; and insurance "
        "premiums covering medical care, with long-term care insurance "
        "premiums counted up to the 213(d)(10) limit for the insured person's "
        "age. Current modeling uses health insurance premiums, those eligible "
        "long-term care premiums (recorded on the insured person) and other "
        "medical expenses, excluding general over-the-counter health "
        "expenses. Section 162(l)(3) excludes premiums the filers deduct "
        "through their self-employed health insurance deduction. Section "
        "213(a) and Treasury regulation 1.213-1(a)(1) allow only expenses "
        "the filers paid, so premiums a dependent deducts on their own "
        "return also leave the subtotal before the medical expense floor. "
        "Premium inputs use payer attribution: each person reports premiums "
        "that person paid, including the full cost of family coverage regardless "
        "of whom it covers. A parent-paid dependent policy belongs on the parent. "
        "The filer exclusion is bounded to the head's and spouse's premium pool; "
        "each dependent exclusion is bounded to their own premiums. Beneficiary-attributed "
        "inputs with an ALD exceeding that pool are inconsistent with this contract "
        "and cannot establish conservation of the supplied ALD. A supplied value "
        "bypasses this formula and is used as given. By default it is taken as "
        "medical costs paid before any self-employed exclusion "
        "(itemized_medical_expenses_applied_exclusion is 0). If it is a Schedule "
        "A line 1 amount that already leaves out premiums taken as the "
        "self-employed health insurance deduction, also supply all of those "
        "premiums, medical and long-term care, as "
        "itemized_medical_expenses_applied_exclusion; the exclusion is taken "
        "from the head's and spouse's medical insurance premiums first, as this "
        "formula does. Report any long-term care premiums still inside the "
        "supplied value, by that same split, in "
        "itemized_medical_expenses_long_term_care_premiums."
    )

    def formula(tax_unit, period, parameters):
        premiums = add(tax_unit, period, ["medical_expense_health_insurance_premiums"])
        # Filers and dependents deduct their own premiums on their own
        # returns. Exclude each deducted payment once, within its paid pool.
        excluded_premiums = add(
            tax_unit,
            period,
            [
                "itemized_medical_expenses_excluded_premiums",
                "itemized_medical_expenses_excluded_dependent_premiums",
            ],
        )
        # Eligible long-term care premiums less the part the same deduction
        # took.
        long_term_care_premiums = tax_unit(
            "itemized_medical_expenses_long_term_care_premiums", period
        )
        other_expenses = add(tax_unit, period, ["other_medical_expenses"])
        return premiums - excluded_premiums + long_term_care_premiums + other_expenses

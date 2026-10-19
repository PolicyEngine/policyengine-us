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
        # CPS ASEC wording of the premium and medical care questions, PDF
        # pages 2-3.
        "https://www.census.gov/content/dam/Census/library/working-papers/2015/demo/Medical-Out-of-pocket-Expenses-CPSASEC-2013-2014.pdf#page=2",
    ]
    documentation = (
        "Medical expenses counted before applying the itemized medical "
        "expense deduction floor. IRC Section 213(d)(1) defines medical care "
        "to include amounts paid for diagnosis, cure, mitigation, treatment, "
        "or prevention of disease; transportation primarily for essential "
        "medical care; qualified long-term care services; and insurance "
        "premiums covering medical care. Current modeling uses health "
        "insurance premiums and other medical expenses, excluding general "
        "over-the-counter health expenses. IRC Section 213(a) allows expenses "
        "the taxpayer paid for the taxpayer, the spouse and dependents. "
        "Premium inputs use payer attribution: each person reports premiums "
        "that person paid, including the full cost of family coverage regardless "
        "of whom it covers. A parent-paid dependent policy belongs on the parent. "
        "So only the head's and spouse's premiums count; a dependent's own "
        "premium payments are not the filers' expenses. Other medical expenses "
        "are recorded on the person cared for, including amounts other "
        "household members paid on that person's behalf, so every member's "
        "count. Premiums deducted through the filer's self-employed health "
        "insurance deduction are excluded under IRC Section 162(l)(3) before "
        "the medical expense floor is applied. "
        "The exclusion is bounded to filer-paid premiums; beneficiary-attributed "
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
        # IRC 213(a) counts what the head and spouse paid. Premium inputs sit
        # on the payer, so take only their premiums, which include coverage
        # they bought for dependents; a dependent's own payments are not the
        # filers' expenses.
        premiums = tax_unit_non_dep_sum(
            "medical_expense_health_insurance_premiums", tax_unit, period
        )
        # The federal ALD covers the head and spouse; dependents take their
        # own SE deductions on their own returns. Bound the exclusion to the
        # corresponding filer premiums, leaving other medical costs intact.
        excluded_premiums = tax_unit(
            "itemized_medical_expenses_excluded_premiums", period
        )
        # Other medical expenses sit on the person cared for, including
        # amounts household members paid on a dependent's behalf, so count
        # every member's.
        other_expenses = add(tax_unit, period, ["other_medical_expenses"])
        return premiums - excluded_premiums + other_expenses

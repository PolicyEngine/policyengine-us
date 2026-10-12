from policyengine_us.model_api import *


class mo_qualified_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Missouri qualified health insurance premiums"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/5695.pdf",  # Lines 8-17
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=15",
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=7",
        "https://www.irs.gov/pub/irs-pdf/f1040sa.pdf",
    )
    documentation = (
        "Health insurance premiums eligible for the Missouri subtraction, "
        "excluding premiums already deducted through the self-employed health "
        "insurance deduction or federal itemization. Premium inputs follow "
        "payer attribution: record a person's premiums on the person who paid "
        "them, including all parent-paid family coverage on the parent. Each "
        "person's SE deduction exclusion is capped at that person's premiums. "
        "Filers' person deductions are limited to the actual tax-unit federal "
        "deduction; dependents retain their own deductions. "
        "A supplied tax-unit SE deduction without corresponding person "
        "deductions is allocated across the filers' remaining premiums. "
        "Form 5695's federal medical deduction ratio is rounded to a whole "
        "percent; half-percent ties round up, consistent with Missouri's "
        "percentage-rounding examples."
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        person_premiums = max_(person("health_insurance_premiums", period), 0)
        person_se_ald = max_(
            person("self_employed_health_insurance_ald_person", period), 0
        )
        filer = not_(person("is_tax_unit_dependent", period))
        tax_unit_se_ald = max_(
            tax_unit("self_employed_health_insurance_ald", period), 0
        )
        filers_person_se_ald = tax_unit.sum(person_se_ald * filer)
        # A supplied unit deduction can be smaller than the modeled personal
        # deductions. Respect the actual amount claimed on the filers' return.
        filer_scale = np.divide(
            min_(tax_unit_se_ald, filers_person_se_ald),
            filers_person_se_ald,
            out=np.zeros_like(filers_person_se_ald),
            where=filers_person_se_ald > 0,
        )
        attributed_se_ald = where(filer, person_se_ald * filer_scale, person_se_ald)
        # MO-1040 instructions, page 15, exclude federally deducted premiums
        # from Form 5695's pool before applying its Schedule A overlap ratio.
        person_eligible_premiums = max_(person_premiums - attributed_se_ald, 0)
        # Reconcile a directly supplied tax-unit ALD. Compare against actual
        # person ALDs, so an unmatched payer's deduction cannot consume another
        # person's premiums merely because its own exclusion was capped.
        unattributed_ald = max_(tax_unit_se_ald - filers_person_se_ald, 0)
        filer_premiums = person_eligible_premiums * filer
        tax_unit_filer_premiums = tax_unit.sum(filer_premiums)
        unattributed_share = np.divide(
            filer_premiums,
            tax_unit_filer_premiums,
            out=np.zeros_like(filer_premiums),
            where=tax_unit_filer_premiums > 0,
        )
        person_eligible_premiums -= unattributed_share * min_(
            unattributed_ald, tax_unit_filer_premiums
        )
        tax_unit_premiums = tax_unit.sum(person_eligible_premiums)

        # Form 5695 lines 10-12 use Schedule A lines 1 and 4, with the ratio
        # rounded to a full percent. Half-up ties follow the percentage example
        # in the MO-1040 instructions, page 7 (97.5% becomes 98%).
        medical_expenses = tax_unit("itemized_medical_expenses", period)
        medical_deduction = tax_unit("medical_expense_deduction", period)
        # Divide in float64 before rounding so float32 error cannot turn an
        # exact half-percent tie, such as 5,850 / 10,000, into a value below it.
        medical_percent = np.divide(
            medical_deduction.astype(np.float64) * 100,
            medical_expenses,
            out=np.zeros_like(medical_expenses, dtype=np.float64),
            dtype=np.float64,
            where=medical_expenses > 0,
        )
        rounded_ratio = np.floor(medical_percent + 0.5) / 100
        remaining_premiums = max_(tax_unit_premiums * (1 - rounded_ratio), 0)

        # Lines 16-17 cap the unit's subtraction at federal taxable income,
        # then allocate it by each person's share of the qualifying premiums.
        person_share = np.divide(
            person_eligible_premiums,
            tax_unit_premiums,
            out=np.zeros_like(person_eligible_premiums),
            where=tax_unit_premiums > 0,
        )
        itemizes = tax_unit("tax_unit_itemizes", period)
        taxable_income = tax_unit("taxable_income", period)
        return person_share * min_(
            where(itemizes, remaining_premiums, tax_unit_premiums), taxable_income
        )

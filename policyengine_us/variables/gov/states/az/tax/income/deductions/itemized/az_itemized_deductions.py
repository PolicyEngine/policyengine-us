from policyengine_us.model_api import *


class az_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Itemized Deductions"
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://law.justia.com/codes/arizona/2022/title-43/section-43-1042/",
        "https://www.azleg.gov/ars/43/01042.htm",
        "https://azdor.gov/forms/individual/itemized-deduction-adjustments-form",
        "https://azdor.gov/forms/individual/form-140-resident-personal-income-tax-form-calculating",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        az_itemized = parameters(period).gov.states.az.tax.income.deductions.itemized
        # Medical and charitable are handled separately below; the state and
        # local tax deduction is also handled separately so Arizona can cap it.
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction
            not in [
                "medical_expense_deduction",
                "charitable_deduction",
                "salt_deduction",
            ]
        ]
        federal_deductions = add(tax_unit, period, deductions)
        # Per A.R.S. 43-1042(D) (HB 4168, TY2026+), Arizona caps the state and
        # local tax itemized deduction in lieu of IRC 164(b)(7). The cap is a
        # flat amount before 2026 (the cap parameter is infinite, so the full
        # federal SALT deduction passes through unchanged).
        # NOTE: The bill states a single $10,000 cap with no single-vs-MFJ
        # split, so it applies as a flat amount regardless of filing status.
        salt_deduction = tax_unit("salt_deduction", period)
        capped_salt_deduction = min_(salt_deduction, az_itemized.salt_cap)
        # Arizona allows a complete deduction for medical and dental expenses
        medical_expenses = tax_unit("itemized_medical_expenses", period)

        # Adjustments to Charitable Contributions
        # Amount of charitable contributions for which you are claiming
        # a credit under Arizona law.
        charitable_deduction = tax_unit("charitable_deduction", period)
        charitable_contributions_credit = tax_unit(
            "az_charitable_contributions_credit_potential", period
        )
        # The charitable deduction is reduced by the amount which is used for the
        # Arizona charitable contributions credit,
        # assuming that the same charitable contributions
        charitable_deduction_after_credit = max_(
            charitable_deduction - charitable_contributions_credit, 0
        )
        # The state and local income tax is reduced by the amount which is used
        # to claim the Arizona charitable contributions credit
        # Since the Arizona charitable contributions credit is based on contributions
        # to qulalifying foster care organizations, we do not reduce the salt deduction
        return (
            federal_deductions
            + capped_salt_deduction
            + medical_expenses
            + charitable_deduction_after_credit
        )

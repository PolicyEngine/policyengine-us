from policyengine_us.model_api import *


class me_itemized_deductions_pre_phaseout(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine itemized deductions before phaseout"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_2_ff.pdf",
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5125.html",
        # Section 68 as amended by P.L. 119-21, sec. 70111, from 2026.
        # PDF pages 94-95
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=94",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Get the Maine itemizing deduction parameters.
        p = parameters(period).gov.states.me.tax.income.deductions.itemized

        # Get federal itemized deductions minus SALT (Section 3A).
        deduction = tax_unit("itemized_deductions_less_salt", period)

        # Get medical (and dental) expenses.
        medical_expenses = tax_unit("medical_expense_deduction", period)

        # Get real estate (and property) taxes.
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])

        p_limitation = parameters(period).gov.irs.deductions.itemized.limitation
        if p_limitation.obbb.applies:
            # 36 M.R.S. 5125(1) starts from the itemized deductions claimed
            # federally, after the section 68 reduction. Allocate the uniform
            # 2026 reduction pro rata to each federal component Maine
            # subtracts or carves out (a deduced allocation; no 2026 agency
            # rule was verified).
            total = tax_unit("total_itemized_taxable_income_deductions", period)
            allowed = tax_unit("itemized_taxable_income_deductions", period)
            mask = total > 0
            allowed_share = np.zeros_like(total)
            allowed_share[mask] = allowed[mask] / total[mask]
            deduction = deduction * allowed_share
            medical_expenses = medical_expenses * allowed_share
            # Property taxes inside the federal SALT deduction (pro rata
            # within SALT) keep their section 68 reduction; those the SALT
            # cap excluded are added back in full under 5125(3)(A-1).
            salt = tax_unit("salt", period)
            salt_deduction = tax_unit("salt_deduction", period)
            deducted_property_taxes = np.zeros_like(salt)
            salt_mask = salt > 0
            deducted_property_taxes[salt_mask] = (
                salt_deduction[salt_mask]
                * real_estate_taxes[salt_mask]
                / salt[salt_mask]
            )
            real_estate_taxes = (
                real_estate_taxes - (1 - allowed_share) * deducted_property_taxes
            )

        # Calculate uncapped (potential) itemized deductions.
        deduction_no_med = deduction - medical_expenses + real_estate_taxes

        # Calculate capped itemized deductions.
        capped_deduction_no_med = min_(deduction_no_med, p.cap)

        # Add back medical and dental expenses (which are not capped).
        return capped_deduction_no_med + medical_expenses

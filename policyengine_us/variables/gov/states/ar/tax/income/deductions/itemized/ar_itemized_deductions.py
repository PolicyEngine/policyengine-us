from policyengine_us.model_api import *


class ar_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized
        p_ded = parameters(period).gov.irs.deductions

        agi = tax_unit("adjusted_gross_income", period)
        person_agi = tax_unit("adjusted_gross_income_person", period)

        # Less salt deduction
        deductions = [
            deduction
            for deduction in p_ded.itemized_deductions
            if deduction not in ["salt_deduction", "medical_expense_deduction",]
        ]
        less_salt_deds =  add(tax_unit, period, deductions)

        # Real estate tax + Personal property tax
        real_estate_deds = add(tax_unit, period, ["real_estate_taxes"])

        # Post-secondary Education Tuition Deduction
        tuition_deds = tax_unit(
            "ar_post_secondary_education_tuition_deductions", period
        )

        # Limitation on several items
        # Medical and Dental Expense
        medical_expenses = add(tax_unit, period, ["medical_expense"])
        medical_deds = max_(
            0,
            medical_expenses
            - p.expense_rate.medical * agi,
        )

        # Miscellaneous Deductions
        misc_deds = tax_unit("misc_deduction", period)
        adjusted_misc_deds = max_(
            0,
            misc_deds
            - p_ded.itemized.misc.floor * agi,
        )

        total_itemized_deduction = (
            less_salt_deds
            + medical_deds
            + real_estate_deds
            + tuition_deds
            + adjusted_misc_deds
        )

        # Prorated itemized deductions
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        proration = np.zeros_like(agi)
        mask = agi > 0
        proration[mask] = (
            person_agi[mask] / agi[mask]
        )
        separated_itemized_deduction = total_itemized_deduction * proration

        return where(
            separate, separated_itemized_deduction, total_itemized_deduction
        )

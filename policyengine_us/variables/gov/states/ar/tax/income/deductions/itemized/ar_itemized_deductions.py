from policyengine_us.model_api import *


class ar_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        agi = tax_unit("adjusted_gross_income", period)
        spouse_agi = tax_unit("spouse_separate_adjusted_gross_income", period)

        # Less salt deduction
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized
        less_salt_deds = tax_unit("itemized_deductions_less_salt", period)
        exempt_deds = add(tax_unit, period, ["medical_expense_deduction"])
        adjusted_salt_deds = max(0, less_salt_deds - exempt_deds)

        # Real estate tax + Personal property tax
        person_real_estate_deds = person("real_estate_taxes", period)
        real_estate_deds = tax_unit.sum(person_real_estate_deds)

        # Post-secondary Education Tuition Deduction
        tuition_deds = tax_unit(
            "ar_post_secondary_education_tuition_deductions", period
        )

        # Limitation on several items
        # Medical and Dental Expense
        medical_expense = add(tax_unit, period, ["medical_expense"])
        medical_deds = max_(
            0,
            medical_expense
            - p.medical_deduction_threshold * (agi + spouse_agi),
        )

        # Miscellaneous Deductions
        misc_p = parameters(period).gov.irs.deductions.itemized.misc
        misc_deds = where(
            tax_unit("misc_deduction", period)
            <= misc_p.floor * (agi + spouse_agi),
            tax_unit("misc_deduction", period),
            0,
        )

        total_itemized_deduction = (
            adjusted_salt_deds
            + medical_deds
            + real_estate_deds
            + tuition_deds
            + misc_deds
        )

        # Prorated itemized deductions
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE

        separated_itemized_deduction = total_itemized_deduction * (
            agi / (agi + spouse_agi)
        )

        return where(
            separate, separated_itemized_deduction, total_itemized_deduction
        )

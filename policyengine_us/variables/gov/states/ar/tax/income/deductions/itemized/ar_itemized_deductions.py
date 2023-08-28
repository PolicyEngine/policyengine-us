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
        p = parameters(period).gov.irs.deductions.itemized
        less_salt_deds = tax_unit("itemized_deductions_less_salt", period)

        agi = tax_unit("adjusted_gross_income", period)
        spouse_agi = tax_unit("spouse_separate_adjusted_gross_income", period)

        # Real estate tax + Personal property tax
        real_estate_deds = tax_unit("real_estate_taxes", period)

        # Post-secondary Education Tuition Deduction
        tuition_deds = tax_unit(
            "ar_post_secondary_education_tuition_deductions", period
        )

        # Limitation on several items
        # Miscellaneous Deductions
        misc_deds = where(
            tax_unit("misc_deduction", period)
            <= p.misc.floor * (agi + spouse_agi),
            tax_unit("misc_deduction", period),
            0,
        )

        total_itemized_deduction = (
            less_salt_deds + +real_estate_deds + tuition_deds + misc_deds
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

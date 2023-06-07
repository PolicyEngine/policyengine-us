from policyengine_us.model_api import *


class nj_taking_property_tax_deduction(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Household taking New Jersey property tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/"
    defined_for = "nj_property_tax_deduction_eligible"

    def formula(tax_unit, period, parameters):
        # This follows the logic of the 1040 instructions Worksheet H.

        # Get the would-be property tax deduction.
        deduction = tax_unit("nj_potential_property_tax_deduction", period)

        # Get NJ taxable income before property tax deduction.
        taxable_income_before_deduction = tax_unit(
            "nj_taxable_income_before_property_tax_deduction", period
        )

        # Calculate the amount of taxes owed without the deduction.
        p = parameters(period).gov.states.nj.tax.income.main
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        taxes_without_deduction = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(taxable_income_before_deduction),
                p.joint.calc(taxable_income_before_deduction),
                p.head_of_household.calc(taxable_income_before_deduction),
                p.widow.calc(taxable_income_before_deduction),
                p.separate.calc(taxable_income_before_deduction),
            ],
        )

        # Calculate NJ taxable income after property tax deduction.
        taxable_income_after_deduction = (
            taxable_income_before_deduction - deduction
        )

        # Calculate the amount of taxes owed after the deduction.
        taxes_with_deduction = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(taxable_income_after_deduction),
                p.joint.calc(taxable_income_after_deduction),
                p.head_of_household.calc(taxable_income_after_deduction),
                p.widow.calc(taxable_income_after_deduction),
                p.separate.calc(taxable_income_after_deduction),
            ],
        )

        # Determine whether the difference in tax incidence is greater than the credit amount.
        # Credit amount is halved if filing separately but maintaining the same home.
        credit_amount = parameters(
            period
        ).gov.states.nj.tax.income.credits.property_tax.amount
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        credit_amount = credit_amount / (1 + separate * cohabitating)

        return (taxes_without_deduction - taxes_with_deduction) > credit_amount

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
        p = parameters(period).gov.states.nj.tax.income.main

        # follows NJ-1040 form Worksheet H
        deduction = tax_unit("nj_potential_property_tax_deduction", period)

        # calculate taxes without deduction
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        taxable_income_before_deduction = tax_unit(
            "nj_taxable_income_before_property_tax_deduction", period
        )
        taxes_without_deduction = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(taxable_income_before_deduction),
                p.joint.calc(taxable_income_before_deduction),
                p.head_of_household.calc(taxable_income_before_deduction),
                p.surviving_spouse.calc(taxable_income_before_deduction),
                p.separate.calc(taxable_income_before_deduction),
            ],
        )

        # calculate taxes with deduction
        taxable_income_after_deduction = max_(
            0, taxable_income_before_deduction - deduction
        )
        taxes_with_deduction = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(taxable_income_after_deduction),
                p.joint.calc(taxable_income_after_deduction),
                p.head_of_household.calc(taxable_income_after_deduction),
                p.surviving_spouse.calc(taxable_income_after_deduction),
                p.separate.calc(taxable_income_after_deduction),
            ],
        )

        # calculate credit amount
        credit_amount = parameters(
            period
        ).gov.states.nj.tax.income.credits.property_tax.amount
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        credit_amount = credit_amount / (1 + separate * cohabitating)

        # choose between taxable income deduction and refundable credit
        return (taxes_without_deduction - taxes_with_deduction) > credit_amount

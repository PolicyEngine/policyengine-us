from policyengine_us.model_api import *


class ma_part_b_taxable_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B taxable income deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-3"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        tax = parameters(period).gov.states.ma.tax.income
        # (B)(a)(3): Taxes for retirement programs.
        # NB: The law only mentions FICA and FRRA, but mass.gov includes SECA.
        # https://www.mass.gov/service-details/learn-about-business-and-professional-income
        person = tax_unit.members
        SS_MEDICARE_VARIABLES = [
            "employee_social_security_tax",
            "employee_medicare_tax",
            "self_employment_social_security_tax",
            "self_employment_medicare_tax",
        ]
        fica_person = add(person, period, SS_MEDICARE_VARIABLES)
        fica_head = min_(
            tax.deductions.public_retirement_contributions,
            fica_person * person("is_tax_unit_head", period),
        )
        fica_spouse = min_(
            tax.deductions.public_retirement_contributions,
            fica_person * person("is_tax_unit_spouse", period),
        )
        fica = tax_unit.sum(fica_head) + tax_unit.sum(fica_spouse)
        # Bank interest deduction.
        filing_status = tax_unit("filing_status", period)
        if tax.exemptions.interest.in_effect:
            bank_interest = add(tax_unit, period, ["taxable_interest_income"])
            bank_interest_deduction = min_(
                tax.exemptions.interest.amount[filing_status],
                bank_interest,
            )
        else:
            bank_interest_deduction = 0
        # (B)(a)(9): Rent deduction.
        rent = add(tax_unit, period, ["rent"])
        rent_deduction = tax.deductions.rent.share * rent
        rent_deduction = min_(
            rent_deduction,
            tax.deductions.rent.cap[filing_status],
        )
        # (B)(a)(13): Charitable contributions deduction.
        charitable_deduction = tax_unit("charitable_deduction", period)
        return (
            fica
            + bank_interest_deduction
            + rent_deduction
            + charitable_deduction
        )

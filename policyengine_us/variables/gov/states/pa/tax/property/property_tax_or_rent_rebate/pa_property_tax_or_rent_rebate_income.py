from policyengine_us.model_api import *


class pa_property_tax_or_rent_rebate_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania Property Tax/Rent Rebate income"
    unit = USD
    definition_period = YEAR
    reference = (
        # PDF pages 3, 7-9
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/"
        "formsandpublications/formsforindividuals/ptrr/documents/"
        "2025_pa-1000_inst.pdf#page=3",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.pa.tax.property.property_tax_or_rent_rebate
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        above_the_line_deductions = tax_unit("above_the_line_deductions", period)
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)
        # Federal AGI includes taxable tier 1 benefits, which line 5 replaces
        # with half of the total.
        taxable_railroad_tier_1 = tax_unit(
            "tax_unit_taxable_railroad_social_security_equivalent_benefits", period
        )
        half_counted_benefits = tax_unit.sum(
            head_or_spouse
            * add(
                person,
                period,
                [
                    "social_security",
                    "ssi",
                    # pa_ssp includes the Supplement for Personal Needs for
                    # Medicaid facility residents; the PA-1000 does not say
                    # whether the Department of Revenue treats it as SSP.
                    "pa_ssp",
                    # Line 5: half of Railroad Retirement Tier 1 benefits as
                    # Form RRB-1099 shows them.
                    "railroad_social_security_equivalent_benefits",
                ],
            )
        )
        tax_exempt_income = tax_unit.sum(
            head_or_spouse
            * add(
                person,
                period,
                [
                    "tax_exempt_interest_income",
                    "tax_exempt_pension_income",
                    "tax_exempt_retirement_distributions",
                    # Line 6 takes the gross amount of Tier 2 Railroad
                    # Retirement benefits; their taxable part is in
                    # adjusted_gross_income.
                    "tax_exempt_railroad_pension_benefits",
                ],
            )
        )
        pa_1000_line_11_income = tax_unit.sum(
            head_or_spouse
            * add(
                person,
                period,
                [
                    "gambling_winnings",
                    "alimony_income",
                    "workers_compensation",
                    # The taxable part is already in adjusted_gross_income.
                    "tax_exempt_disability_benefits",
                ],
            )
        )
        life_insurance_benefits = tax_unit.sum(
            head_or_spouse * person("life_insurance_benefits", period)
        )
        taxable_life_insurance_benefits = max_(
            0, life_insurance_benefits - p.death_benefit_exclusion
        )
        csrs_pay = person("csrs_retirement_pay", period)
        csrs_income = tax_unit.sum(head_or_spouse * csrs_pay)
        csrs_exclusion = tax_unit.sum(
            head_or_spouse * min_(csrs_pay, p.csrs_income_exclusion)
        )

        return max_(
            0,
            adjusted_gross_income
            + above_the_line_deductions
            - taxable_social_security
            - taxable_railroad_tier_1
            + p.benefit_income_rate * half_counted_benefits
            + tax_exempt_income
            + pa_1000_line_11_income
            + taxable_life_insurance_benefits
            + csrs_income
            - csrs_exclusion,
        )

from policyengine_us.model_api import *


class pa_property_tax_or_rent_rebate_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania Property Tax/Rent Rebate income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/"
        "formsandpublications/formsforindividuals/ptrr/documents/"
        "2025_pa-1000_inst.pdf#page=7",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/"
        "formsandpublications/formsforindividuals/ptrr/documents/"
        "2025_pa-1000_inst.pdf#page=8",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/"
        "formsandpublications/formsforindividuals/ptrr/documents/"
        "2025_pa-1000_inst.pdf#page=9",
        # PA-1000 booklet, line 11b: net gambling and lottery winnings
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/"
        "formsandpublications/formsforindividuals/ptrr/documents/"
        "dfo-03.pdf#page=40",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.pa.tax.property.property_tax_or_rent_rebate
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        above_the_line_deductions = tax_unit("above_the_line_deductions", period)
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)
        half_counted_benefits = tax_unit.sum(
            head_or_spouse
            * add(
                person,
                period,
                [
                    "social_security",
                    "ssi",
                    "railroad_benefits",
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
                ],
            )
        )
        pa_1000_line_11_income = tax_unit.sum(
            head_or_spouse
            * add(
                person,
                period,
                [
                    "alimony_income",
                    "workers_compensation",
                    "disability_benefits",
                ],
            )
        )
        # Line 11b counts net gambling and lottery winnings: losses offset the
        # winnings but may not exceed them. The winnings are already in
        # federal adjusted gross income.
        gambling_loss_offset = tax_unit.sum(
            head_or_spouse * person("pa_gambling_loss_offset", period)
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
            + p.benefit_income_rate * half_counted_benefits
            + tax_exempt_income
            + pa_1000_line_11_income
            - gambling_loss_offset
            + taxable_life_insurance_benefits
            + csrs_income
            - csrs_exclusion,
        )

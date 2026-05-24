from policyengine_us.model_api import *


class mn_homestead_credit_refund_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Homestead Credit Refund household income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Approximates Form M1PR lines 1 through 13 using modeled adjusted gross "
        "income, nontaxable Social Security, retirement add-backs and "
        "contributions, and age/disability and dependent subtractions. "
        "Co-occupant income and other nontaxable additions or subtractions "
        "are not separately modeled."
    )
    reference = (
        "https://www.taxformfinder.org/forms/2024/2024-minnesota-form-m1pr-instructions.pdf#page=7",
        "https://www.taxformfinder.org/forms/2025/2025-minnesota-form-m1pr-instructions.pdf#page=7",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn
        income_p = p.tax.income
        refund_p = p.tax.property.homestead_credit_refund

        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        gross_income = tax_unit("adjusted_gross_income", period) + (
            tax_unit("spouse_separate_adjusted_gross_income", period) * separate
        )

        people = tax_unit.members
        is_dependent = people("is_tax_unit_dependent", period) | people(
            "claimed_as_dependent_on_another_return", period
        )
        social_security = people("social_security", period)
        taxable_social_security = people("taxable_social_security", period)
        nontaxable_social_security = tax_unit.sum(
            max_(0, social_security - taxable_social_security) * ~is_dependent
        )

        retirement_contributions = add(
            tax_unit,
            period,
            [
                "traditional_401k_contributions",
                "roth_401k_contributions",
                "traditional_403b_contributions",
                "roth_403b_contributions",
                "capped_traditional_ira_contributions",
                "capped_roth_ira_contributions",
                "self_employed_pension_contributions",
            ],
        )
        retirement_additions = add(
            tax_unit,
            period,
            [
                "traditional_401k_contributions",
                "traditional_403b_contributions",
                "capped_traditional_ira_contributions",
                "self_employed_pension_contributions",
            ],
        )
        compensation = add(
            tax_unit, period, ["employment_income", "self_employment_income"]
        )
        retirement_subtraction = min_(
            retirement_contributions,
            min_(compensation, refund_p.retirement_subtraction.limit[filing_status]),
        )

        claimant = people("is_tax_unit_head_or_spouse", period)
        minimum_age = income_p.credits.renters.age_threshold
        is_age_eligible = people("age", period) >= minimum_age
        is_disabled = people("is_permanently_and_totally_disabled", period)
        age_or_disability_subtraction = (
            tax_unit.any(claimant & ~is_dependent & (is_age_eligible | is_disabled))
            * income_p.exemptions.amount
        )

        dependent_count = tax_unit("tax_unit_dependents", period)
        dependent_subtraction_multiplier = (
            income_p.credits.renters.dependent_subtraction_multiplier.calc(
                dependent_count
            )
        )
        dependent_subtraction = (
            income_p.exemptions.amount * dependent_subtraction_multiplier
        )

        additions = nontaxable_social_security + retirement_additions
        subtractions = (
            age_or_disability_subtraction
            + dependent_subtraction
            + retirement_subtraction
        )
        return max_(0, gross_income + additions - subtractions)

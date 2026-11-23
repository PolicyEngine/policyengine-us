from policyengine_us.model_api import *


class mn_homestead_credit_refund_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Homestead Credit Refund household income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Approximates Form M1PR lines 1 through 13 using modeled adjusted gross "
        "income, nontaxable Social Security, government assistance (line 4), "
        "the line 6 nontaxable income and deductions listed in "
        "gov.states.mn.tax.property.homestead_credit_refund.income_additions, "
        "alimony not in adjusted gross income, retirement add-backs and "
        "contributions, and age/disability and dependent subtractions. "
        "Co-occupant income and other nontaxable additions or subtractions "
        "are not separately modeled."
    )
    reference = (
        "https://www.taxformfinder.org/forms/2024/2024-minnesota-form-m1pr-instructions.pdf#page=7",
        "https://www.taxformfinder.org/forms/2025/2025-minnesota-form-m1pr-instructions.pdf#page=7",
        # Minn. Stat. 290A.03, subd. 3 (income) and subd. 5 (household income).
        "https://www.revisor.mn.gov/statutes/cite/290A.03",
        # IRC 219(b)(5)(A), the retirement base amount of subd. 3(d)(2).
        "https://www.law.cornell.edu/uscode/text/26/219#b_5_A",
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
        claimant = people("is_tax_unit_head_or_spouse", period)
        is_dependent = people("is_tax_unit_dependent", period) | people(
            "claimable_as_dependent_on_another_return", period
        )
        social_security = people("social_security", period)
        taxable_social_security = people("taxable_social_security", period)
        nontaxable_social_security = tax_unit.sum(
            max_(0, social_security - taxable_social_security) * ~is_dependent
        )

        # Lines 4 and 6 (subd. 3(a)(2)): government assistance, nontaxable
        # income and the deductions added back. Household income leaves out
        # a dependent's income (subd. 5), so person amounts count for the
        # head and spouse only. The HSA deduction is the filer's tax unit
        # amount, and tanf, an SPM unit amount, counts as the tax unit's
        # per-person share.
        listed_additions = tax_unit_non_dep_add(
            tax_unit, period, refund_p.income_additions
        )
        # Subd. 3(a)(2)(xiv): "alimony received to the extent not included
        # in the recipient's income". taxable_alimony_income is the part in
        # federal AGI.
        alimony = tax_unit_non_dep_add(tax_unit, period, ["alimony_income"])
        taxable_alimony = tax_unit_non_dep_add(
            tax_unit, period, ["taxable_alimony_income"]
        )
        nontaxable_alimony = max_(0, alimony - taxable_alimony)

        # Line 1 is the filer's federal AGI, which leaves out tax unit
        # dependents, so the retirement add-backs, contributions and
        # compensation count the head and spouse only.
        retirement_contributions = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "traditional_401k_contributions",
                "roth_401k_contributions",
                "traditional_403b_contributions",
                "roth_403b_contributions",
                "traditional_ira_contributions",
                "roth_ira_contributions",
                "self_employed_pension_contributions",
            ],
        )
        # M1PR line 3 adds back "your deductions for your qualified retirement
        # plan contributions from lines 16 and 20 of federal Schedule 1", so
        # the IRA term is the federal deduction (Schedule 1 line 20), not total
        # traditional contributions: nondeductible contributions never left
        # federal AGI. 2025 M1PR instructions, PDF page 7:
        # https://www.taxformfinder.org/forms/2025/2025-minnesota-form-m1pr-instructions.pdf#page=7
        retirement_additions = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "traditional_401k_contributions",
                "traditional_403b_contributions",
                "traditional_ira_deduction",
                "self_employed_pension_contributions",
            ],
        )
        compensation = tax_unit_non_dep_add(
            tax_unit, period, ["employment_income", "self_employment_income"]
        )
        # Subd. 3(d)(2): the retirement base amount is "the deductible amount
        # for the taxable year for the claimant and spouse under section
        # 219(b)(5)(A)", the federal IRA limit for each of them.
        ira_limit = parameters(
            period
        ).gov.irs.gross_income.retirement_contributions.limit.ira
        retirement_base_amount = ira_limit * tax_unit.sum(claimant)
        retirement_subtraction = min_(
            retirement_contributions,
            min_(compensation, retirement_base_amount),
        )

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

        additions = (
            nontaxable_social_security
            + listed_additions
            + nontaxable_alimony
            + retirement_additions
        )
        subtractions = (
            age_or_disability_subtraction
            + dependent_subtraction
            + retirement_subtraction
        )
        return max_(0, gross_income + additions - subtractions)

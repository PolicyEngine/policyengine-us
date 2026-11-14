from policyengine_us.model_api import *


class nd_renters_refund_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota Renter's Refund income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://ndlegis.gov/cencode/t57c02.pdf#page=16",
        "https://www.tax.nd.gov/sites/www/files/documents/guidelines/homestead-veterans-renters/credits-for-nd-homeowners-renters-guideline.pdf#page=2",
    )
    defined_for = StateCode.ND

    documentation = (
        "Renter refund income: the listed income sources, less the parts of "
        "market income that federal law excludes and the unreimbursed medical "
        "costs actually paid, and at least zero. The excluded parts are those "
        "of each person's market income components "
        "(nd_renters_refund_federally_excluded_income) and the federal "
        "exclusions the model deducts above the line (excluded_deductions), "
        "each of which comes out of the tax unit's income that holds it, or, "
        "for income from Puerto Rico and American Samoa, out of market income "
        "before losses. Social security counts in full. "
        "The paid-cost base restores the self-employed premiums excluded from "
        "the federal subtotal: by the federal formula, or as supplied with a "
        "caller's subtotal in itemized_medical_expenses_applied_exclusion. A "
        "caller-supplied subtotal without that amount is used unchanged, "
        "including when components are supplied. Premium inputs use payer "
        "attribution: each person reports premiums that person paid, including "
        "family coverage regardless of whom it covers."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        # NDCC 57-02-08.1(5)(c) excludes "any amount excluded from income by
        # federal or state law with the exception of income from social
        # security benefits". market_income counts wages before payroll
        # deductions and the tax-exempt parts of several sources in full, so
        # subtract the parts federal law excludes. Social security stays whole.
        person_exclusions = add(
            tax_unit, period, ["nd_renters_refund_federally_excluded_income"]
        )
        # The model deducts some federal exclusions above the line, so
        # market_income still holds the income they exclude. Each comes out of
        # the income that holds it, summed over the tax unit, because a
        # household may record savings bond interest spent on higher education
        # (IRC 135) on the student and employer adoption assistance (IRC 137)
        # on the child: savings bond interest out of the interest North Dakota
        # counts, and adoption assistance out of wages after payroll
        # deductions. Income from Puerto Rico and American Samoa (IRC 933,
        # 931) can sit in any component, so it comes out of market income
        # before losses, less the other exclusions. None of them comes out of
        # social security, and a loss elsewhere in the unit keeps none of them
        # in.
        holders = {
            "us_bonds_for_higher_ed": max_(
                add(tax_unit, period, ["interest_income"])
                - add(tax_unit, period, ["tax_exempt_interest_income"]),
                0,
            ),
            "qualified_adoption_assistance_expense": max_(
                add(tax_unit, period, ["irs_employment_income"]), 0
            ),
        }
        deducted_exclusions = 0
        without_holder = 0
        for name in p.excluded_deductions:
            excluded = max_(add(tax_unit, period, [name]), 0)
            if name in holders:
                deducted_exclusions = deducted_exclusions + min_(
                    excluded, holders[name]
                )
            else:
                without_holder = without_holder + excluded
        # Market income before losses: each person's components, each at
        # zero or more.
        person = tax_unit.members
        income_before_losses = 0
        for component in p.market_income_components:
            income_before_losses = income_before_losses + max_(
                person(component, period), 0
            )
        income_left = max_(
            tax_unit.sum(income_before_losses)
            - person_exclusions
            - deducted_exclusions,
            0,
        )
        deducted_exclusions = deducted_exclusions + min_(without_holder, income_left)
        # Restore premiums excluded from the federal subtotal (computed, or
        # supplied with a caller's subtotal).
        medical_expenses = add(
            tax_unit,
            period,
            [
                "itemized_medical_expenses",
                "itemized_medical_expenses_applied_exclusion",
            ],
        )
        return max_(
            add(tax_unit, period, p.income_sources)
            - person_exclusions
            - deducted_exclusions
            - medical_expenses,
            0,
        )

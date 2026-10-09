from policyengine_us.model_api import *


class hi_food_excise_exemption_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exemption amount for Hawaii Food/Excise Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=50",
        "https://files.hawaii.gov/tax/forms/2025/n311_i.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax

        income = tax_unit("adjusted_gross_income", period)

        minor_child_include = p.minor_child.in_effect
        # Count exemptions as number of people
        #   The legal code defines exemptions as Hawaii exemptions,
        #   which normally include additional exemptions for aged and
        #   disabled people, but excludes those additional exemptions
        #   for this program.
        # Determine amount per exemption based on income and filing status
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        amount_per_exemption = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.amount.single.calc(income),
                p.amount.joint.calc(income),
                p.amount.head_of_household.calc(income),
                p.amount.separate.calc(income),
                p.amount.surviving_spouse.calc(income),
            ],
        )
        exemptions = tax_unit("exemptions_count", period)
        minor_children = tax_unit("hi_food_excise_credit_minor_child_count", period)
        if p.minor_child.in_effect:
            # Reduce number of exemptions by the number of minor children,
            # who get a fixed amount instead.
            claimable_exemptions = exemptions - minor_children
            minor_child_exemptions = 0
        else:
            claimable_exemptions = exemptions
            minor_child_exemptions = minor_children
        # Form N-311 counts only people who cannot be claimed as a dependent
        # by another taxpayer. A return on which a filer can be claimed
        # generally claims no dependents (IRS Publication 501; its exception
        # for a claimer who files only for a refund is not modeled), so it
        # counts the filers who cannot be claimed and, through HRS
        # 235-55.85(c), their minor children receiving public support.
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        mixed_return_exemptions = independent_filers + where(
            independent_filers > 0, minor_child_exemptions, 0
        )
        qualified_exemptions = where(
            dependent_filer, mixed_return_exemptions, claimable_exemptions
        )
        return qualified_exemptions * amount_per_exemption

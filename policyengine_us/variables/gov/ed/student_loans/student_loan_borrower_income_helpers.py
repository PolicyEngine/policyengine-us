from policyengine_us.model_api import *

DEPENDENT_BORROWER_INCOME = "income_driven_repayment_dependent_adjusted_gross_income"


def poverty_guideline_for_family_size(household, period, parameters, size):
    """HHS poverty guideline for a family of `size` in the household's state
    group (34 CFR 685.209(b)(14)). Alaska and Hawaii residents use their own
    guidelines; everyone else, including residents of the territories, uses
    the 48 contiguous states' guideline."""
    p = parameters(period).gov.hhs.fpg
    state_group = household("state_group", period)
    groups = state_group.possible_values
    guideline_group = where(
        state_group == groups.AK,
        "AK",
        where(state_group == groups.HI, "HI", "CONTIGUOUS_US"),
    )
    first_person = p.first_person[guideline_group]
    additional_person = p.additional_person[guideline_group]
    return first_person + additional_person * (size - 1)


def repayment_assistance_plan_annual_base_payment(agi, period, parameters):
    """Annual Repayment Assistance Plan base payment on `agi` (20 U.S.C.
    1087e(q)(4)(B)(iv); 34 CFR 685.209(b)(2)): the bracket rate times the
    whole adjusted gross income, or the low-income amount when that income is
    not more than the rate scale's first finite threshold."""
    p = parameters(period).gov.ed.student_loans.repayment_assistance_plan.base_payment
    # The low-income limit is the first finite threshold of the rate scale.
    low_income = agi <= p.rate.thresholds[1]
    income_based_payment = p.rate.calc(agi, right=True) * agi
    return where(low_income, p.low_income_amount, income_based_payment)


def income_contingent_repayment_factor(agi, is_single, period, parameters):
    """Income percentage factor at `agi` from the Department of Education's
    annual notice (34 CFR 685.209(f)(4)(i)(A)), from the single table or the
    married or head of household table."""
    p = parameters(
        period
    ).gov.ed.student_loans.income_contingent_repayment.income_percentage_factor
    # The table rows are points to interpolate between, not brackets.
    single_factor = np.interp(agi, p.single.thresholds, p.single.amounts)
    married_factor = np.interp(
        agi,
        p.married_or_head_of_household.thresholds,
        p.married_or_head_of_household.amounts,
    )
    factor = where(is_single, single_factor, married_factor)
    # The notice rounds the interpolated factor to the nearest hundredth of
    # a percent, which is four decimal places of the fraction.
    return np.round(factor, 4)


def dependent_borrower_discretionary_income(
    person, period, parameters, fpg_exempt_rate
):
    """Monthly discretionary income of a borrower claimed as someone else's
    tax dependent: their own income above the plan's multiple of the poverty
    guideline for a family of one (34 CFR 685.209(b)(4), (b)(9), (e)(1))."""
    year = period.this_year
    income = person(DEPENDENT_BORROWER_INCOME, year)
    # 685.209(b)(9): the borrower, plus a spouse on a joint return and anyone
    # the borrower supports. A dependent is modeled as supporting no one.
    poverty_guideline = poverty_guideline_for_family_size(
        person.household, year, parameters, 1
    )
    exempt_income = fpg_exempt_rate * poverty_guideline
    return max_(income - exempt_income, 0) / MONTHS_IN_YEAR


def borrower_discretionary_income(
    person, period, parameters, tax_unit_variable, fpg_exempt_rate
):
    """Monthly discretionary income that sets the person's payment: their
    tax unit's `tax_unit_variable` for a head or spouse, and their own for a
    borrower claimed as a tax dependent."""
    is_dependent = person("is_tax_unit_dependent", period.this_year)
    return where(
        is_dependent,
        dependent_borrower_discretionary_income(
            person, period, parameters, fpg_exempt_rate
        ),
        person.tax_unit(tax_unit_variable, period),
    )


def dependent_borrower_repayment_assistance_plan_applicable_payment(
    person, period, parameters
):
    """Applicable monthly Repayment Assistance Plan payment of a borrower
    claimed as someone else's tax dependent: the base payment on their own
    income divided by 12, and no less than the minimum payment. There is no
    dependent reduction, because a person claimed as a dependent has no
    dependents of their own (26 U.S.C. 152(b)(1))."""
    p = parameters(period).gov.ed.student_loans.repayment_assistance_plan
    year = period.this_year
    income = person(DEPENDENT_BORROWER_INCOME, year)
    base_payment = repayment_assistance_plan_annual_base_payment(
        income, year, parameters
    )
    return max_(base_payment / MONTHS_IN_YEAR, p.minimum_payment)

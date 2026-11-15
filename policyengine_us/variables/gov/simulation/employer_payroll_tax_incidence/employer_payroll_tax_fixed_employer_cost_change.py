from typing import NamedTuple, Optional

from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.payroll.payroll_tax_gross_wages import (
    payroll_tax_gross_wages as default_payroll_tax_gross_wages,
)
from policyengine_us.reforms.tax_exempt.tax_exempt_reform import (
    payroll_tax_exempt_income,
    tax_exempt_payroll_tax_gross_wages,
)


# The variables each federal employer tax is calculated from. Abolishing any
# of them (core's gov.abolitions switches, which zero a variable) removes the
# tax.
SOCIAL_SECURITY_VARIABLES = (
    "employer_social_security_tax",
    "taxable_earnings_for_social_security",
    "payroll_tax_gross_wages",
)
MEDICARE_VARIABLES = ("employer_medicare_tax", "payroll_tax_gross_wages")
FEDERAL_UNEMPLOYMENT_VARIABLES = (
    "employer_federal_unemployment_tax",
    "employer_federal_unemployment_tax_rate",
    "taxable_earnings_for_federal_unemployment_tax",
    "payroll_tax_gross_wages",
)


def abolishes(gov, variables):
    """Whether ``gov`` abolishes any of ``variables``, which core then zeroes."""
    for variable in variables:
        try:
            if gov.abolitions[variable]:
                return True
        except KeyError:
            # Core has abolition switches only for calculated variables.
            continue
    return False


def federal_employer_payroll_tax_components(gov, state_code, cap=None):
    """Federal employer payroll taxes on payroll wages, as (rate, base) pairs.

    Each tax is ``rate * min(wages, base)``, as in
    ``employer_social_security_tax``, ``employer_medicare_tax`` and
    ``employer_federal_unemployment_tax``. The base is ``inf`` for the
    uncapped Medicare tax. The federal unemployment rate varies by state
    through its credit reduction, so it is an array. A tax whose variable, or
    a variable it is calculated from, is abolished has a rate of zero.

    A finite ``gov.contrib.cbo.payroll.secondary_earnings_threshold`` turns on
    CBO's option to tax earnings above a second threshold as well as below the
    cap, which taxes ``rate * max(0, wages - threshold)`` more, with the
    threshold at least the cap. That is ``rate * wages - rate * min(wages,
    threshold)``, so it adds an uncapped component and a negative one.

    Args:
        gov: The ``gov`` parameter node for one period.
        state_code: Each person's state code.
        cap: The Social Security taxable maximum to use, if not ``gov``'s own.

    Returns:
        A list of (rate, base) pairs.
    """
    payroll = gov.irs.payroll
    social_security = payroll.social_security
    federal_unemployment = payroll.federal_unemployment
    if cap is None:
        cap = social_security.cap
    social_security_rate = social_security.rate.employer * (
        not abolishes(gov, SOCIAL_SECURITY_VARIABLES)
    )
    components = [
        (social_security_rate, cap),
        (
            payroll.medicare.rate.employer * (not abolishes(gov, MEDICARE_VARIABLES)),
            np.inf,
        ),
        (
            (
                federal_unemployment.effective_rate
                + federal_unemployment.credit_reduction_rate[state_code]
            )
            * (not abolishes(gov, FEDERAL_UNEMPLOYMENT_VARIABLES)),
            federal_unemployment.taxable_wage_base,
        ),
    ]
    secondary_threshold = max(gov.contrib.cbo.payroll.secondary_earnings_threshold, cap)
    if np.isfinite(secondary_threshold):
        components += [
            (social_security_rate, np.inf),
            (-social_security_rate, secondary_threshold),
        ]
    return components


def employer_payroll_tax_from_components(wages, components):
    """Employer payroll tax on payroll wages under (rate, base) pairs."""
    wages = np.asarray(wages, dtype=np.float64)
    tax = np.zeros_like(wages)
    for rate, base in components:
        tax = tax + rate * np.minimum(wages, base)
    return tax


def components_match(first, second):
    """Whether two lists of (rate, base) pairs describe the same taxes."""
    return len(first) == len(second) and all(
        np.array_equal(np.asarray(rate_a), np.asarray(rate_b))
        and np.array_equal(np.asarray(base_a), np.asarray(base_b))
        for (rate_a, base_a), (rate_b, base_b) in zip(first, second)
    )


def wages_at_employer_cost(cost, components):
    """Payroll wages whose cost to the employer equals ``cost``.

    The cost of payroll wages w is ``w + tax(w)``, where ``tax`` sums
    ``rate * min(w, base)`` over the components. The cost is continuous and
    piecewise linear in w, with kinks at the bases, and strictly increasing
    while each segment's slope (1 plus the rates of the taxes whose base lies
    above the segment) is positive. So each cost of zero or more has exactly
    one wage, found by locating the segment that contains the cost and
    inverting it there.

    Args:
        cost: Employer cost of each person's payroll wages, at least zero.
        components: (rate, base) pairs, as from
            ``federal_employer_payroll_tax_components``. Rates may be arrays;
            bases must be scalars of zero or more.

    Returns:
        The payroll wages for each cost.

    Raises:
        ValueError: If a segment's slope is not positive, so the cost does not
            rise with wages and no unique wage exists.
    """
    cost = np.asarray(cost, dtype=np.float64)
    breakpoints = sorted(
        {
            float(base)
            for _, base in components
            if np.isfinite(float(base)) and float(base) > 0
        }
    )
    wages = np.zeros_like(cost)
    for lower in [0.0] + breakpoints:
        slope = 1 + sum(
            np.asarray(rate, dtype=np.float64) * (float(base) > lower)
            for rate, base in components
        )
        slope = np.broadcast_to(slope, cost.shape)
        if np.any(slope <= 0):
            raise ValueError(
                "Employer payroll tax rates must keep the employer's cost "
                f"rising with wages, but on payroll wages from {lower:,.0f} "
                f"the rates sum to {float(np.min(slope)) - 1:.4f}, so a "
                "dollar of wages costs the employer nothing or less. "
                f"Components (rate, base): {components!r}."
            )
        cost_at_lower = lower + employer_payroll_tax_from_components(
            np.full_like(cost, lower), components
        )
        wages = np.where(
            cost >= cost_at_lower,
            lower + (cost - cost_at_lower) / slope,
            wages,
        )
    return wages


def fixed_employer_cost_wage_change(
    pay,
    baseline_exclusions,
    reform_exclusions,
    baseline_components,
    reform_components,
    share,
):
    """Change in pay that holds the employer's federal cost of it fixed.

    Payroll wages are ``max(0, pay - exclusions)``, with each system's own
    exclusions. The employer's outlay on a worker is their pay plus federal
    employer payroll tax on their payroll wages. The change brings the outlay
    under the reform's schedule and exclusions to its baseline amount, and
    ``share`` of it applies.

    Args:
        pay: Each person's pay, which may be negative.
        baseline_exclusions: Pay the baseline's payroll wages leave out.
        reform_exclusions: Pay the reform's payroll wages leave out.
        baseline_components: Baseline (rate, base) pairs.
        reform_components: Reform (rate, base) pairs.
        share: The share of the fixed-cost change that applies.

    Returns:
        The change in each person's pay.
    """
    pay = np.asarray(pay, dtype=np.float64)
    baseline_wages = np.maximum(pay - baseline_exclusions, 0)
    # Payroll wages under the reform's definition, before the change.
    # Negative when the reform excludes more than the pay.
    reform_wages = pay - reform_exclusions
    # The baseline outlay less the reform's exclusions: pay differs from
    # reform payroll wages by a fixed amount, so holding this fixed holds the
    # outlay fixed.
    cost = reform_wages + employer_payroll_tax_from_components(
        baseline_wages, baseline_components
    )
    # Below zero, the reform taxes none of the pay, so the employer pays out
    # the whole saving and the reform's wages equal the cost.
    new_wages = np.where(
        cost > 0,
        wages_at_employer_cost(np.maximum(cost, 0), reform_components),
        cost,
    )
    change = (new_wages - reform_wages) * share
    # With nonnegative tax rates and a share of at most 1 this floor never
    # binds. A larger share passes on more than the fixed-cost change, and
    # the floor keeps reform payroll wages from falling below zero.
    return np.maximum(change, -np.maximum(reform_wages, 0))


DEFAULT_WAGE_RULE = "default"
TAX_EXEMPT_WAGE_RULE = "tax_exempt"


def payroll_wage_rule(system, period):
    """Which definition of payroll wages a tax-benefit system uses.

    Payroll wages are ``max(0, employment_income - exclusions)`` under every
    definition in this package: the exclusions are FICA pre-tax contributions,
    plus exempt tips and overtime premiums under the tax-exempt reform. A
    definition this function does not know raises, so that a new structural
    reform to payroll wages adds its exclusions here rather than having
    employer cost held on the wrong wages.
    """
    formula = system.get_variable("payroll_tax_gross_wages").get_formula(period)
    # Code objects compare by content, so a formula loaded again from the
    # same source still matches.
    code = getattr(formula, "__code__", None)
    if code == default_payroll_tax_gross_wages.formula.__code__:
        return DEFAULT_WAGE_RULE
    if code == tax_exempt_payroll_tax_gross_wages.__code__:
        return TAX_EXEMPT_WAGE_RULE
    raise NotImplementedError(
        "employer_payroll_tax_fixed_employer_cost_change does not know this "
        f"system's payroll_tax_gross_wages formula ({formula!r}). Add its "
        "exclusions to payroll_wage_exclusions."
    )


def payroll_wage_exclusions(person, period, system, rule):
    """Pay that ``system``'s payroll wages leave out, for each person.

    Each system's FICA pre-tax contributions come from its own list of them
    (inputs), so a reform to the list, or to its abolition switch, leaves the
    baseline's exclusions alone.
    """
    gov = system.parameters(period).gov
    if abolishes(gov, ["fica_pre_tax_contributions"]):
        exclusions = 0
    else:
        exclusions = add(
            person, period, gov.irs.gross_income.fica_pre_tax_contributions
        )
    if rule == TAX_EXEMPT_WAGE_RULE:
        exclusions = exclusions + payroll_tax_exempt_income(
            person, period, system.parameters
        )
    return exclusions


class PayrollWageDefinition(NamedTuple):
    """Everything that sets which pay a system's payroll wages leave out.

    Two systems with equal definitions leave out the same pay for everyone
    (``payroll_wage_exclusions``): the rule, the FICA pre-tax list (``None``
    when abolished) and, under the tax-exempt rule, whether tips and overtime
    premiums are exempt.
    """

    rule: str
    fica_pre_tax_contributions: Optional[tuple]
    payroll_tax_exempt: tuple


def payroll_wage_definition(system, period):
    """The payroll wage definition of ``system`` in ``period``."""
    rule = payroll_wage_rule(system, period)
    gov = system.parameters(period).gov
    fica = None
    if not abolishes(gov, ["fica_pre_tax_contributions"]):
        fica = tuple(gov.irs.gross_income.fica_pre_tax_contributions)
    exempt = ()
    if rule == TAX_EXEMPT_WAGE_RULE:
        p = gov.contrib.tax_exempt
        exempt = (
            bool(p.tip_income.payroll_tax_exempt),
            bool(p.overtime.payroll_tax_exempt),
        )
    return PayrollWageDefinition(rule, fica, exempt)


class EmployerCostSchedule(NamedTuple):
    """Federal employer taxes as (rate, base) pairs, on payroll wages."""

    components: list
    wage_definition: PayrollWageDefinition


def employer_cost_schedules(baseline_system, reform_system, period, state_code):
    """The baseline and reform schedules the employer's cost is held across.

    The baseline's taxable maximum is the reform's copy of the current-law
    cap, ``gov.simulation.employer_payroll_tax_incidence.current_law_cap``:
    policy reforms leave it alone, while scenario reforms extend it with the
    live cap. It is this variable's own copy, so a policy that edits the
    owners' draw copy moves no wages.
    """
    reform_gov = reform_system.parameters(period).gov
    baseline = EmployerCostSchedule(
        federal_employer_payroll_tax_components(
            baseline_system.parameters(period).gov,
            state_code,
            cap=reform_gov.simulation.employer_payroll_tax_incidence.current_law_cap,
        ),
        payroll_wage_definition(baseline_system, period),
    )
    reform = EmployerCostSchedule(
        federal_employer_payroll_tax_components(reform_gov, state_code),
        payroll_wage_definition(reform_system, period),
    )
    return baseline, reform


def schedules_match(first, second):
    """Whether two schedules give every worker the same employer cost."""
    return first.wage_definition == second.wage_definition and components_match(
        first.components, second.components
    )


class employer_payroll_tax_fixed_employer_cost_change(Variable):
    value_type = float
    entity = Person
    label = "wage change from an employer payroll tax reform"
    documentation = (
        "The change in wages that holds the employer's cost of each worker "
        "fixed when a reform changes federal employer payroll taxes: the "
        "employer Social Security rate, taxable maximum or CBO secondary "
        "earnings threshold, the employer Medicare rate, the federal "
        "unemployment tax rate or wage base, or which pay counts as payroll "
        "wages (the tax-exempt reform's tips and overtime, and the list of "
        "FICA pre-tax contributions), including abolishing these taxes or the "
        "variables they are calculated from. The baseline cost "
        "is the worker's pay plus current-law federal employer taxes on it. "
        "The reformed pay is the one whose reformed federal employer taxes "
        "bring it to that cost, and "
        "gov.simulation.employer_payroll_tax_incidence.employee_share of the "
        "difference applies. The current-law taxable maximum is the reform's "
        "copy in gov.simulation.employer_payroll_tax_incidence.current_law_cap: "
        "policy reforms leave it alone, while scenario reforms such as the "
        "Trustees' economic assumptions extend it with the live cap, so a "
        "scenario is not read as a tax change. The cost leaves out state and local "
        "employer payroll taxes, which change with the new wage where they "
        "apply to it. Like the employer tax variables, it applies the taxable "
        "maximum and the federal unemployment wage base per person rather "
        "than per employer, and to all pay, including at employers exempt "
        "from federal unemployment tax and in public employment outside "
        "Social Security. CBO's secondary earnings threshold belongs in the "
        "reform a simulation is built with: the tax on earnings above it is "
        "a structural reform chosen at construction, while this variable "
        "reads the threshold each period. Zero without a reform "
        "(including a simulation built on a reformed tax-benefit system "
        "without one, which has no baseline), for a person with no pay, and "
        "when the reform leaves the federal employer taxes and the payroll "
        "wage definition unchanged. employment_income includes it, so income "
        "and employee payroll taxes respond to the new wage, and marginal "
        "tax rates measured in a reform count each added dollar of pay at "
        "its baseline cost to the employer. Programs that read "
        "employment_income_before_lsr, as some TANF and SNAP rules do, see "
        "neither this change nor the labor supply response, and a dataset "
        "that stores employment_income itself, rather than "
        "employment_income_before_lsr, overrides both."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.jct.gov/getattachment/df6ad7a8-d3f8-4f39-b465-1cbe5b077d20/x-89-16-4962.pdf#page=8",
    )

    def formula(person, period, parameters):
        share = parameters(
            period
        ).gov.simulation.employer_payroll_tax_incidence.employee_share
        baseline = person.simulation.baseline
        if share == 0 or baseline is None:
            return 0
        baseline_system = baseline.tax_benefit_system
        reform_system = person.simulation.tax_benefit_system
        baseline_schedule, reform_schedule = employer_cost_schedules(
            baseline_system,
            reform_system,
            period,
            person.household("state_code", period),
        )
        if schedules_match(baseline_schedule, reform_schedule):
            return 0
        # Pay before this change, as payroll_tax_gross_wages reads it from
        # employment_income.
        pay = person("employment_income_before_lsr", period) + person(
            "employment_income_behavioral_response", period
        )
        return fixed_employer_cost_wage_change(
            pay,
            payroll_wage_exclusions(
                person,
                period,
                baseline_system,
                baseline_schedule.wage_definition.rule,
            ),
            payroll_wage_exclusions(
                person, period, reform_system, reform_schedule.wage_definition.rule
            ),
            baseline_schedule.components,
            reform_schedule.components,
            share,
        )

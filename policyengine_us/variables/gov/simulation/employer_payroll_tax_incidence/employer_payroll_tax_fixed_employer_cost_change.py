from policyengine_us.model_api import *


def federal_employer_payroll_tax_components(gov, state_code):
    """Federal employer payroll taxes on payroll wages, as (rate, base) pairs.

    Each tax is ``rate * min(wages, base)``, as in
    ``employer_social_security_tax``, ``employer_medicare_tax`` and
    ``employer_federal_unemployment_tax``. The base is ``inf`` for the
    uncapped Medicare tax. The federal unemployment rate varies by state
    through its credit reduction, so it is an array.

    A finite ``gov.contrib.cbo.payroll.secondary_earnings_threshold`` turns on
    CBO's option to tax earnings above a second threshold as well as below the
    cap, which taxes ``rate * max(0, wages - threshold)`` more, with the
    threshold at least the cap. That is ``rate * wages - rate * min(wages,
    threshold)``, so it adds an uncapped component and a negative one.

    Args:
        gov: The ``gov`` parameter node for one period.
        state_code: Each person's state code.

    Returns:
        A list of (rate, base) pairs.
    """
    payroll = gov.irs.payroll
    social_security = payroll.social_security
    federal_unemployment = payroll.federal_unemployment
    components = [
        (social_security.rate.employer, social_security.cap),
        (payroll.medicare.rate.employer, np.inf),
        (
            federal_unemployment.effective_rate
            + federal_unemployment.credit_reduction_rate[state_code],
            federal_unemployment.taxable_wage_base,
        ),
    ]
    secondary_threshold = max(
        gov.contrib.cbo.payroll.secondary_earnings_threshold, social_security.cap
    )
    if np.isfinite(secondary_threshold):
        components += [
            (social_security.rate.employer, np.inf),
            (-social_security.rate.employer, secondary_threshold),
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
            bases must be scalars.

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
                "rising with wages: a segment's marginal cost is not positive."
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


class employer_payroll_tax_fixed_employer_cost_change(Variable):
    value_type = float
    entity = Person
    label = "wage change from an employer payroll tax reform"
    documentation = (
        "The change in wages that holds the employer's cost of each worker "
        "fixed when a reform changes federal employer payroll taxes: the "
        "employer Social Security rate, taxable maximum or CBO secondary "
        "earnings threshold, the employer Medicare rate, or the federal "
        "unemployment tax rate or wage base. "
        "The baseline cost is the worker's payroll wages plus the baseline "
        "federal employer taxes on them. The reformed wage is the one whose "
        "payroll wages plus reformed federal employer taxes equal that cost, "
        "and gov.simulation.employer_payroll_tax_incidence.employee_share of "
        "the difference applies. State and local employer payroll taxes are "
        "held at their baseline schedules, so the cost leaves out the small "
        "change in them that the new wage brings. Zero without a reform, for "
        "a person with no payroll wages, and when the reform leaves the "
        "federal employer taxes unchanged. employment_income includes it, so "
        "income and employee payroll taxes respond to the new wage."
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
        state_code = person.household("state_code", period)
        baseline_components = federal_employer_payroll_tax_components(
            baseline.tax_benefit_system.parameters(period).gov, state_code
        )
        reform_components = federal_employer_payroll_tax_components(
            parameters(period).gov, state_code
        )
        if components_match(baseline_components, reform_components):
            return 0
        # Payroll wages before this change, as payroll_tax_gross_wages
        # computes them from employment_income.
        pay = person("employment_income_before_lsr", period) + person(
            "employment_income_behavioral_response", period
        )
        wages = max_(pay - person("fica_pre_tax_contributions", period), 0)
        cost = wages + employer_payroll_tax_from_components(wages, baseline_components)
        new_wages = wages_at_employer_cost(cost, reform_components)
        # A cost of zero or more maps to wages of zero or more, so pay stays
        # at or above the FICA pre-tax deductions.
        return where(wages > 0, (new_wages - wages) * share, 0)

from policyengine_us.model_api import *


class ny_employee_disability_benefits_contribution(Variable):
    value_type = float
    entity = Person
    label = "New York employee disability benefits contribution"
    documentation = (
        "Employee-side New York Disability Benefits contribution. The "
        "employer is authorized, not required, to collect it by payroll "
        "deduction, up to 0.5 percent of wages and 60 cents a week, and pays "
        "the cost beyond what it collects (Workers' Compensation Law "
        "ss. 209(3)(a), (4) and 210(1)); this is that permitted amount, "
        "annualized from the weekly cap, times "
        "state_payroll_premium_deduction_share. The employer's cost of "
        "coverage is not modeled."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://www.nysenate.gov/legislation/laws/WKC/209",
        "https://www.nysenate.gov/legislation/laws/WKC/210",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.tax.payroll.disability_benefits
        uncapped = p.employee_rate * person(
            "ny_disability_benefits_taxable_wages", period
        )
        permitted = min_(uncapped, p.annual_max_contribution)
        return permitted * person("state_payroll_premium_deduction_share", period)

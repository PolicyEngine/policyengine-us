from policyengine_us.model_api import *


class nj_unemployment_insurance_dependency_allowance(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance dependency allowance rate"
    unit = "/1"
    documentation = "Dependency allowance rate for New Jersey unemployment insurance. The first dependent adds 7% to the weekly benefit rate, and each additional dependent (up to the maximum) adds 4%, with a maximum total allowance of 15%."
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # Get the number of dependents from the tax unit
        # NJ UI dependents include: unemployed spouse, children under 19
        # (or under 22 if in school), or disabled adult children
        # For simplicity, we use tax unit dependents as a proxy
        dependents = person.tax_unit("tax_unit_dependents", period)

        # Get parameters
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        first_dependent_rate = p.dependency_allowance_first
        additional_rate = p.dependency_allowance_additional
        max_rate = p.max_dependency_allowance
        max_dependents = p.max_dependents

        # Cap the number of dependents at the maximum
        capped_dependents = min_(dependents, max_dependents)

        # Calculate the allowance rate:
        # - First dependent: 7%
        # - Each additional dependent: 4%
        # - Maximum total: 15%
        has_dependents = capped_dependents > 0
        additional_dependents = where(
            capped_dependents > 1, capped_dependents - 1, 0
        )

        calculated_rate = where(
            has_dependents,
            first_dependent_rate + (additional_dependents * additional_rate),
            0,
        )

        return min_(calculated_rate, max_rate)

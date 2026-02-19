from policyengine_us.model_api import *


class nj_unemployment_insurance_dependency_allowance(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance dependency allowance rate"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # For simplicity, we use tax unit dependents as a proxy
        dependents = person.tax_unit("tax_unit_dependents", period)
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        capped_dependents = min_(dependents, p.max_dependents)
        has_dependents = capped_dependents > 0
        additional_dependents = where(
            capped_dependents > 1, capped_dependents - 1, 0
        )
        calculated_rate = where(
            has_dependents,
            p.dependency_allowance_first
            + (additional_dependents * p.dependency_allowance_additional),
            0,
        )
        return min_(calculated_rate, p.max_dependency_allowance)

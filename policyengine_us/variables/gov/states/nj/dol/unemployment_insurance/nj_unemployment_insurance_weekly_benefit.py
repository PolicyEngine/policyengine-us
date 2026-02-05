from policyengine_us.model_api import *


class nj_unemployment_insurance_weekly_benefit(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance weekly benefit"
    unit = USD
    documentation = "Final weekly unemployment insurance benefit for New Jersey, including the dependency allowance. The weekly benefit rate is increased by the dependency allowance percentage, but the total cannot exceed the maximum weekly benefit."
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/calculator/",
        "https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        wbr = person("nj_unemployment_insurance_weekly_benefit_rate", period)
        dependency_rate = person(
            "nj_unemployment_insurance_dependency_allowance", period
        )

        # Get parameters
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        max_weekly_benefit = p.max_weekly_benefit

        # Calculate benefit with dependency allowance
        # WBR * (1 + dependency_rate), capped at maximum
        benefit_with_dependency = wbr * (1 + dependency_rate)

        return min_(benefit_with_dependency, max_weekly_benefit)

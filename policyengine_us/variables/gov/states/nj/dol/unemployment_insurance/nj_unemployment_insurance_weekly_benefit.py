from policyengine_us.model_api import *


class nj_unemployment_insurance_weekly_benefit(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance weekly benefit"
    unit = USD
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
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        return min_(wbr * (1 + dependency_rate), p.max_weekly_benefit)

from policyengine_us.model_api import *


class nj_unemployment_insurance_dependency_allowance(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance dependency allowance rate"
    unit = "/1"
    documentation = (
        "Dependency benefits rely on the user-provided count of qualifying "
        "dependents at claim establishment. Phase-1 scope: the statutory "
        "rule allowing only one spouse to receive dependency benefits when "
        "both spouses establish claims is not derived in-model."
    )
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml",
        "https://www.nj.gov/labor/ea/help/employer_handbook/ui.shtml",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        qualifying_dependents = min_(
            person("nj_unemployment_insurance_qualifying_dependents", period),
            p.max_dependents,
        )
        spouse_employed = person(
            "nj_unemployment_insurance_spouse_employed_when_claim_established",
            period,
        )
        calculated_rate = where(
            qualifying_dependents > 0,
            p.dependency_allowance_first
            + max_(0, qualifying_dependents - 1) * p.dependency_allowance_additional,
            0,
        )
        return where(
            spouse_employed, 0, min_(calculated_rate, p.max_dependency_allowance)
        )

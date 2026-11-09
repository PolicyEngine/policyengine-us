from policyengine_us.model_api import *


class ak_permanent_fund_dividend_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Alaska Permanent Fund Dividend eligible"
    documentation = (
        "Applies the immigration status test in AS 43.23.005(a)(5). PolicyEngine "
        "has no inputs for the statute's other tests: an application, residence "
        "during all of the qualifying year, allowable absences, or a felony "
        "sentence or conviction-based incarceration during that year. To model "
        "a person who fails one of those, set "
        "takes_up_ak_permanent_fund_dividend_if_eligible to false. See "
        "docs/validation/alaska-pfd.md."
    )
    definition_period = YEAR
    reference = "https://www.akleg.gov/basis/statutes.asp#43.23.005"
    defined_for = StateCode.AK

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dor
        immigration_status = person("immigration_status", period)
        return np.isin(
            immigration_status.decode_to_str(),
            p.permanent_fund_dividend_eligible_immigration_statuses,
        )

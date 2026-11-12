from policyengine_us.model_api import *


class ak_energy_relief(Variable):
    value_type = float
    entity = Person
    label = "Alaska One Time Energy Relief"
    documentation = (
        "PolicyEngine calculates energy relief automatically for each Alaska "
        "resident who passes ak_permanent_fund_dividend_eligible and takes up "
        "the dividend (takes_up_ak_permanent_fund_dividend_if_eligible, true "
        "by default), since Alaska pays it as part of the dividend. The model "
        "does not otherwise check an application, prior-year residence, or "
        "actual receipt. Supplying "
        "other income does not disable the calculation. Override this "
        "person-level variable directly, which leaves "
        "ak_permanent_fund_dividend in place. To remove both Alaska payments "
        "for a person, set the take-up input to false. "
        "The rounded 2022 energy payment is $662, separate from the $2,622 "
        "regular PFD. Its exclusion from federal gross income follows the "
        "IRS's 2022 nonchallenge convention, which does not establish a "
        "statutory disaster-relief exclusion for every recipient or year. "
        "See docs/validation/alaska-pfd.md."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://pfd.alaska.gov"
    defined_for = "ak_permanent_fund_dividend_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dor
        takes_up = person("takes_up_ak_permanent_fund_dividend_if_eligible", period)
        return p.energy_relief * takes_up

from policyengine_us.model_api import *


class ak_permanent_fund_dividend(Variable):
    value_type = float
    entity = Person
    label = "Alaska Permanent Fund Dividend"
    documentation = (
        "PolicyEngine calculates the regular PFD automatically for each Alaska "
        "resident who passes ak_permanent_fund_dividend_eligible and takes up "
        "the dividend (takes_up_ak_permanent_fund_dividend_if_eligible, true "
        "by default). "
        "The model does not otherwise check an application, prior-year "
        "residence, or actual receipt. Supplying wages or other income does "
        "not disable this calculation. Supply this "
        "person-level variable to override it, which leaves ak_energy_relief "
        "in place. To remove both Alaska payments for a person, set the "
        "take-up input to false. "
        "A dependent child's PFD is not automatically included in a parent's "
        "AGI. In 2022 this variable is the rounded $2,622 taxable regular "
        "dividend; the separate $662 energy payment follows the IRS's 2022 "
        "nonchallenge convention. See docs/validation/alaska-pfd.md."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://pfd.alaska.gov"
    defined_for = "ak_permanent_fund_dividend_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dor
        takes_up = person("takes_up_ak_permanent_fund_dividend_if_eligible", period)
        return p.permanent_fund_dividend * takes_up

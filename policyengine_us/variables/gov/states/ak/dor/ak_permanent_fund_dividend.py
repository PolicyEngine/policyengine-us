from policyengine_us.model_api import *


class ak_permanent_fund_dividend(Variable):
    value_type = float
    entity = Person
    label = "Alaska Permanent Fund Dividend"
    documentation = (
        "Regular PFD calculated automatically for each Alaska resident, using "
        "current residence as an eligibility proxy without checking an "
        "application, prior-year residence, or actual receipt. Supplying wages "
        "or other income does not disable this calculation. Supply this "
        "person-level variable to override it; to exclude both Alaska "
        "transfers, also supply ak_energy_relief as zero for every person. "
        "A dependent child's PFD is not automatically included in a parent's "
        "AGI. In 2022 this variable is the rounded $2,622 taxable regular "
        "dividend; the separate $662 energy payment follows the IRS's 2022 "
        "nonchallenge convention. See docs/validation/alaska-pfd.md."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://pfd.alaska.gov"
    defined_for = StateCode.AK

    adds = ["gov.states.ak.dor.permanent_fund_dividend"]

from policyengine_us.model_api import *


class ak_energy_relief(Variable):
    value_type = float
    entity = Person
    label = "Alaska One Time Energy Relief"
    documentation = (
        "Energy relief calculated automatically for each Alaska resident, "
        "using current residence as an eligibility proxy without checking an "
        "application, prior-year residence, or actual receipt. Supplying "
        "other income does not disable the calculation. Override this "
        "person-level variable directly; excluding both Alaska transfers "
        "requires also overriding ak_permanent_fund_dividend for each person. "
        "The rounded 2022 energy payment is $662, separate from the $2,622 "
        "regular PFD. Its exclusion from federal gross income follows the "
        "IRS's 2022 nonchallenge convention, which does not establish a "
        "statutory disaster-relief exclusion for every recipient or year. "
        "See docs/validation/alaska-pfd.md."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://pfd.alaska.gov"
    defined_for = StateCode.AK

    adds = ["gov.states.ak.dor.energy_relief"]

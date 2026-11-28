from policyengine_us.model_api import *


class railroad_benefits_retroactive_lump_sum(Variable):
    value_type = float
    entity = Person
    label = "Retroactive Railroad Retirement lump-sum payments"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Annual amount of Railroad Retirement annuities received as retroactive "
        "lump sums. Include these payments in railroad_benefits."
    )
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40019/400_19_55_25.htm",
        "https://ndlegis.gov/prod/acdata/pdf/75-02-01.3.pdf#page=5",
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/",
    )

from policyengine_us.model_api import *


class mi_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan CDC countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/503.pdf#page=31",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/502.pdf#page=3",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/500.pdf#page=9",
    )

    # BEM 703: counts gross monthly income of the program group. Grandparent
    # and guardian P/SP income is excluded by BEM 703, but we don't track the
    # relationship of each adult to the child at the moment, so all program
    # group income is counted.
    adds = "gov.states.mi.mdhhs.ccap.income.countable_income.sources"

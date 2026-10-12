from policyengine_us.model_api import *


class wi_cts_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS individual gross countable income"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "All child support is excluded. Override for income sources or deeming absent from the modeled SSI cash-income sources. SSI recipients are excluded from the filing unit."

    def formula(person, period, parameters):
        return max_(person("ssi_earned_income", period), 0) + max_(
            person("ssi_unearned_income", period)
            - person("child_support_received", period),
            0,
        )

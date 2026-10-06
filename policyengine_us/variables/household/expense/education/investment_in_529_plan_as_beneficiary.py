from policyengine_us.model_api import *


class investment_in_529_plan_as_beneficiary(Variable):
    value_type = float
    entity = Person
    label = (
        "529 plan contributions made for this person by the tax unit's head and spouse"
    )
    unit = USD
    documentation = (
        "Amount the head and spouse of this person's tax unit together "
        "contributed during the year to 529 savings plans for which this "
        "person is the beneficiary. These contributions are also part of the "
        "head's and spouse's own investment_in_529_plan_indv. States that "
        "limit the deduction per beneficiary use it to apply the limit to "
        "each beneficiary in the tax unit."
    )
    definition_period = YEAR

from policyengine_us.model_api import *


class claimed_as_dependent_on_another_return(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is claimed as a dependent elsewhere"
    documentation = (
        "Whether another taxpayer can claim the person as a dependent, that "
        "is, a deduction under IRC section 151 for the person is allowable to "
        "another taxpayer, whether or not it is claimed. A person whose "
        "would-be claimer is not required to file and files only to claim a "
        "refund is not such a dependent (IRS Publications 501 and 596). Rules "
        "that turn on actually being claimed also read this input; the model "
        "has no separate input for that."
    )

from policyengine_us.model_api import *


class takes_up_part_d_lis_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Whether an eligible person enrolls in the Medicare Part D low-income subsidy"
    )
    documentation = (
        "Whether an eligible person who is neither a Medicaid enrollee nor a "
        "Supplemental Security Income recipient applies for the subsidy. "
        "Medicare Savings Program enrollees are deemed eligible, but the "
        "model has Medicare Savings Program eligibility, not enrollment, so "
        "this flag covers them too. The subsidy also requires enrollment in "
        "a Part D plan (medicare_part_d_enrolled)."
    )
    definition_period = YEAR
    default_value = True

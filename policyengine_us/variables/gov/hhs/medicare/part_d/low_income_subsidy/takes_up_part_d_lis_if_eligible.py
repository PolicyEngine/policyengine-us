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
        "a Part D plan (medicare_part_d_enrolled); part_d_lis_enrolled "
        "describes when CMS enrolls subsidy-eligible people who don't choose "
        "a plan, and the exception for qualifying covered retirees (42 CFR "
        "423.34(d)). The default, true, takes everyone up; microdata can set "
        "a take-up rate."
    )
    definition_period = YEAR
    default_value = True

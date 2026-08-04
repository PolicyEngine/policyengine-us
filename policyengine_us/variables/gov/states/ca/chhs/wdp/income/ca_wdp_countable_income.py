from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ca_wdp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "California 250 Percent Working Disabled Program countable income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Countable income for California's 250% Working Disabled Program. "
        "This applies SSI earned-income exclusions to earned income and "
        "excludes modeled disability income from unearned income. Retained "
        "earned income accounts and converted retirement-income edge cases are "
        "not modeled."
    )
    reference = (
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/medi-cal/non-magi/250-percent-wdp.html",
        "https://stgenssa.sccgov.org/debs/program_handbooks/medi-cal/assets/26250WDP/250WDP.htm",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        earned_income = person("ca_wdp_gross_earned_income", period)
        unearned_income = person("ssi_unearned_income", period)
        disability_income = person("ca_wdp_disability_income", period)
        non_exempt_unearned_income = max_(unearned_income - disability_income, 0)
        return _apply_ssi_exclusions(
            earned_income,
            non_exempt_unearned_income,
            parameters,
            period,
        )

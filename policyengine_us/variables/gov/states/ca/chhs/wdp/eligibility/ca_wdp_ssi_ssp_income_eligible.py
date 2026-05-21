from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ca_wdp_ssi_ssp_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California 250 Percent Working Disabled Program SSI/SSP income eligible"
    definition_period = YEAR
    documentation = (
        "Whether this person passes a first-pass SSI/SSP income screen for "
        "California's 250% Working Disabled Program after disregarding modeled "
        "earned income and modeled disability income. This approximates the "
        "program requirement that a person would be SSI/SSP-eligible if not "
        "for earned income; full SSI/SSP deeming is not modeled here."
    )
    reference = (
        "https://www.dhcs.ca.gov/services/working-disabled-program/",
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/medi-cal/non-magi/250-percent-wdp.html",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        unearned_income = person("ssi_unearned_income", period)
        disability_income = person("ca_wdp_disability_income", period)
        non_exempt_unearned_income = max_(unearned_income - disability_income, 0)
        countable_unearned_income = _apply_ssi_exclusions(
            0,
            non_exempt_unearned_income,
            parameters,
            period,
        )

        p = parameters(
            period.first_month
        ).gov.states.ca.cdss.state_supplement.payment_standard
        is_joint = person.tax_unit("tax_unit_is_joint", period)
        monthly_standard = where(
            is_joint,
            p.aged_or_disabled.amount.married,
            p.aged_or_disabled.amount.single,
        )
        return countable_unearned_income < monthly_standard * MONTHS_IN_YEAR

from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)


class medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled income deemed from ineligible spouse"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-05/",
    )
    defined_for = "is_ssi_eligible_individual"
    unit = USD

    def formula(person, period, parameters):
        deeming_applies = person("is_ssi_spousal_deeming_applies", period)
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )
        individual_earned = person("ssi_earned_income", period)
        individual_unearned = person("ssi_unearned_income", period)

        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.disregard
        state = person.household("state_code_str", period)

        # Missouri MHABD considers the gross income of a married couple
        # living together (DSS Manual § 0805.015.05) rather than the SSI
        # deeming methodology: the spouse's income counts without the
        # FBR-differential threshold or ineligible-child allocations.
        is_mo = state == "MO"
        marital_unit = person.marital_unit
        ineligible_spouse = person("is_ssi_ineligible_spouse", period)
        spouse_gross_earned = (
            marital_unit.sum(ineligible_spouse * individual_earned)
            - ineligible_spouse * individual_earned
        )
        spouse_gross_unearned = (
            marital_unit.sum(ineligible_spouse * individual_unearned)
            - ineligible_spouse * individual_unearned
        )
        spouse_earned = where(is_mo, spouse_gross_earned, spouse_earned)
        spouse_unearned = where(is_mo, spouse_gross_unearned, spouse_unearned)
        has_ineligible_spouse = marital_unit.sum(ineligible_spouse) > 0
        deeming_applies = deeming_applies | (is_mo & has_ineligible_spouse)

        alone_countable = _apply_medicaid_optional_senior_or_disabled_exclusions(
            individual_earned,
            individual_unearned,
            state,
            p.individual[state],
            parameters,
            period,
        )
        couple_countable = _apply_medicaid_optional_senior_or_disabled_exclusions(
            individual_earned + spouse_earned,
            individual_unearned + spouse_unearned,
            state,
            p.couple[state],
            parameters,
            period,
        )

        deemed_amount = max_(0, couple_countable - alone_countable)
        return deeming_applies * deemed_amount

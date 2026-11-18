from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._couple_standard import (
    spouses_split_by_facility,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)

from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)


class medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse_monthly(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled income deemed from ineligible spouse"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://www.law.cornell.edu/uscode/text/42/1396r-5",
        "https://epm.azahcccs.gov/epmplus/Policy/Chapter_600_Income_Eligibility/611_How_to_Calculate_Income_Eligibility_for_SSIMAO/611A.htm",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-05/",
    )
    unit = USD

    def formula(person, period, parameters):
        supplied = annual_input(
            person,
            period,
            "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse",
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR

        deeming_applies = person("is_ssi_spousal_deeming_applies_monthly", period)
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse_monthly", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse_monthly", period
        )
        individual_earned = person("ssi_earned_income", period)
        individual_unearned = person("ssi_unearned_income", period)

        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.disregard
        state = person.household("state_code_str", period)

        # Some states budget a married couple living together: the spouse's
        # income counts without SSI's FBR-differential threshold. The spouse's
        # income is still what remains after the allocations for ineligible
        # children in 20 CFR 416.1163(b), which Arizona's MA611 A also
        # subtracts. Missouri MHABD alone considers the couple's gross income
        # and does "not consider the income and expenses of minor children"
        # (DSS Manual § 0805.015.05), so no allocation comes off there.
        budgets_together = (
            parameters(period)
            .gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.budgets_couple_together[
                state
            ]
            .astype(bool)
        )
        ineligible_spouse = person("is_ssi_ineligible_spouse", period)
        spouse_gross_earned = (
            _ssi_couple_total(person, period, ineligible_spouse * individual_earned)
            - ineligible_spouse * individual_earned
        )
        spouse_gross_unearned = (
            _ssi_couple_total(person, period, ineligible_spouse * individual_unearned)
            - ineligible_spouse * individual_unearned
        )
        is_mo = state == "MO"
        spouse_earned = where(is_mo, spouse_gross_earned, spouse_earned)
        spouse_unearned = where(is_mo, spouse_gross_unearned, spouse_unearned)
        has_ineligible_spouse = _ssi_couple_total(person, period, ineligible_spouse) > 0
        # A couple split by a facility counts no spouse income under either method
        # (42 USC 1396r-5(b)(1)).
        deeming_applies = (
            deeming_applies | (budgets_together & has_ineligible_spouse)
        ) & ~spouses_split_by_facility(person, period)

        alone_countable = (
            _apply_medicaid_optional_senior_or_disabled_exclusions(
                individual_earned * MONTHS_IN_YEAR,
                individual_unearned * MONTHS_IN_YEAR,
                state,
                p.individual[state],
                parameters,
                period,
            )
            / MONTHS_IN_YEAR
        )
        couple_countable = (
            _apply_medicaid_optional_senior_or_disabled_exclusions(
                (individual_earned + spouse_earned) * MONTHS_IN_YEAR,
                (individual_unearned + spouse_unearned) * MONTHS_IN_YEAR,
                state,
                p.couple[state],
                parameters,
                period,
            )
            / MONTHS_IN_YEAR
        )

        deemed_amount = max_(0, couple_countable - alone_countable)
        return where(
            person("is_ssi_aged_blind_disabled", period),
            deeming_applies * deemed_amount,
            0,
        )

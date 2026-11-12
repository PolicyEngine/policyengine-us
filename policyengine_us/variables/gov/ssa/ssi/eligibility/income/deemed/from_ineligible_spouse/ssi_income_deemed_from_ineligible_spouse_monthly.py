from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions_monthly,
)


class ssi_income_deemed_from_ineligible_spouse_monthly(Variable):
    value_type = float
    entity = Person
    label = "Monthly SSI income deemed from an ineligible spouse"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1163.htm",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320150",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320400",
    )
    documentation = (
        "Monthly combined countable income less the claimant's own countable "
        "income when spousal deeming applies. Both budgets include the "
        "claimant's in-kind support before applying one general exclusion. "
        "Supplied legacy annual deemed income takes precedence."
    )

    def formula(person, period, parameters):
        supplied = annual_input(
            person, period, "ssi_income_deemed_from_ineligible_spouse"
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR

        deeming_applies = person("is_ssi_spousal_deeming_applies", period.this_year)
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )
        individual_earned = person("ssi_earned_income", period)
        # SI 01320.150 B.1.a counts the claimant's ISM in combined unearned
        # income. Include it in both budgets so their difference adds no
        # second general exclusion when ssi_countable_income counts ISM.
        individual_unearned = person("ssi_unearned_income", period) + person(
            "ssi_in_kind_support_and_maintenance", period
        )
        alone_countable = _apply_ssi_exclusions_monthly(
            individual_earned, individual_unearned, parameters, period
        )
        couple_countable = _apply_ssi_exclusions_monthly(
            individual_earned + spouse_earned,
            individual_unearned + spouse_unearned,
            parameters,
            period,
        )
        deemed_amount = max_(0, couple_countable - alone_countable)
        return where(
            person("is_ssi_aged_blind_disabled", period),
            deeming_applies * deemed_amount,
            0,
        )

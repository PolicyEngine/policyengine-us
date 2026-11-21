from policyengine_us.model_api import *


class nm_modified_gross_income_long_term_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "New Mexico modified gross income long-term capital gains"
    unit = USD
    documentation = (
        "A person's long-term capital gain or loss for the year, before the "
        "prior-year long-term capital loss carryover, for New Mexico modified "
        "gross income. Modified gross income counts gross capital gains, not "
        "reduced by capital losses, so the carryover that "
        "long_term_capital_gains nets (as Schedule D line 15 does) is added "
        "back. nm_modified_gross_income floors this amount at zero for each "
        "person, apart from short-term gains, so only the gain the carryover "
        "hid is restored, never the unused loss. Short-term inputs must hold "
        "only the year's own gains and losses; no short-term carryover memo "
        "is modeled. Losses netted inside one input cannot be separated."
    )
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503656",
        "https://taxsim.nber.org/historical_state_tax_forms/NM/2025/NM_PIT_RC_INST.PDF#page=4",
        "https://www.law.cornell.edu/regulations/new-mexico/N-M-Admin-Code-SS-3.3.1.10",
        "https://www.law.cornell.edu/uscode/text/26/1212#b_1_B",
    )
    defined_for = StateCode.NM

    def formula(person, period, parameters):
        # NMSA 1978 § 7-2-2(L): income "undiminished by losses"; PIT-RC line
        # 9: "Do not reduce them by capital losses." long_term_capital_gains
        # includes the carryover (26 U.S.C. 1212(b)(1)(B)) as a loss, so
        # adding it back gives the year's own long-term gain or loss.
        carryover = max_(0, person("long_term_capital_loss_carryover", period))
        return person("long_term_capital_gains", period) + carryover

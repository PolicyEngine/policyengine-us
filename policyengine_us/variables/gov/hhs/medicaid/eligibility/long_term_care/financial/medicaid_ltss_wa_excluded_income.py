from policyengine_us.model_api import *


class medicaid_ltss_wa_excluded_income(Variable):
    value_type = float
    entity = Person
    label = "Washington Medicaid LTSS modeled income exclusions"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Derives the WAC 182-513-1340 exclusions represented by the "
        "screen's source facts: SSI, qualifying state needs-based public "
        "assistance, and the institutionally classified applicant's "
        "interest and dividends. Institutional status includes the modeled "
        "Washington HCBS waivers under WAC 182-513-1320; investment "
        "income remains income of a nonapplying community spouse. "
        "These exclusions apply before both the special-income-limit "
        "comparison under WAC 182-513-1317(2) and the medically needy "
        "income calculation. The total is capped at remaining unearned "
        "income. Other source, qualification, or expense distinctions "
        "required by WAC 182-513-1340 cannot be inferred from aggregate "
        "monthly gross income. Many excluded receipts already lie "
        "outside the annual-source gross default."
    )
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1317",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1320",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1340",
    )

    def formula_2026_01_01(person, period, parameters):
        state = person.household("state_code", period)
        setting = person("medicaid_ltss_setting", period)
        settings = setting.possible_values
        waiver = person("medicaid_ltss_waiver", period)
        waivers = waiver.possible_values
        institutional_status = (setting == settings.INSTITUTIONAL) | (
            (setting == settings.HCBS)
            & (
                (waiver == waivers.WA_COPES)
                | (waiver == waivers.WA_NEW_FREEDOM)
                | (waiver == waivers.WA_RSW)
            )
        )
        investment_income = max_(
            person("medicaid_ltss_interest_income", period), 0
        ) + max_(person("medicaid_ltss_dividend_income", period), 0)
        public_assistance = max_(person("medicaid_ltss_ssi_income", period), 0) + max_(
            person("medicaid_ltss_state_needs_based_public_assistance_income", period),
            0,
        )
        excluded = public_assistance + where(institutional_status, investment_income, 0)
        unearned = max_(person("medicaid_ltss_qit_adjusted_unearned_income", period), 0)
        return where(state == state.possible_values.WA, min_(excluded, unearned), 0)

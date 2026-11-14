from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


def _sctc_income_facts(tax_unit, period):
    agi = tax_unit("adjusted_gross_income", period)
    amt = tax_unit("alternative_minimum_tax", period)
    family_size = tax_unit("wv_sctc_family_unit_size", period)
    confirmed = tax_unit("wv_sctc_income_facts_available", period)
    valid = (
        confirmed
        & np.isfinite(agi)
        & np.isfinite(amt)
        & (amt >= 0)
        & (family_size >= 1)
    )
    return valid, agi, amt, family_size


def _sctc_eligibility_facts(tax_unit, period, parameters):
    income_known, agi, amt, family_size = _sctc_income_facts(tax_unit, period)
    p = parameters(period).gov.states.wv.tax.income.credits.sctc
    state_group = tax_unit.household("state_group_str", period)
    income_limit = p.fpg_percentage * fpg(
        max_(family_size, 1), state_group, period, parameters
    )
    income_eligible = agi <= income_limit
    homestead_known = tax_unit("wv_sctc_homestead_facts_available", period)
    homestead_qualified = tax_unit("wv_sctc_homestead_qualified", period)
    dv_claim = tax_unit("wv_sctc_disabled_veteran_credit_claim_status", period)
    dv_claimed = dv_claim == dv_claim.possible_values.CLAIMED
    dv_not_claimed = dv_claim == dv_claim.possible_values.NOT_CLAIMED
    known_ineligible = (
        (homestead_known & ~homestead_qualified)
        | (income_known & (~income_eligible | (amt > 0)))
        | dv_claimed
    )
    known_eligible = (
        homestead_known
        & homestead_qualified
        & income_known
        & income_eligible
        & (amt == 0)
        & dv_not_claimed
    )
    return known_ineligible, known_eligible


class wv_sctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia senior citizens tax credit"
    reference = (
        "https://code.wvlegislature.gov/11-21-21/",
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=36",
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=27",
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=35",
    )
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        wv_homestead_exemption = tax_unit("wv_homestead_exemption", period)

        p_sctc = parameters(period).gov.states.wv.tax.income.credits.sctc
        p_homestead = parameters(
            period
        ).gov.states.wv.tax.income.exemptions.homestead_exemption

        fpg = tax_unit("tax_unit_fpg", period)
        income_threshold = p_sctc.fpg_percentage * fpg

        meets_agi_condition = federal_agi <= income_threshold
        meets_homestead_exemption_condition = (
            wv_homestead_exemption == p_homestead.max_amount
        )

        return meets_agi_condition & meets_homestead_exemption_condition

    def formula_2025_01_01(tax_unit, period, parameters):
        _, known_eligible = _sctc_eligibility_facts(tax_unit, period, parameters)
        return known_eligible

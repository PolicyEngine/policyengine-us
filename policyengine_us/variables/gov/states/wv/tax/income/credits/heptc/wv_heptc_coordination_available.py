from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wv.tax.income.credits.sctc.wv_sctc_eligible import (
    _sctc_income_facts,
)


class wv_heptc_coordination_available(Variable):
    """Availability of SCTC, AMT and DV coordination, not complete HEPTC eligibility."""

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia HEPTC credit coordination can be determined"
    reference = (
        "https://code.wvlegislature.gov/11-21-23/",
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=11",
    )
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        income_known, _, amt, _ = _sctc_income_facts(tax_unit, period)
        dv_claim = tax_unit("wv_sctc_disabled_veteran_credit_claim_status", period)
        dv_claimed = dv_claim == dv_claim.possible_values.CLAIMED
        dv_not_claimed = dv_claim == dv_claim.possible_values.NOT_CLAIMED
        shared_bar = (income_known & (amt > 0)) | dv_claimed
        senior_amount_known = tax_unit("wv_sctc_amount_available", period)
        return shared_bar | (
            senior_amount_known & income_known & (amt == 0) & dv_not_claimed
        )

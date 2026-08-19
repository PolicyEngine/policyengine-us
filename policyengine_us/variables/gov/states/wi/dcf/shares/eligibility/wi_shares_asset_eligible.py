from policyengine_us.model_api import *


class wi_shares_asset_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Shares asset eligible"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=64",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/1m/cm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.eligibility
        # Only liquid assets are included in the self-declared asset test
        # (Section 6.5); the statutory home value and vehicle equity limits
        # (Wis. Stat. § 49.155(1m)(cr)) are not part of the operational test.
        assets = spm_unit("spm_unit_cash_assets", period.this_year)
        # Foster parents are exempt from the asset test; the other exempt
        # categories (subsidized guardians, interim caretakers, court-ordered
        # kinship relatives, and tribal placement homes) are not tracked at
        # the moment (Section 6.5).
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return (assets <= p.asset_limit) | has_foster_child

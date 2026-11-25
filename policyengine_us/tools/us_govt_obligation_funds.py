"""Per-fund inputs for state subtractions of mutual fund dividends that are
attributable to interest on U.S. government obligations.

PolicyEngine has no entity for a single holding, so each person carries a
fixed number of fund slots. Each slot describes one regulated investment
company (mutual fund, ETF or money market fund) held in a taxable account:

- ``us_govt_fund_<n>_ordinary_dividends``: the fund's ordinary dividends for
  the year (Form 1099-DIV box 1a, which excludes capital gain distributions).
  These dividends must already be in the person's dividend inputs
  (``qualified_dividend_income`` or ``non_qualified_dividend_income``). The
  slot is a memo line that says which part of those dividends came from the
  fund; it never adds income.
- ``us_govt_fund_<n>_govt_income_share``: the share of the fund's ordinary
  dividends attributable to interest on U.S. government obligations, as the
  fund reports it in its annual tax supplement. It sets the size of the
  subtraction, never eligibility.
- ``us_govt_fund_<n>_govt_asset_share_q1`` to ``_q4``: the share of the
  value of the fund's total assets (IRC 851(c)(4)) held in qualifying U.S.
  government obligations at the close of each quarter of the fund's taxable
  year. These set eligibility, never the size of the subtraction.
- ``us_govt_fund_<n>_asset_test_evidence``: which evidence establishes the
  asset test (quarterly shares, or the issuer's own statement that the fund
  met or did not meet it).
- ``us_govt_fund_<n>_qualified_fund_of_funds``: whether the fund is a
  qualified fund of funds under IRC 852(g)(2), which California exempts from
  its asset test.

Missing data fails the asset test: every quarterly share defaults to 0, and a
fund qualifies only on four quarter-end shares at or above the threshold or
on the issuer's statement that it met the test. An income share alone, of
any size, never qualifies a fund.
"""

import numpy as np
from policyengine_core.enums import Enum

# The number of fund slots per person. Funds beyond this number need a
# second person or a larger constant; each slot is applied separately, so
# funds must never be merged into one slot.
US_GOVT_OBLIGATION_FUND_SLOTS = 10

US_GOVT_FUND_QUARTERS = (1, 2, 3, 4)


class USGovtFundAssetTestEvidence(Enum):
    QUARTERLY_ASSET_SHARES = "Quarter-end asset shares supplied for each quarter"
    ISSUER_CONFIRMED_MET = "Fund issuer states the fund met the quarterly test"
    ISSUER_CONFIRMED_NOT_MET = (
        "Fund issuer states the fund did not meet the quarterly test"
    )


def us_govt_fund_variable(slot: int, field: str) -> str:
    return f"us_govt_fund_{slot}_{field}"


def us_govt_fund_eligible_dividends(
    person,
    period,
    asset_threshold,
    qualified_fund_of_funds_exempt=False,
):
    """Sum, over a person's fund slots, the ordinary dividends attributable
    to U.S. government obligations from funds that pass a state's asset test.

    Each fund is tested on its own: a fund passes when the issuer states it
    met the test, or when the quarterly-shares evidence is chosen and the
    share at the close of every quarter is at least ``asset_threshold``.
    When ``qualified_fund_of_funds_exempt`` is true, a qualified fund of
    funds passes without the asset test. A passing fund contributes its
    ordinary dividends times its income share; a failing fund contributes
    nothing.
    """
    evidence_values = USGovtFundAssetTestEvidence
    total = 0
    for slot in range(1, US_GOVT_OBLIGATION_FUND_SLOTS + 1):
        dividends = np.maximum(
            person(us_govt_fund_variable(slot, "ordinary_dividends"), period),
            0,
        )
        income_share = np.clip(
            person(us_govt_fund_variable(slot, "govt_income_share"), period),
            0,
            1,
        )
        evidence = person(us_govt_fund_variable(slot, "asset_test_evidence"), period)
        meets_every_quarter = True
        for quarter in US_GOVT_FUND_QUARTERS:
            asset_share = person(
                us_govt_fund_variable(slot, f"govt_asset_share_q{quarter}"),
                period,
            )
            meets_every_quarter = meets_every_quarter & (asset_share >= asset_threshold)
        passes_on_quarterly_shares = (
            evidence == evidence_values.QUARTERLY_ASSET_SHARES
        ) & meets_every_quarter
        passes_on_issuer_statement = evidence == evidence_values.ISSUER_CONFIRMED_MET
        passes = passes_on_quarterly_shares | passes_on_issuer_statement
        if qualified_fund_of_funds_exempt:
            passes = passes | person(
                us_govt_fund_variable(slot, "qualified_fund_of_funds"), period
            )
        total = total + passes * dividends * income_share
    return total


def us_govt_fund_state_subtraction(
    person,
    period,
    asset_threshold,
    qualified_fund_of_funds_exempt=False,
):
    """A person's state subtraction for fund dividends attributable to U.S.
    government obligations, capped at the ordinary dividends included in
    federal gross income. Dividends earned inside an IRA or other retirement
    account are not in ordinary dividend income, so the cap keeps a misfiled
    retirement-account fund from producing a subtraction.
    """
    eligible = us_govt_fund_eligible_dividends(
        person, period, asset_threshold, qualified_fund_of_funds_exempt
    )
    ordinary_dividends = np.maximum(person("ordinary_dividend_income", period), 0)
    return np.minimum(eligible, ordinary_dividends)

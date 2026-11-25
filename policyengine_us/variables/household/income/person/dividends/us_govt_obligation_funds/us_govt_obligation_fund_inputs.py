"""Per-fund input slots for dividends attributable to U.S. government
obligations. See policyengine_us/tools/us_govt_obligation_funds.py for the
meaning of each field and the missing-data rule.

The slots are built in a loop so every slot carries identical metadata; each
generated class is a plain input variable named, for example,
``us_govt_fund_1_ordinary_dividends``.
"""

from policyengine_us.model_api import *
from policyengine_us.tools.us_govt_obligation_funds import (
    US_GOVT_FUND_QUARTERS,
    US_GOVT_OBLIGATION_FUND_SLOTS,
    USGovtFundAssetTestEvidence,
    us_govt_fund_variable,
)

_REFERENCE = (
    # Cal. Rev. & Tax. Code § 17145(a), (b)(4), (d)
    "https://law.justia.com/codes/california/code-rtc/division-2/part-10/chapter-3/article-3/section-17145/",
    # Conn. Gen. Stat. § 12-718
    "https://law.justia.com/codes/connecticut/title-12/chapter-229/section-12-718/",
    # N.Y. Tax Law § 612(c)(1)
    "https://newyork.public.law/laws/n.y._tax_law_section_612",
)


def _input_class(name, attributes):
    attributes = {
        "entity": Person,
        "definition_period": YEAR,
        "reference": _REFERENCE,
        "__module__": __name__,
        **attributes,
    }
    globals()[name] = type(name, (Variable,), attributes)


for _slot in range(1, US_GOVT_OBLIGATION_FUND_SLOTS + 1):
    _input_class(
        us_govt_fund_variable(_slot, "ordinary_dividends"),
        dict(
            value_type=float,
            unit=USD,
            label=f"Ordinary dividends from U.S. government obligation fund {_slot}",
            documentation=(
                "Ordinary dividends (Form 1099-DIV box 1a, excluding capital "
                "gain distributions) the person received in a taxable account "
                f"from fund {_slot}. A memo of dividends already reported in "
                "qualified_dividend_income or non_qualified_dividend_income; "
                "it does not add income. Leave out dividends earned inside an "
                "IRA, 401(k) or other retirement account."
            ),
        ),
    )
    _input_class(
        us_govt_fund_variable(_slot, "govt_income_share"),
        dict(
            value_type=float,
            unit="/1",
            label=f"U.S. government obligation income share of fund {_slot}",
            documentation=(
                "Share of the fund's ordinary dividends attributable to "
                "interest on U.S. government obligations, from the fund's "
                "annual tax supplement. Sets the subtraction amount only; it "
                "never shows that the fund passed a state's asset test."
            ),
        ),
    )
    for _quarter in US_GOVT_FUND_QUARTERS:
        _input_class(
            us_govt_fund_variable(_slot, f"govt_asset_share_q{_quarter}"),
            dict(
                value_type=float,
                unit="/1",
                label=(
                    f"U.S. government obligation asset share of fund {_slot} "
                    f"at the close of fiscal quarter {_quarter}"
                ),
                documentation=(
                    "Share of the value of the fund's total assets (IRC "
                    "851(c)(4)) held in U.S. government obligations whose "
                    "interest states may not tax under federal law, at the "
                    f"close of quarter {_quarter} of the fund's taxable year. "
                    "Excludes repurchase agreements and Ginnie Mae, Fannie Mae "
                    "and Freddie Mac securities. Defaults to 0, which fails "
                    "the asset test, so missing data never qualifies a fund."
                ),
            ),
        )
    _input_class(
        us_govt_fund_variable(_slot, "asset_test_evidence"),
        dict(
            value_type=Enum,
            possible_values=USGovtFundAssetTestEvidence,
            default_value=USGovtFundAssetTestEvidence.QUARTERLY_ASSET_SHARES,
            label=f"Evidence for the asset test of fund {_slot}",
            documentation=(
                "QUARTERLY_ASSET_SHARES tests the four quarter-end asset "
                "shares. ISSUER_CONFIRMED_MET or ISSUER_CONFIRMED_NOT_MET uses "
                "the issuer's explicit statement that the fund did or did not "
                "meet the quarterly 50% test for California, Connecticut and "
                "New York; never infer it from the income share."
            ),
        ),
    )
    _input_class(
        us_govt_fund_variable(_slot, "qualified_fund_of_funds"),
        dict(
            value_type=bool,
            default_value=False,
            label=f"Fund {_slot} is a qualified fund of funds",
            documentation=(
                "Whether the fund is a qualified fund of funds under IRC "
                "852(g)(2): at least 50% of the value of its total assets is "
                "in other regulated investment companies at the close of "
                "each quarter. California exempts such a fund from its asset "
                "test; Connecticut and New York do not."
            ),
        ),
    )

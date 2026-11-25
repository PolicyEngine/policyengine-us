"""Lot-level inputs for holding-period, wash-sale, RIC loss and bond
discount rules. Amounts entered here must be left out of the aggregate
inputs they adjust (short_term_capital_gains, long_term_capital_gains,
qualified and non-qualified dividends, taxable_interest_income);
policyengine_us.tools.investment_lots.apply_investment_lot_adjustments folds
the computed results into those inputs. Dates are day numbers on one scale
(for example days since 2000-01-01)."""

from policyengine_us.model_api import *

LOT_SLOTS = 5
WASH_SALE_PURCHASES = 3

_REF = {
    "dividend_lot": (
        "https://www.law.cornell.edu/uscode/text/26/1#h_11_B_iii",
        "https://www.law.cornell.edu/cfr/text/26/1.199A-3",
    ),
    "wash_sale": (
        "https://www.law.cornell.edu/uscode/text/26/1091",
        "https://www.irs.gov/publications/p550",
    ),
    "fund_sale": ("https://www.law.cornell.edu/uscode/text/26/852#b_4",),
    "bond_lot": (
        "https://www.law.cornell.edu/uscode/text/26/1272",
        "https://www.law.cornell.edu/uscode/text/26/1276",
        "https://www.law.cornell.edu/uscode/text/26/171",
        "https://www.irs.gov/publications/p1212",
    ),
}

_FIELDS = {
    "dividend_lot": {
        "qualified_dividends_reported": (
            float,
            USD,
            "Dividends reported as qualified (1099-DIV box 1b) on the holding",
        ),
        "days_held_in_window": (
            int,
            None,
            "Days held, unhedged, in the 121-day (181-day for long-period preferred) window",
        ),
        "preferred_long_period": (
            bool,
            None,
            "Preferred stock dividend attributable to more than 366 days",
        ),
        "section_199a_dividends_reported": (
            float,
            USD,
            "Section 199A dividends reported (1099-DIV box 5) on the holding",
        ),
        "days_held_in_199a_window": (
            int,
            None,
            "Days held in the 91-day window for section 199A dividends",
        ),
    },
    "wash_sale": {
        "loss": (float, USD, "Loss realized on the sale (positive)"),
        "shares_sold": (float, None, "Shares or units sold at a loss"),
        "sale_day": (int, None, "Sale date as a day number"),
        "long_term": (bool, None, "Lot sold was held more than one year"),
    },
    "fund_sale": {
        "loss": (float, USD, "Loss realized on RIC shares (positive)"),
        "held_six_months_or_less": (bool, None, "Shares held six months or less"),
        "capital_gain_dividends": (
            float,
            USD,
            "Capital gain dividends (including designated undistributed gains) on the shares",
        ),
        "exempt_interest_dividends": (
            float,
            USD,
            "Exempt-interest dividends on the shares",
        ),
        "daily_dividend_fund": (
            bool,
            None,
            "Fund declares exempt-interest dividends daily and pays at least monthly (IRC 852(b)(4)(E))",
        ),
    },
    "bond_lot": {
        "adjusted_issue_price_start": (
            float,
            USD,
            "Adjusted issue price at the start of the year (OID bonds)",
        ),
        "yield_per_accrual_period": (
            float,
            "/1",
            "Yield to maturity per accrual period",
        ),
        "accrual_periods_held": (
            float,
            None,
            "Accrual periods held this year (fractions allowed)",
        ),
        "qualified_stated_interest": (
            float,
            USD,
            "Qualified stated interest received this year",
        ),
        "stated_redemption_price": (float, USD, "Stated redemption price at maturity"),
        "issue_price": (float, USD, "Issue price"),
        "complete_years_to_maturity_at_issue": (
            int,
            None,
            "Complete years to maturity at issue",
        ),
        "acquisition_premium_fraction": (
            float,
            "/1",
            "Acquisition premium fraction reducing OID (IRC 1272(a)(7))",
        ),
        "market_discount": (float, USD, "Market discount at purchase"),
        "complete_years_to_maturity_at_purchase": (
            int,
            None,
            "Complete years to maturity at purchase",
        ),
        "days_held": (int, None, "Days held from purchase to disposition or year-end"),
        "days_purchase_to_maturity": (int, None, "Days from purchase to maturity"),
        "disposition_gain": (
            float,
            USD,
            "Gain on disposition this year (0 if not disposed)",
        ),
        "disposition_long_term": (
            bool,
            None,
            "Bond held more than one year at disposition",
        ),
        "market_discount_included_currently": (
            bool,
            None,
            "Election to include market discount currently (IRC 1278(b))",
        ),
        "market_discount_included_before": (
            float,
            USD,
            "Market discount already included in income",
        ),
        "premium_amortization": (
            float,
            USD,
            "Bond premium amortized this year under an IRC 171 election",
        ),
    },
}

for _kind, _fields in _FIELDS.items():
    for _slot in range(1, LOT_SLOTS + 1):
        for _field, (_type, _unit, _label) in _fields.items():
            _name = f"{_kind}_{_slot}_{_field}"
            _attrs = dict(
                value_type=_type,
                entity=Person,
                definition_period=YEAR,
                label=f"{_kind.replace('_', ' ').capitalize()} {_slot}: {_label}",
                reference=_REF[_kind],
                __module__=__name__,
            )
            if _unit:
                _attrs["unit"] = _unit
            globals()[_name] = type(_name, (Variable,), _attrs)
    if _kind == "wash_sale":
        for _slot in range(1, LOT_SLOTS + 1):
            for _k in range(1, WASH_SALE_PURCHASES + 1):
                for _field, _type, _label in (
                    ("day", int, "acquisition date as a day number"),
                    (
                        "shares",
                        float,
                        "shares or units acquired (substantially identical)",
                    ),
                    ("in_ira", bool, "acquired in an IRA or Roth IRA"),
                ):
                    _name = f"wash_sale_{_slot}_purchase_{_k}_{_field}"
                    globals()[_name] = type(
                        _name,
                        (Variable,),
                        dict(
                            value_type=_type,
                            entity=Person,
                            definition_period=YEAR,
                            label=f"Wash sale {_slot}, purchase {_k}: {_label}",
                            reference=_REF["wash_sale"],
                            __module__=__name__,
                        ),
                    )

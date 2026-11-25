"""Results of the lot-level rules. Long-term results flow into
long_term_capital_gains automatically; short-term, dividend and interest
results are applied by apply_investment_lot_adjustments."""

from policyengine_us.model_api import *

LOT_SLOTS = 5
WASH_SALE_PURCHASES = 3


def _p(period, parameters):
    return parameters(period).gov.irs.investment_lots


def _wash_sale_parts(person, period, parameters):
    """Per slot: allowed loss, loss disallowed with basis added to a taxable
    replacement, and loss disallowed permanently (IRA replacement, Rev. Rul.
    2008-5). Replacement shares are matched in purchase order."""
    window = _p(period, parameters).wash_sale_window_days
    parts = []
    for slot in range(1, LOT_SLOTS + 1):

        def v(field):
            return person(f"wash_sale_{slot}_{field}", period)

        loss = max_(0, v("loss"))
        sold = max_(0, v("shares_sold"))
        sale_day = v("sale_day")
        remaining = sold
        deferred_shares = 0
        permanent_shares = 0
        for k in range(1, WASH_SALE_PURCHASES + 1):
            day = v(f"purchase_{k}_day")
            shares = max_(0, v(f"purchase_{k}_shares"))
            in_window = (shares > 0) & (abs(day - sale_day) <= window)
            matched = where(in_window, min_(shares, remaining), 0)
            remaining = remaining - matched
            in_ira = v(f"purchase_{k}_in_ira")
            permanent_shares = permanent_shares + where(in_ira, matched, 0)
            deferred_shares = deferred_shares + where(in_ira, 0, matched)
        per_share = np.divide(loss, sold, out=np.zeros_like(loss), where=sold > 0)
        deferred = per_share * deferred_shares
        permanent = per_share * permanent_shares
        parts.append((loss - deferred - permanent, deferred, permanent, v("long_term")))
    return parts


def _fund_sale_parts(person, period, parameters):
    """Per slot: (short-term loss, long-term loss, disallowed loss)."""
    parts = []
    for slot in range(1, LOT_SLOTS + 1):

        def v(field):
            return person(f"fund_sale_{slot}_{field}", period)

        loss = max_(0, v("loss"))
        short = v("held_six_months_or_less")
        disallowed = where(
            short & ~v("daily_dividend_fund"),
            min_(loss, max_(0, v("exempt_interest_dividends"))),
            0,
        )
        after = loss - disallowed
        long_part = where(short, min_(after, max_(0, v("capital_gain_dividends"))), 0)
        parts.append((after - long_part, long_part, disallowed))
    return parts


def _bond_parts(person, period, parameters):
    """Per slot: (interest income adjustment, capital gain, gain is long-term).
    Interest = OID accrued + market discount recognized - premium amortized."""
    p = _p(period, parameters)
    parts = []
    for slot in range(1, LOT_SLOTS + 1):

        def v(field):
            return person(f"bond_lot_{slot}_{field}", period)

        # OID under the constant yield method (IRC 1272(a)(3)), zero when de minimis.
        srpm = max_(0, v("stated_redemption_price"))
        discount = max_(0, srpm - v("issue_price"))
        de_minimis = discount < p.de_minimis_discount_rate * srpm * v(
            "complete_years_to_maturity_at_issue"
        )
        aip = max_(0, v("adjusted_issue_price_start"))
        growth = (1 + v("yield_per_accrual_period")) ** v("accrual_periods_held") - 1
        oid = max_(0, aip * growth - max_(0, v("qualified_stated_interest")))
        oid = where(de_minimis, 0, oid) * (
            1 - np.clip(v("acquisition_premium_fraction"), 0, 1)
        )
        # Market discount accrued ratably (IRC 1276(b)(1)), zero when de minimis.
        md = max_(0, v("market_discount"))
        md_de_minimis = md < p.de_minimis_discount_rate * srpm * v(
            "complete_years_to_maturity_at_purchase"
        )
        to_maturity = v("days_purchase_to_maturity")
        accrued = md * np.clip(
            np.divide(
                v("days_held"),
                to_maturity,
                out=np.zeros(md.shape),
                where=to_maturity > 0,
            ),
            0,
            1,
        )
        accrued = where(md_de_minimis, 0, accrued)
        already = max_(0, v("market_discount_included_before"))
        current = v("market_discount_included_currently")
        gain = v("disposition_gain")
        # With the current inclusion election the accrual is interest each
        # year; otherwise gain up to the accrued discount is interest at sale.
        md_interest = where(
            current,
            max_(0, accrued - already),
            min_(max_(0, gain), max_(0, accrued - already)),
        )
        disposed_md = where(current, 0, md_interest)
        capital = gain - disposed_md
        interest = oid + md_interest - max_(0, v("premium_amortization"))
        parts.append((interest, capital, v("disposition_long_term")))
    return parts


def _var(name, label, doc, compute, reference):
    def formula(person, period, parameters):
        return compute(person, period, parameters)

    globals()[name] = type(
        name,
        (Variable,),
        dict(
            value_type=float,
            entity=Person,
            definition_period=YEAR,
            unit=USD,
            label=label,
            documentation=doc,
            reference=reference,
            formula=formula,
            __module__=__name__,
        ),
    )


def _sum(parts, index, when=None):
    total = 0
    for part in parts:
        value = part[index]
        if when is not None:
            value = where(when(part), value, 0)
        total = total + value
    return total


_var(
    "investment_lot_short_term_gain",
    "Short-term gain or loss from lot-level rules",
    "Allowed short-term wash-sale losses, RIC losses that stay short-term, and short-term bond gains (negative for losses).",
    lambda person, period, parameters: (
        -_sum(_wash_sale_parts(person, period, parameters), 0, lambda x: ~x[3])
        - _sum(_fund_sale_parts(person, period, parameters), 0)
        + _sum(_bond_parts(person, period, parameters), 1, lambda x: ~x[2])
    ),
    (
        "https://www.law.cornell.edu/uscode/text/26/1091",
        "https://www.law.cornell.edu/uscode/text/26/852#b_4",
    ),
)
_var(
    "investment_lot_long_term_gain",
    "Long-term gain or loss from lot-level rules",
    "Allowed long-term wash-sale losses, RIC losses recharacterized as long-term, and long-term bond gains (negative for losses).",
    lambda person, period, parameters: (
        -_sum(_wash_sale_parts(person, period, parameters), 0, lambda x: x[3])
        - _sum(_fund_sale_parts(person, period, parameters), 1)
        + _sum(_bond_parts(person, period, parameters), 1, lambda x: x[2])
    ),
    (
        "https://www.law.cornell.edu/uscode/text/26/1091",
        "https://www.law.cornell.edu/uscode/text/26/852#b_4",
    ),
)
_var(
    "wash_sale_disallowed_loss_deferred",
    "Wash sale losses added to replacement basis",
    "Disallowed losses the simulator must add to the basis of the replacement lots (IRC 1091(d)).",
    lambda person, period, parameters: _sum(
        _wash_sale_parts(person, period, parameters), 1
    ),
    ("https://www.law.cornell.edu/uscode/text/26/1091#d",),
)
_var(
    "wash_sale_disallowed_loss_permanent",
    "Wash sale losses disallowed permanently",
    "Losses disallowed because the replacement was bought in an IRA; no basis adjustment (Rev. Rul. 2008-5).",
    lambda person, period, parameters: _sum(
        _wash_sale_parts(person, period, parameters), 2
    ),
    ("https://www.irs.gov/pub/irs-drop/rr-08-05.pdf",),
)
_var(
    "ric_loss_disallowed_exempt_interest",
    "RIC share losses disallowed for exempt-interest dividends",
    "Losses on RIC shares held six months or less, disallowed to the extent of exempt-interest dividends (IRC 852(b)(4)(B)).",
    lambda person, period, parameters: _sum(
        _fund_sale_parts(person, period, parameters), 2
    ),
    ("https://www.law.cornell.edu/uscode/text/26/852#b_4",),
)
_var(
    "investment_lot_interest_adjustment",
    "Interest income adjustment from bond lots",
    "OID accrued plus market discount treated as interest, less amortizable bond premium.",
    lambda person, period, parameters: _sum(_bond_parts(person, period, parameters), 0),
    (
        "https://www.law.cornell.edu/uscode/text/26/1272",
        "https://www.law.cornell.edu/uscode/text/26/1276",
        "https://www.law.cornell.edu/uscode/text/26/171",
    ),
)


def _disqualified_dividends(person, period, parameters):
    p = _p(period, parameters)
    total = 0
    for slot in range(1, LOT_SLOTS + 1):
        days = person(f"dividend_lot_{slot}_days_held_in_window", period)
        minimum = where(
            person(f"dividend_lot_{slot}_preferred_long_period", period),
            p.qualified_dividend_preferred_min_days,
            p.qualified_dividend_min_days,
        )
        amount = max_(
            0, person(f"dividend_lot_{slot}_qualified_dividends_reported", period)
        )
        total = total + where(days > minimum, 0, amount)
    return total


def _disqualified_199a(person, period, parameters):
    p = _p(period, parameters)
    total = 0
    for slot in range(1, LOT_SLOTS + 1):
        days = person(f"dividend_lot_{slot}_days_held_in_199a_window", period)
        amount = max_(
            0, person(f"dividend_lot_{slot}_section_199a_dividends_reported", period)
        )
        total = total + where(days > p.section_199a_dividend_min_days, 0, amount)
    return total


_var(
    "dividends_failing_qualified_holding_period",
    "Reported qualified dividends failing the holding period",
    "Dividends reported as qualified on holdings not held more than 60 days (90 for long-period preferred) in the window; they are ordinary dividends.",
    _disqualified_dividends,
    ("https://www.law.cornell.edu/uscode/text/26/1#h_11_B_iii",),
)
_var(
    "section_199a_dividends_failing_holding_period",
    "Section 199A dividends failing the 45-day holding period",
    "Section 199A dividends on shares not held more than 45 days in the 91-day window; not qualified REIT dividends.",
    _disqualified_199a,
    ("https://www.law.cornell.edu/cfr/text/26/1.199A-3",),
)

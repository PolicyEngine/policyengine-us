"""Reconcile supplied annual earnings with the selected eligibility PIA.

Money is serialized as strings. Recurring rational mini-PIAs include an exact
fraction alongside their 50-digit decimal representation. Selection flags refer
only to supplied or certified annual rows; zero padding invents no ledger rows.
"""

from dataclasses import asdict
from decimal import Decimal, localcontext
from fractions import Fraction
import json


OUTPUTS = {
    "history_ledger",
    "history_aime",
    "history_aime_plus",
    "history_mini_pia",
    "history_conventional_pia",
}


def _amount(value):
    if value is None:
        return None
    if isinstance(value, Fraction):
        with localcontext() as context:
            context.prec = 50
            return str(Decimal(value.numerator) / Decimal(value.denominator))
    return str(value)


def _json_value(value):
    if isinstance(value, (Decimal, Fraction)):
        return _amount(value)
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            result[key] = _json_value(item)
            if isinstance(item, Fraction):
                result[f"{key}_exact"] = str(item)
        return result
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    return value


def _selected(rows, amounts, count):
    """Break equal-amount ties by earnings year, then original row position."""
    return set(
        sorted(
            range(len(rows)),
            key=lambda index: (-Fraction(amounts[index]), rows[index].year, index),
        )[:count]
    )


def history_report(annual, output):
    """Return an annual history diagnostic, or an empty unselected result.

    ``annual.history_pia`` is the formula diagnostic for January entitlement in
    the requested year. Before eligibility it may be absent while the initial
    claim-year earnings calculation remains available for reconciliation.
    """
    if output not in OUTPUTS:
        raise ValueError(f"Unknown history report output {output}")
    history = getattr(annual, "history", None)
    if history is None:
        return "" if output == "history_ledger" else 0
    details = getattr(annual, "history_pia", None)
    if output == "history_aime":
        return history.aime
    if output == "history_aime_plus":
        return getattr(history, "aime_plus", 0)
    if output == "history_mini_pia":
        return details.mini_pia if details is not None else 0
    if output == "history_conventional_pia":
        return details.conventional_pia if details is not None else 0

    rows = tuple(history.ledger)
    ordinary_selected = _selected(rows, [row.indexed_ordinary for row in rows], 35)
    donut_selected = _selected(
        rows, [getattr(row, "indexed_donut", 0) for row in rows], 35
    )
    mini_amounts = tuple(details.annual_mini_pias) if details is not None else None
    if mini_amounts is not None and len(mini_amounts) != len(rows):
        raise ValueError("Annual mini-PIAs must match the annual earnings ledger")
    mini_selected = (
        _selected(rows, mini_amounts, 40) if mini_amounts is not None else set()
    )

    serialized_rows = []
    for index, row in enumerate(rows):
        values = asdict(row)
        serialized = _json_value(values)
        # Monetary fields accept integer fixtures as well as Decimal values;
        # the annual year remains an integer in the public JSON schema.
        for name, value in values.items():
            if (
                name != "year"
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
            ):
                serialized[name] = _amount(value)
        mini = mini_amounts[index] if mini_amounts is not None else None
        serialized.update(
            mini_pia=_amount(mini),
            mini_pia_exact=str(mini) if mini is not None else None,
            ordinary_top35=index in ordinary_selected,
            donut_top35=index in donut_selected,
            mini_top40=index in mini_selected,
        )
        serialized_rows.append(serialized)

    def pia_amount(name):
        return getattr(details, name) if details is not None else None

    mini_share = getattr(history, "mini_share", Fraction(0))
    donut_credit = getattr(history, "donut_credit_pia", Fraction(0))
    mini_pia = pia_amount("mini_pia")
    blended_pia = pia_amount("blended_pia")
    return json.dumps(
        {
            "schema_version": 1,
            "eligibility_year": history.eligibility_year,
            "claim_year": history.claim_year,
            "aime": history.aime,
            "aime_plus": getattr(history, "aime_plus", 0),
            "mini_share": _amount(mini_share),
            "mini_share_exact": str(mini_share),
            "donut_credit_pia": _amount(donut_credit),
            "donut_credit_pia_exact": str(donut_credit),
            "conventional_pia": _amount(pia_amount("conventional_pia")),
            "mini_pia": _amount(mini_pia),
            "mini_pia_exact": str(mini_pia) if mini_pia is not None else None,
            "blended_pia": _amount(blended_pia),
            "blended_pia_exact": str(blended_pia) if blended_pia is not None else None,
            "eligibility_pia": _amount(pia_amount("eligibility_pia")),
            "rows": serialized_rows,
        },
        separators=(",", ":"),
        allow_nan=False,
    )

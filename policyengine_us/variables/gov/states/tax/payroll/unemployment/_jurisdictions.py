from policyengine_us.model_api import *


STATE_UNEMPLOYMENT_TAX_JURISDICTIONS = (
    ("states", "AL", "al"),
    ("states", "AK", "ak"),
    ("states", "AZ", "az"),
    ("states", "AR", "ar"),
    ("states", "CA", "ca"),
    ("states", "CO", "co"),
    ("states", "CT", "ct"),
    ("states", "DE", "de"),
    ("states", "DC", "dc"),
    ("states", "FL", "fl"),
    ("states", "GA", "ga"),
    ("states", "HI", "hi"),
    ("states", "ID", "id"),
    ("states", "IL", "il"),
    ("states", "IN", "in"),
    ("states", "IA", "ia"),
    ("states", "KS", "ks"),
    ("states", "KY", "ky"),
    ("states", "LA", "la"),
    ("states", "ME", "me"),
    ("states", "MD", "md"),
    ("states", "MA", "ma"),
    ("states", "MI", "mi"),
    ("states", "MN", "mn"),
    ("states", "MS", "ms"),
    ("states", "MO", "mo"),
    ("states", "MT", "mt"),
    ("states", "NE", "ne"),
    ("states", "NV", "nv"),
    ("states", "NH", "nh"),
    ("states", "NJ", "nj"),
    ("states", "NM", "nm"),
    ("states", "NY", "ny"),
    ("states", "NC", "nc"),
    ("states", "ND", "nd"),
    ("states", "OH", "oh"),
    ("states", "OK", "ok"),
    ("states", "OR", "or"),
    ("states", "PA", "pa"),
    ("states", "RI", "ri"),
    ("states", "SC", "sc"),
    ("states", "SD", "sd"),
    ("states", "TN", "tn"),
    ("states", "TX", "tx"),
    ("states", "UT", "ut"),
    ("states", "VT", "vt"),
    ("states", "VA", "va"),
    ("states", "WA", "wa"),
    ("states", "WV", "wv"),
    ("states", "WI", "wi"),
    ("states", "WY", "wy"),
    ("territories", "PR", "pr"),
    ("territories", "VI", "vi"),
)

STATE_EMPLOYER_UNEMPLOYMENT_TAX_VARIABLES = tuple(
    f"{slug}_employer_state_unemployment_tax"
    for _, _, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS
)


MONTHS_IN_QUARTER = 3


def _jurisdiction_parameter_values(parameters, instant, parameter_name: str) -> list:
    gov = parameters(instant).gov
    return [
        getattr(
            getattr(getattr(gov, group), slug).tax.payroll.unemployment,
            parameter_name,
        )
        for group, _, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS
    ]


def select_state_unemployment_tax_parameter(
    person: Population,
    period: Period,
    parameters,
    parameter_name: str,
    average_over_quarter_starts: bool = False,
) -> ArrayLike:
    """Select each person's jurisdiction value of an unemployment parameter.

    With average_over_quarter_starts, each jurisdiction's value is the mean
    of its values at the four calendar quarter starts. New Hampshire, New
    Jersey, Tennessee and Vermont assign rates for a July-June rate year, so
    their annual rate mixes two rate years.
    """
    state_code = person.household("state_code_str", period)
    if average_over_quarter_starts:
        quarter_starts = period.get_subperiods(MONTH)[::MONTHS_IN_QUARTER]
        by_quarter = [
            _jurisdiction_parameter_values(parameters, quarter_start, parameter_name)
            for quarter_start in quarter_starts
        ]
        values = [
            sum(quarter_values) / len(quarter_starts)
            for quarter_values in zip(*by_quarter)
        ]
    else:
        values = _jurisdiction_parameter_values(parameters, period, parameter_name)
    conditions = [
        state_code == code for _, code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS
    ]
    return select(conditions, values, default=0)

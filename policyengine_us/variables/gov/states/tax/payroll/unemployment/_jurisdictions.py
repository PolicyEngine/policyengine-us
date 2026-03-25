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


def select_state_unemployment_tax_parameter(
    person: Population,
    period: Period,
    parameters,
    parameter_name: str,
) -> ArrayLike:
    state_code = person.household("state_code_str", period)
    gov = parameters(period).gov
    conditions = []
    values = []

    for group, code, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS:
        jurisdiction = getattr(getattr(gov, group), slug)
        unemployment = jurisdiction.tax.payroll.unemployment
        conditions.append(state_code == code)
        values.append(getattr(unemployment, parameter_name))

    return select(conditions, values, default=0)

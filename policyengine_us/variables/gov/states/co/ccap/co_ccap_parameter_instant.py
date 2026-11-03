from policyengine_us.tools.parameters import FIRST_MODELED_YEAR


def co_ccap_parameter_instant(period) -> str:
    """The instant at which Colorado CCAP reads its parameters for a month.

    CCAP sets its limits each October, so a month from January to September
    uses the limits that took effect the previous October 1. Before October
    of the first modeled year, that October falls before the date to which
    CountryTaxBenefitSystem backdates parameters, where the CCAP parameters
    have no value. Those months read the parameters at the start of the
    first modeled year instead. There the CCAP parameters hold their
    backdated values, and `gov.hhs.smi` still holds HHS's values for the
    fiscal year that began the previous October. The helper backdates
    nothing further.
    """
    year = period.start.year
    if period.start.month >= 10:
        return f"{year}-10-01"
    if year - 1 < FIRST_MODELED_YEAR:
        return f"{FIRST_MODELED_YEAR}-01-01"
    return f"{year - 1}-10-01"

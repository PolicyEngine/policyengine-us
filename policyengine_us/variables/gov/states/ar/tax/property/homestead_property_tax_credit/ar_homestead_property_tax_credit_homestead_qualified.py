from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_homestead_qualified(Variable):
    """County-verified qualification for this parcel and assessment year.

    Sections 26-26-1122(a)(2), (5) and 26-26-1118(b)(4)-(6) require a principal
    dwelling/contiguous eligible land and a qualifying recorded title,
    mortgagee, purchase-contract, life-estate or redemption interest. Check
    qualifying settlor/beneficiary trusts or single-person/married-couple LLCs
    and qualification before January 1 after assessment. Preserve an
    established credit through that year's transfer/use changes. Nursing-home
    circumstances require actual accepted county qualification. Current
    tenure, age or generic disability cannot supply these facts.
    """

    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = (
        "The parcel satisfies Arkansas homestead qualification for the assessment year"
    )
    reference = (
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2023R%2FPublic%2FACT541.pdf#page=2",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2017R%2FPublic%2FACT49.pdf#page=2",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2005%2FPublic%2FACT1268.pdf#page=2",
        "https://sebastiancountyar.gov/Portals/0/Content/Assessor/Downloads/Homestead%20Tax%20Credit%20Form%202026.html",
    )

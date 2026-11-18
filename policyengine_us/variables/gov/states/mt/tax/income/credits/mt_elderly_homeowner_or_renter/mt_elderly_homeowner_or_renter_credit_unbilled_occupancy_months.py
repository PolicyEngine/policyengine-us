from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_unbilled_occupancy_months(Variable):
    value_type = int
    entity = Person
    label = "Months occupying a Montana dwelling as an owner, renter, or lessee without rent paid or property tax billed, for the Montana elderly homeowner/renter credit"
    documentation = (
        "Months of the year, from 0 to 12, this person occupied one or more "
        "Montana dwellings as an owner, renter, or lessee that neither rent "
        "paid nor property tax billed to their tax unit shows, such as a "
        "lessee who pays no rent. Defaults to 0. Supplying it for one person "
        "leaves everyone else's occupancy to follow their own rent and "
        "property tax."
    )
    unit = "month"
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # MCA 15-30-2338(1)(c): occupied one or more dwellings in Montana
        # "as an owner, renter, or lessee for at least 6 months"
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0380/0150-0300-0230-0380.html",
        "https://mca.legmt.gov/bills/2009/mca/15/30/15-30-2338.htm",
    )

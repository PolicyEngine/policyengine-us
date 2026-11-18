from policyengine_us.model_api import *


class va_ag_maximum_care_rate(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant maximum monthly care rate"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://www.dss.virginia.gov/media/vdss/licensing/documents/assisted-living-facilities/additional-resources/ARC2026_ag_rate_letter.pdf",
        "https://budget.lis.virginia.gov/item/2026/2/HB30/Chapter/1/332/",
        # PDF pages 520, 542
        "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=520",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dars.ag
        fbr = parameters(period).gov.ssa.ssi.amount.individual
        standard = fbr + p.rate.fbr_offset
        # The published $2,450 Planning District Eight rate is 2,130 x 1.15
        # rounded to the nearest dollar; the rounding is inferred.
        northern_rate = np.floor(
            standard * (1 + p.rate.northern_virginia_differential) + 0.5
        )
        northern = np.isin(
            person.household("county_str", period.this_year),
            p.northern_virginia_localities,
        )
        return where(northern, northern_rate, standard)

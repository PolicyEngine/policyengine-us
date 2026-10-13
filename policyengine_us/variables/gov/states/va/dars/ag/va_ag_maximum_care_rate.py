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
        northern = np.isin(
            person.household("county_str", period.this_year),
            p.northern_virginia_localities,
        )
        return where(northern, p.rate.northern_virginia, p.rate.standard)

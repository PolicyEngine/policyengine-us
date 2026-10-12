from policyengine_us.model_api import *


class va_ag_care_rate(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant approved monthly care rate"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dss.virginia.gov/media/vdss/licensing/documents/assisted-living-facilities/additional-resources/ARC2026_ag_rate_letter.pdf"
    documentation = "Use the approved provider rate when it is below the published locality maximum."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dars.ag
        northern = np.isin(
            person.household("county_str", period.this_year),
            p.northern_virginia_localities,
        )
        return where(northern, p.rate.northern_virginia, p.rate.standard)

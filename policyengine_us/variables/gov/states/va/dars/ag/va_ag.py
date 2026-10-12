from policyengine_us.model_api import *


class va_ag(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant"
    definition_period = MONTH
    unit = USD
    defined_for = "va_ag_eligible"
    reference = (
        "https://law.lis.virginia.gov/admincode/title22/agency30/chapter80/section50/",
        "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dars.ag
        rate = max_(person("va_ag_care_rate", period), 0)
        northern = np.isin(
            person.household("county_str", period.this_year),
            p.northern_virginia_localities,
        )
        maximum = where(northern, p.rate.northern_virginia, p.rate.standard)
        rate = min_(rate, maximum)
        days = clip(person("va_ag_days_eligible", period), 0, period.days)
        rate = where(days == period.days, rate, rate / p.proration_days * days)
        need = rate + p.personal_needs_allowance
        deficiency = max_(need - person("va_ag_countable_income", period), 0)
        return (days > 0) * np.floor(deficiency + 0.5)

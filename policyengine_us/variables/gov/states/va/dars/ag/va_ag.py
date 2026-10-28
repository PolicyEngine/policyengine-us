from policyengine_us.model_api import *


class va_ag(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant"
    definition_period = MONTH
    unit = USD
    defined_for = "va_ag_eligible"
    reference = (
        "https://law.lis.virginia.gov/vacode/title51.5/chapter14/section51.5-160/",
        "https://law.lis.virginia.gov/admincode/title22/agency30/chapter80/section50/",
        # PDF pages 519-520, 522, 524
        "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=519",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dars.ag
        rate = person("va_ag_care_rate", period)
        days = person("va_ag_partial_month_days", period)
        partial_month = (days > 0) & (days < period.days)
        rate = where(partial_month, rate / p.proration_days * days, rate)
        need = rate + p.personal_needs_allowance
        deficiency = max_(need - person("va_ag_countable_income", period), 0)
        return np.floor(deficiency + 0.5)

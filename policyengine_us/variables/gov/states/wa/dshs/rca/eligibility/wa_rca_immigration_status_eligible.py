from policyengine_us.model_api import *


class wa_rca_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Washington Refugee Cash Assistance immigration status eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1522",
        # WAC 388-466-0120(1)-(2): RCA-eligible immigration statuses.
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-466-0120",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0030",
    )

    def formula(person, period, parameters):
        status = person("immigration_status", period.this_year)
        status_str = status.decode_to_str()
        p = parameters(period).gov.states.wa.dshs.rca
        return np.isin(status_str, p.eligible_immigration_statuses)

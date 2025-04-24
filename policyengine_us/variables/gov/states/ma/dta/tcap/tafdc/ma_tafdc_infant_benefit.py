from policyengine_us.model_api import *


class ma_tafdc_infant_benefit(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) infant benefit"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-705-600"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        eligible_infant = person("ma_tafdc_eligible_infant", period)
        p = parameters(period).gov.states.ma.dta.tcap.tafdc
        return eligible_infant * p.infant_amount

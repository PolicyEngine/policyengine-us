from policyengine_us.model_api import *


class ma_tafdc_lump_sum_income_exclusion(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts TAFDC lump sum income exclusion"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # Section (B): The first $600 of lump sum income
        # in the month of receipt is noncountable.
        lump_sum = person("ma_tafdc_lump_sum_income", period)
        p = parameters(period).gov.states.ma.dta.tcap.tafdc
        cap = p.income.noncountable.lump_sum.cap
        return min_(lump_sum, cap)

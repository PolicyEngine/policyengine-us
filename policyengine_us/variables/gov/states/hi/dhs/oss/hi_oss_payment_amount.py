from policyengine_us.model_api import *


class hi_oss_payment_amount(Variable):
    value_type = float
    entity = Person
    label = "Hawaii OSS monthly payment amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://secure.ssa.gov/POMS.NSF/lnx/0501415057"

    def formula(person, period, parameters):
        la = person("hi_oss_living_arrangement", period)
        couple_rate = person("hi_oss_couple_rate_applies", period)
        p = parameters(period).gov.states.hi.dhs.oss.payment
        return where(
            couple_rate,
            p.couple.amount[la] / 2,
            p.individual.amount[la],
        )

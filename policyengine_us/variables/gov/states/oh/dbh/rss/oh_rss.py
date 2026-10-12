from policyengine_us.model_api import *


class oh_rss(Variable):
    value_type = float
    entity = Person
    label = "Ohio Residential State Supplement"
    definition_period = MONTH
    unit = USD
    defined_for = "oh_rss_eligible"
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dbh.rss
        limits = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        eligible = person("oh_rss_eligible", period)
        couple = person.marital_unit.sum(eligible) == 2
        resources = person("ssi_countable_resources", period.this_year)
        resources = where(couple, person.marital_unit.sum(resources), resources)
        limit = where(couple, limits.couple, limits.individual)
        payment = max_(
            p.allowable_fee
            + p.personal_needs_allowance
            - person("oh_rss_countable_income", period),
            0,
        )
        days = clip(person("oh_rss_days_of_placement", period), 0, period.days)
        # First-month placement is prorated after rounding the daily payment
        # upward to the cent. Full months retain the unprorated benefit.
        daily_payment = np.ceil(payment.astype(np.float64) / period.days * 100) / 100
        partial = np.ceil(daily_payment * days * 100 - 1e-8) / 100
        return (resources <= limit) * where(days == period.days, payment, partial)

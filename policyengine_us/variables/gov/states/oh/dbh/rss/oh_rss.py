from policyengine_us.model_api import *


class oh_rss(Variable):
    value_type = float
    entity = Person
    label = "Ohio Residential State Supplement"
    definition_period = MONTH
    unit = USD
    defined_for = "oh_rss_eligible"
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-3-05.1",
    )
    # NOTE: Not in the HUD income list. RSS is paid to the person (5122-36-04(A)(7)),
    # but recipients live in licensed residential care (5122-36-02(A)(5)), and HUD
    # income would make the Medicaid condition circular via rent tax deductions.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dbh.rss
        limits = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        eligible = person("oh_rss_eligible", period)
        couple = person.marital_unit.sum(eligible) == 2
        # When only one spouse qualifies, 5160:1-5-01(E)(3) applies the
        # individual standard: own resources against $2,000. Source conflict:
        # 5160:1-3-05.1(B)(9)(b) and 5160:1-3-05.20(E) would combine the
        # couple's resources against $3,000.
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
        daily_payment = (
            np.ceil(payment.astype(np.float64) / period.days * 100 - 1e-8) / 100
        )
        partial = np.ceil(daily_payment * days * 100 - 1e-8) / 100
        return (resources <= limit) * where(days == period.days, payment, partial)

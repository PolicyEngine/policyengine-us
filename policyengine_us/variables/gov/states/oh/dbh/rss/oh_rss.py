from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


class oh_rss(Variable):
    value_type = float
    entity = Person
    label = "Ohio Residential State Supplement"
    definition_period = MONTH
    unit = USD
    defined_for = "oh_rss_eligible"
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5119.41",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-3-05.1",
    )
    # NOTE: Not in the HUD income list. RSS is paid to the person (5122-36-04(A)(7)),
    # but recipients live in licensed residential care (5122-36-02(A)(5)), and HUD
    # income would make the Medicaid condition circular via rent tax deductions.
    # NOTE: ORC 5119.41(A) describes RSS as supplementing "the amounts received by
    # aged, blind, or disabled adults as supplemental security income payments ...
    # or as social security benefits or social security disability insurance
    # benefits". Under 5119.41(B), eligibility is set by the rules, and neither
    # 5160:1-5-01(C) nor 5122-36-02(A) requires receipt of SSI or Social Security.
    # Ohio's Medicaid conditions of eligibility (5160:1-2-10(B)) also do not
    # require applying for SSI. The model follows the rules, so it pays eligible
    # people who receive neither benefit and does not require SSI take-up.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dbh.rss
        # Ohio prints the same $2,000 individual and $3,000 couple resource
        # limits (5160:1-3-05.1(B)(9)), so the SSI parameters are used and an
        # SSI reform carries over to RSS.
        limits = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        eligible = person("oh_rss_eligible", period)
        couple = _ssi_couple_total(person, period.this_year, eligible.astype(int)) == 2
        # NOTE: When only one spouse qualifies, 5160:1-5-01(E)(3) applies the
        # individual standard, so the model tests own resources against
        # $2,000. Ohio's Medicaid resource rules, 5160:1-3-05.1(B)(9)(b) and
        # 5160:1-3-05.20(E)(1)-(2), would instead combine the couple's resources
        # against $3,000. The model follows the RSS rule. The reading decides the
        # result only when medicaid_enrolled is entered: computed Medicaid and
        # the SSI resource test both combine the couple's resources, so a
        # couple above $3,000 fails the Medicaid condition.
        resources = person("ssi_countable_resources", period.this_year)
        resources = where(
            couple, _ssi_couple_total(person, period.this_year, resources), resources
        )
        limit = where(couple, limits.couple, limits.individual)
        payment = max_(
            p.allowable_fee
            + p.personal_needs_allowance
            - person("oh_rss_countable_income", period),
            0,
        )
        days = person("oh_rss_partial_month_days", period)
        prorate = (days > 0) & (days < period.days)
        # A first month that starts after the first day is prorated: the daily
        # amount and the prorated total are each rounded up to the next whole
        # cent (5160:1-5-01(G)(5)-(6)). Countable income is stored in float32,
        # so the daily amount allows a thousandth of a cent before rounding up.
        daily_payment = (
            np.ceil(payment.astype(np.float64) / period.days * 100 - 1e-3) / 100
        )
        partial = np.ceil(daily_payment * days * 100 - 1e-8) / 100
        return (resources <= limit) * where(prorate, partial, payment)

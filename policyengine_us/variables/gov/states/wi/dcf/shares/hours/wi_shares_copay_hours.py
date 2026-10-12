from policyengine_us.model_api import *


class wi_shares_copay_hours(Variable):
    value_type = float
    entity = Person
    unit = "hour"
    label = "Wisconsin Shares monthly copayment hours"
    definition_period = MONTH
    defined_for = "wi_shares_eligible_child"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=150",
        "https://dcf.wisconsin.gov/files/wishares/pdf/wishares-copay-schedule.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.copay.hours
        # Each child's copayment hours are their monthly subsidized hours
        # capped at 152: part-time authorizations contribute 131 hours and
        # full-time authorizations contribute 152 (the 153rd subsidized hour
        # is not charged a copayment; Section 18.2).
        subsidized_hours = person("wi_shares_monthly_subsidized_hours", period)
        capped_hours = min_(subsidized_hours, p.per_child_cap)
        # Children with a $0 copayment type are excluded from the assistance
        # group's copayment hours pool (Section 18.3). Foster children are
        # the modeled $0 type; the W-2 participant type zeroes the whole
        # assistance group's copayment in wi_shares_copay, and the
        # court-ordered kinship and Learnfare types are not tracked at the
        # moment.
        is_regular_copay_type = ~person("is_in_foster_care", period)
        return capped_hours * is_regular_copay_type

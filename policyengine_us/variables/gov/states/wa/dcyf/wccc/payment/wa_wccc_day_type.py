from policyengine_us.model_api import *


class WAWCCCDayType(Enum):
    HALF_DAY = "Half Day"
    PARTIAL_DAY = "Partial Day"
    FULL_DAY = "Full Day"


class wa_wccc_day_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = WAWCCCDayType
    default_value = WAWCCCDayType.FULL_DAY
    definition_period = MONTH
    defined_for = StateCode.WA
    label = "Washington WCCC daily billing unit type"
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0190"
    # Per WAC 110-15-0190(7): FULL_DAY = at least 5 hours of care, HALF_DAY
    # = under 5 hours, PARTIAL_DAY = under 5 hours with care before AND
    # after school. We don't track per-day care hours or the
    # before-and-after-school flag at the moment; defaults to FULL_DAY but
    # accepts user override. Centers do not have a PARTIAL_DAY rate per
    # WAC 110-15-0200; PARTIAL_DAY for centers is treated as HALF_DAY in
    # the reimbursement calculation.

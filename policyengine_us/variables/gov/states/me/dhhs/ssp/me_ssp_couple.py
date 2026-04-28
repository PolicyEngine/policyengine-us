from policyengine_us.model_api import *


class me_ssp_couple(Variable):
    value_type = float
    entity = Person
    label = "Maine SSP per-person share of the couple monthly amount"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ssp_eligible"
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ssp.amount
        category = person("me_ssp_payment_category", period)
        # Maine's couple amounts for D/E/F/G are not 2x the individual
        # amount -- they are the facility's couple rate covering both
        # spouses. Per-person attribution splits the couple total 50/50.
        per_person_share = p.couple[category] / 2
        # State Supplement-only path: when countable income exceeds the
        # federal SSI break-even, uncapped_ssi goes negative. ssa/ssi
        # already splits couple countable income 50/50 across eligible
        # spouses, so each person's share of the excess offsets their
        # share of the couple supplement. Maine also disregards an
        # additional $80 (couple) for codes A and C on top of the
        # federal exclusions per SSA 2011 Table 1; we don't model that
        # state disregard at the moment, so SS-only couple supplements
        # in those categories are slightly under-paid.
        monthly_excess = max_(0, -person("uncapped_ssi", period))
        return max_(0, per_person_share - monthly_excess)

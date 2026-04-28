from policyengine_us.model_api import *


class me_ssp_individual(Variable):
    value_type = float
    entity = Person
    label = "Maine SSP individual monthly amount"
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
        table_amount = p.individual[category]
        # State Supplement-only path: when countable income exceeds the
        # federal SSI break-even, uncapped_ssi goes negative. The
        # excess is netted against the state supplement so the combined
        # SSI + SSP standard is preserved. uncapped_ssi is YEAR-defined,
        # so accessing it with `period` auto-converts to monthly.
        # Maine also disregards an additional $55 (individual) for codes
        # A and C on top of the federal exclusions per SSA 2011 Table 1;
        # we don't model that state disregard at the moment, so SS-only
        # supplements in those categories are slightly under-paid.
        monthly_excess = max_(0, -person("uncapped_ssi", period))
        return max_(0, table_amount - monthly_excess)

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
        p = parameters(period).gov.states.me.dhhs.ssp
        category = person("me_ssp_payment_category", period)
        categories = category.possible_values
        table_amount = p.amount.individual[category]
        # A/C/H/I pay a fixed amount; D/E/F/G net excess against the rate.
        is_fixed = (
            (category == categories.LIVING_ALONE_OR_WITH_OTHERS)
            | (category == categories.HOUSEHOLD_OF_ANOTHER)
            | (category == categories.MEDICAID_FACILITY)
            | (category == categories.RESIDENTIAL_CARE_FACILITY)
        )
        # SS-only path: uncapped_ssi < 0 means income exceeds the federal
        # SSI standard. Apply Maine's state disregard ($55 for A/C, $0
        # elsewhere) on top of federal exclusions per SSA 2011 Table 1.
        federal_excess = max_(0, -person("uncapped_ssi", period))
        state_disregard = p.disregard.individual[category]
        adjusted_excess = max_(0, federal_excess - state_disregard)
        within_limit = adjusted_excess <= table_amount
        return where(
            is_fixed,
            table_amount * within_limit,
            max_(0, table_amount - adjusted_excess),
        )

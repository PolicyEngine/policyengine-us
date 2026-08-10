from policyengine_us.model_api import *


class ca_cc_general_assistance_personal_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Meets property limit for Contra Costa County General Assistance"
    defined_for = "in_cc"
    reference = (
        "https://ehsd.org/aging-and-adult-services/general-assistance/",
        # Other resource exclusions (home, jewelry, property-tax escrow,
        # cash < $50) are listed in the GA-80 brochure but are not modeled
        # separately; we treat `personal_property` as the net countable
        # non-cash asset figure.
        "https://ehsd.org/wp-content/uploads/2024/08/GA-Brochure_ENGLISH_July2024_FA_Digital.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.cc.general_assistance.personal_property
        # The brochure exempts only money held for property taxes and amounts
        # under $50, so cash counts toward the limit; spm_unit_cash_assets
        # aggregates it, and personal_property covers non-cash items.
        countable_property = add(
            spm_unit,
            period.this_year,
            [
                "spm_unit_cash_assets",
                "personal_property",
                "ca_cc_general_assistance_countable_vehicle_value",
            ],
        )
        return countable_property <= p.limit

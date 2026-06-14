from policyengine_us.model_api import *


class ca_cc_general_assistance_personal_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Meets property limit for Contra Costa County General Assistance"
    defined_for = "in_cc"
    reference = (
        "https://ehsd.org/aging-and-adult-services/general-assistance/",
        # Resource exclusions (home, one vehicle <= $4,500, jewelry, property-tax
        # escrow, cash < $50) are listed in the GA-80 brochure but are not modeled
        # separately; we treat `personal_property` as the net countable-asset figure.
        "https://ehsd.org/wp-content/uploads/2024/08/GA-Brochure_ENGLISH_July2024_FA_Digital.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.cc.general_assistance.personal_property
        personal_property = add(spm_unit, period.this_year, ["personal_property"])
        return personal_property <= p.limit

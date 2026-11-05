from policyengine_us.model_api import *


class wi_wheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Wisconsin WHEAP household size"
    defined_for = StateCode.WI
    # Sections 3.2.2.4, 3.2.6.2, 3.2.6.4 and 4.4.26.2.
    # PDF pages 35, 44-45, 82
    reference = "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=35"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Citizens, qualified non-citizens and non-citizens receiving any
        # Social Security are counted. Ineligible non-citizens are excluded
        # from size, but their income counts. FoodShare receipt has no
        # person-level input, so non-citizens in FoodShare are counted only
        # through their immigration status. Court-placed foster children are
        # counted because no input identifies a court placement. SPM
        # membership approximates the economic unit on the application date.
        eligible_member = person("is_citizen_or_legal_immigrant", period) | (
            person("social_security", period) > 0
        )
        return spm_unit.sum(eligible_member)

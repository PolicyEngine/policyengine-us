from policyengine_us.model_api import *


class ca_marin_general_relief_personal_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for the Marin County General Relief based on the personal property requirements"
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=11"

    def formula(spm_unit, period, parameters):
        # The Standards phrase the limit as "not more than" the threshold, so a
        # unit at exactly the limit is eligible. Personal property is a
        # year-defined stock; read it with period.this_year so this month-defined
        # formula does not divide the balance across months.
        countable_property = add(
            spm_unit,
            period.this_year,
            [
                "personal_property",
                "ca_marin_general_relief_countable_vehicle_value",
            ],
        )
        limit = spm_unit("ca_marin_general_relief_personal_property_limit", period)
        return countable_property <= limit

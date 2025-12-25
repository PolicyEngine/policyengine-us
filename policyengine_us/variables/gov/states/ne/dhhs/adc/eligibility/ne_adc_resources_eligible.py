from policyengine_us.model_api import *


class ne_adc_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nebraska ADC resources eligible"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1726",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1713",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.adc
        # spm_unit_assets is a YEAR variable
        countable_resources = spm_unit("spm_unit_assets", period)
        size = spm_unit("spm_unit_size", period)
        # Resource limits: $4,000 for 1 person, $6,000 for 2+ persons
        limit = p.resources.limit.calc(size)
        return countable_resources <= limit

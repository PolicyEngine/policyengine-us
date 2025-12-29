from policyengine_us.model_api import *


class mi_fip_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan FIP based on resources"
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/400.pdf",
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.fip

        # Get total household assets
        # Using spm_unit_assets as a proxy for countable assets
        # Full implementation would apply specific asset exclusions per BEM 400
        # Note: spm_unit_assets is a YEAR variable, so we access it with this_year
        assets = spm_unit("spm_unit_assets", period.this_year)

        return assets <= p.resources.limit

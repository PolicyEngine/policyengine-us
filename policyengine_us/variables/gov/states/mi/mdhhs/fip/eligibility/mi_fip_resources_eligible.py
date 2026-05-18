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

        # Count liquid financial assets explicitly. BEM 400 excludes several
        # non-liquid resources that are not yet modeled separately here.
        assets = spm_unit("spm_unit_cash_assets", period.this_year)

        return assets <= p.resources.limit

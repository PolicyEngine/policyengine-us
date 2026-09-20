from policyengine_us.model_api import *


class tx_ccs_meets_standard_family_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.TX
    label = "Texas CCS standard family income, asset, and work requirements"
    reference = "https://www.twc.texas.gov/sites/default/files/ogc/docs/rules-chapter-809-child-care-services-twc.pdf#page=23"

    def formula(spm_unit, period, parameters):
        income = spm_unit("tx_ccs_income_eligible", period)
        assets = spm_unit("tx_ccs_asset_eligible", period)
        work = spm_unit("tx_ccs_work_requirement_eligible", period)
        return income & assets & work

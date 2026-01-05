from policyengine_us.model_api import *


class fl_tca_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA resource eligible"
    definition_period = MONTH
    reference = (
        "https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance",
        "https://flrules.org/gateway/RuleNo.asp?id=65A-4.208",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per Florida DCF: Countable assets must be <= $2,000
        p = parameters(period).gov.states.fl.dcf.tanf.resources
        assets = spm_unit("spm_unit_assets", period.this_year)
        return assets <= p.asset_limit

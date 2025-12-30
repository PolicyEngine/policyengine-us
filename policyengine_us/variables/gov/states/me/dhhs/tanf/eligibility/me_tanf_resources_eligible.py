from policyengine_us.model_api import *


class me_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maine TANF resources eligible"
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP0892&item=3&session=131",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762 and P.L. 2023 Ch. 366:
        # Resource limit is $10,000 per family
        # One vehicle per licensed driver is exempt
        p = parameters(period).gov.states.me.dhhs.tanf
        countable_resources = spm_unit("spm_unit_assets", period.this_year)
        return countable_resources <= p.resource_limit

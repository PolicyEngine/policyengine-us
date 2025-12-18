from policyengine_us.model_api import *


class wi_works(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin Works"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/148",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/7.4.1_Community_Service_Jobs_(CSJ).htm",
    )
    defined_for = "wi_works_eligible"

    def formula(spm_unit, period, parameters):
        placement = spm_unit("wi_works_placement", period)
        p = parameters(period).gov.states.wi.dcf.works.placement
        return p.amount[placement]

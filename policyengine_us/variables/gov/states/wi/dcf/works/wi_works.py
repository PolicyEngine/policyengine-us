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
        # Wis. Stat. 49.148(1)(b)1m prorates only the Community Service Job.
        hours = spm_unit("wi_works_unsubsidized_hours", period)
        is_csj = placement == placement.possible_values.CSJ
        share = where(is_csj, p.csj_share.calc(hours), 1)
        # W-2 Manual 7.4.1.5 pays whole dollars, and half of $653 is $327.
        return np.floor(p.amount[placement] * share + 0.5)

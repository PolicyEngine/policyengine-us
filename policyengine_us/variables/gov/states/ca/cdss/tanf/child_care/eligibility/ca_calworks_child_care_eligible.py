from policyengine_us.model_api import *


class ca_calworks_child_care_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the California CalWORKs Child Care"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2"

    def formula(spm_unit, period, parameters):
        # This variable is inside the federal tanf dependency tree (state
        # TANF countable income deducts childcare_expenses, which nets out
        # child_care_subsidies, which includes ca_calworks_child_care), so
        # reading tanf here is circular. Read ca_tanf and apply the take-up
        # gate directly instead, which is equivalent for CA households.
        receives_calworks = (
            (spm_unit("ca_tanf", period) > 0)
            & spm_unit("takes_up_tanf_if_eligible", period)
        ) | (add(spm_unit, period, ["receives_tanf"]) > 0)
        age_eligible = spm_unit("ca_calworks_child_care_age_eligible", period)
        work_requirement = spm_unit(
            "ca_calworks_child_care_meets_work_requirement", period
        )
        person = spm_unit.members
        immigration_eligible = spm_unit.all(
            person(
                "ca_calworks_child_care_immigration_status_eligible_person",
                period,
            )
        )
        return (
            receives_calworks & age_eligible & work_requirement & immigration_eligible
        )

from policyengine_us.model_api import *


class ca_tanf_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Minimum Basic Standard of Adequate Care"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-212_Minimum_Basic_Standard_of_Adequate_Care%2F44-212_Minimum_Basic_Standard_of_Adequate_Care.htm%23Documentsbc-6&rhtocid=_3_1_7_20_5"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.cash.income.monthly_limit
        unit_size = spm_unit("spm_unit_size", period)
        au_size = min_(unit_size, p.max_au_size)
        additional_people = unit_size - au_size
        region1 = spm_unit.household("ca_tanf_region1", period)

        main_limit = where(
            region1, p.region1.main[au_size], p.region2.main[au_size]
        )
        increase_per_additional_person = where(
            region1, p.region1.additional, p.region2.additional
        )

        monthly_limit = (
            main_limit + increase_per_additional_person * additional_people
        )
        return monthly_limit * MONTHS_IN_YEAR

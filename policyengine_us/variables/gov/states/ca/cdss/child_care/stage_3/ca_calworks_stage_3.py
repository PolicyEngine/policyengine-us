from policyengine_us.model_api import *


class ca_calworks_stage_3(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Stage 3 child care subsidy"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_calworks_stage_3_eligible"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=10372.5.&lawCode=WIC"

    def formula(spm_unit, period, parameters):
        gross_payment = add(spm_unit, period, ["ca_calworks_stage_3_payment"])
        family_fee = spm_unit("ca_child_care_family_fee", period)
        return max_(gross_payment - family_fee, 0)

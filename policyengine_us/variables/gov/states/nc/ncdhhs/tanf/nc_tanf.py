from policyengine_us.model_api import *


class nc_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "nc_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_percentage = parameters(
            period
        ).gov.states.nc.ncdhhs.tanf.need_standard.payment_percentage
        reduced_need_standard = spm_unit(
            "nc_tanf_reduced_need_standard", period
        )

        return reduced_need_standard * payment_percentage

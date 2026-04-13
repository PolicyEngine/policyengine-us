from policyengine_us.model_api import *


class dc_tanf_work_sanction_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF work sanction rate"
    unit = "/1"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = (
        "https://dhs.dc.gov/sites/default/files/dc/sites/dhs/service_content/attachments/DHS%20Work%20Requirement%20Sanctions.pdf",
        "https://dhs.dc.gov/service/temporary-cash-assistance-needy-families-tanf",
    )

    def formula(spm_unit, period, parameters):
        enrolled = spm_unit("is_tanf_enrolled", period)
        meets_work_requirements = spm_unit(
            "dc_tanf_meets_work_requirements", period
        )
        rate = parameters(period).gov.states.dc.dhs.tanf.work_requirement.sanction.rate
        # CPS does not observe applicant-side orientation / IRP compliance. Restrict
        # the sanction proxy to enrolled recipients, where we at least observe TANF
        # participation and can use work-requirement status as a continuing-case proxy.
        sanctioned = enrolled & ~meets_work_requirements
        return where(sanctioned, rate, 0)

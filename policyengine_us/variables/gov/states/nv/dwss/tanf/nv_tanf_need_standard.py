from policyengine_us.model_api import *


class nv_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada TANF need standard"
    unit = USD
    definition_period = MONTH
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Home/Features/eligibility/Chapter%20C_140.pdf"
    defined_for = StateCode.NV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.tanf
        size = spm_unit("spm_unit_size", period.this_year)
        max_explicit_size = p.max_unit_size

        # For sizes <= 8, use explicit table values
        # For sizes > 8, use base at size 8 + increment per additional person
        base_amount = p.need_standard.amount[min_(size, max_explicit_size)]
        additional_persons = max_(size - max_explicit_size, 0)
        additional_amount = (
            additional_persons * p.need_standard.additional_person
        )

        return base_amount + additional_amount

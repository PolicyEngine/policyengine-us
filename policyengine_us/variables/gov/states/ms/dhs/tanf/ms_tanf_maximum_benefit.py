from policyengine_us.model_api import *


class ms_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = (
        "https://www.mdhs.ms.gov/wp-content/uploads/2018/02/MDHS_TANF-Eligibility-Flyer.pdf",
        "https://billstatus.ls.state.ms.us/documents/2021/html/SB/2700-2799/SB2759SG.htm",
        "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.tanf.payment_standard
        size = spm_unit("spm_unit_size", period.this_year)

        # Payment standard: first_person + second_person (if size >= 2) + additional_person * (size - 2)
        first_person = p.first_person
        second_person = where(size >= 2, p.second_person, 0)
        additional_persons = max_(size - 2, 0) * p.additional_person

        return first_person + second_person + additional_persons

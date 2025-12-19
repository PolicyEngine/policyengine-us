from policyengine_us.model_api import *


class ms_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi TANF maximum benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = (
        "https://law.justia.com/codes/mississippi/title-43/chapter-17/section-43-17-5/",
        "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.tanf.payment_standard
        size = spm_unit("spm_unit_size", period.this_year)

        # Per MS Code 43-17-5: $200 first person + $36 second + $24 each additional
        first_person = p.first_person
        second_person = where(size >= 2, p.second_person, 0)
        additional_persons = max_(size - 2, 0) * p.additional_person

        return first_person + second_person + additional_persons

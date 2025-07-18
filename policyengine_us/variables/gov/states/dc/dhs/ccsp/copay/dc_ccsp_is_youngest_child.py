from policyengine_us.model_api import *


class dc_ccsp_is_youngest_child(Variable):
    value_type = bool
    entity = Person
    label = "Person is the youngest child for DC Child Care Subsidy Program (CCSP) "
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf"
    definition_period = MONTH

    def formula(person, period, parameters):
        # the copay applies to the two youngest children
        eligible = person("dc_ccsp_eligible_child", period)
        age = person("monthly_age", period)
        spm_unit = person.spm_unit
        return person.get_rank(spm_unit, age, eligible) == 0

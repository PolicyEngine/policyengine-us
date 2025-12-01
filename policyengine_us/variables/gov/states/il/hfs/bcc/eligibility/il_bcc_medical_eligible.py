from policyengine_us.model_api import *


class il_bcc_medical_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Persons with Breast or Cervical Cancer medical condition eligible"
    definition_period = YEAR
    reference = "https://www.dhs.state.il.us/page.aspx?item=33528"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Must have diagnosis of breast cancer, cervical cancer,
        # or qualifying precancerous condition
        has_breast_cancer = person("has_breast_cancer_diagnosis", period)
        has_cervical_cancer = person("has_cervical_cancer_diagnosis", period)
        has_precancer = person("has_cervical_precancerous_condition", period)
        return has_breast_cancer | has_cervical_cancer | has_precancer

from policyengine_us.model_api import *


class ca_state_supplement_medical_care_facility_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement medical care facility amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.state_supplement.payment_standard
        # Medical care facility amount
        person = spm_unit.members
        eligible = person("ca_state_supplement_eligible_person", period)
        # The model pays dependent children the dependent amount instead.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        in_medical_care_facility = person("ca_in_medical_care_facility", period)
        medical_care_facility_count = spm_unit.sum(
            in_medical_care_facility * eligible * head_or_spouse
        )
        return medical_care_facility_count * p.allowance.medical_care_facility

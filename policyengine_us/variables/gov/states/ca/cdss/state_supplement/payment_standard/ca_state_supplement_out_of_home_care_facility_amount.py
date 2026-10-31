from policyengine_us.model_api import *


class ca_state_supplement_out_of_home_care_facility_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement out of home care facility amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.state_supplement.payment_standard
        person = spm_unit.members
        eligible = person("ca_state_supplement_eligible_person", period)
        # The model pays dependent children the dependent amount instead.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        in_out_of_home_care_facility = person("in_out_of_home_care_facility", period)
        out_of_home_care_facility_count = spm_unit.sum(
            in_out_of_home_care_facility * eligible * head_or_spouse
        )
        return out_of_home_care_facility_count * p.allowance.out_of_home_care

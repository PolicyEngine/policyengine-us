from policyengine_us.model_api import *


class ca_state_supplement_dependent_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement dependent amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.state_supplement.payment_standard
        person = spm_unit.members
        age = person("monthly_age", period)
        dependent = person("is_tax_unit_dependent", period)
        dependent_age_eligible = age < p.dependent.age_limit
        # The eligible person flag applies the SSI/SSP conditions, including
        # being blind or disabled; a child who fails SSI's noncitizen test
        # gets CAPI instead (WIC 18938, 18941).
        eligible = person("ca_state_supplement_eligible_person", period)
        dependent_count = spm_unit.sum(dependent & dependent_age_eligible & eligible)
        return dependent_count * p.dependent.amount

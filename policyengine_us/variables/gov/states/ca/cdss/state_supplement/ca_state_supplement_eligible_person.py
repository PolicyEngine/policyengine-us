from policyengine_us.model_api import *


class ca_state_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California SSI state supplement eligible person"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://law.justia.com/codes/california/code-wic/division-9/part-3/chapter-3/article-4/"

    def formula(person, period, parameters):
        meets_resource_test = person("meets_ssi_resource_test", period)
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        is_qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return (
            meets_resource_test
            & aged_blind_disabled
            & (is_qualified_noncitizen | is_citizen)
            & is_head_or_spouse
        )

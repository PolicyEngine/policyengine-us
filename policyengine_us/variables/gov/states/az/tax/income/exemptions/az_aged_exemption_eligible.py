from policyengine_us.model_api import *


class az_aged_exemption_eligible(Variable):
    value_type = float
    entity = Person
    label = "Eligible for the Arizona aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)

        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE

        dependent_head = tax_unit("head_is_dependent_elsewhere", period)
        head_eligible = ~dependent_head

        dependent_spouse = tax_unit("spouse_is_dependent_elsewhere", period)
        spouse_eligible = ~dependent_spouse * ~separate

        return (head & head_eligible) | (spouse & spouse_eligible)

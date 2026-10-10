from policyengine_us.model_api import *


class az_aged_exemption_eligible_person(Variable):
    value_type = float
    entity = Person
    label = "Eligible person for the Arizona aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=6"

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)

        tax_unit = person.tax_unit
        filing_status = tax_unit("az_filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE

        # Form 140, Box 8, excludes each spouse only when actually claimed.
        claimed_elsewhere = person("claimed_as_dependent_on_another_return", period)
        return ~claimed_elsewhere & (head | (spouse & ~separate))

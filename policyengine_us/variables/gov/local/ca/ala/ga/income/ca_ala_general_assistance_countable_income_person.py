from policyengine_us.model_api import *


class ca_ala_general_assistance_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = (
        "Alameda County General Assistance countable income for each person"
    )
    defined_for = "is_tax_unit_head_or_spouse"
    reference = "https://www.alamedacountysocialservices.org/acssa-assets/PDF/GA-Policies/GA-Regulations.pdf#page=29"

    adds = "gov.local.ca.ala.general_assistance.countable_income.sources"

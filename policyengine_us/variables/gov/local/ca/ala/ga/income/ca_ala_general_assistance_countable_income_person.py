from policyengine_us.model_api import *


class ca_ala_general_assistance_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Eligible for Alameda County General Assistance based on age requirements"
    defined_for = "is_tax_unit_head_or_spouse"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    adds = "gov.local.ca.ala.general_assistance.countable_income.sources"

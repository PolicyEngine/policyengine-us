from policyengine_us.model_api import *


class ca_ala_general_assistance(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alameda County General Assistance base amount"
    definition_period = MONTH
    defined_for = "ca_ala_general_assistance_income_eligible"
    reference = "https://www.alamedacountysocialservices.org/acssa-assets/PDF/GA-Policies/GA-Regulations.pdf#page=28"

    # Defined for income eligible family, which make sure that countable income is less than based amount
    adds = ["ca_ala_general_assistance_base_amount"]
    subtracts = ["ca_ala_general_assistance_countable_income"]

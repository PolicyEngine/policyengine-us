from policyengine_us.model_api import *


class ca_riv_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County Low Income Home Energy Assistance Program (LIHEAP) countable income"
    definition_period = YEAR
    defined_for = "in_riv"
    reference = "https://capriverside.org/sites/g/files/aldnop136/files/2024-12/2025%20LIHEAP%20CAP%20APPLICATION%20ENGLISH.pdf#page=3"

    adds = "gov.local.ca.riv.cap.liheap.countable_income.sources"

from policyengine_us.model_api import *


class ks_liheap_self_employment_gross_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    default_value = -1
    label = "Kansas LIEAP gross self-employment receipts"
    documentation = "Annual gross receipts before business expenses, including farming. A value of -1 means receipts are unavailable; the countable-income formula then uses reported net self-employment income without taking a second expense deduction."
    reference = "https://content.dcf.ks.gov/ees/keesm/current/keesm13360.htm"

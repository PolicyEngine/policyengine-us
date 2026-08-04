from policyengine_us.model_api import *


class ca_cc_general_assistance_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Contra Costa County General Assistance countable income for each person"
    defined_for = "is_tax_unit_head_or_spouse"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    adds = "gov.local.ca.cc.general_assistance.countable_income.sources"

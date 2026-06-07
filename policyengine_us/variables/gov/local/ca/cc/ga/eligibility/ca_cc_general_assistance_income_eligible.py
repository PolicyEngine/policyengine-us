from policyengine_us.model_api import *


class ca_cc_general_assistance_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Contra Costa County General Assistance based on income requirements"
    definition_period = MONTH
    defined_for = "in_cc"
    # The EHSD program page states GA serves "an adult without dependent
    # children"; families with children are directed to CalWORKs.
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(spm_unit, period, parameters):
        income = spm_unit("ca_cc_general_assistance_countable_income", period)
        base_amount = spm_unit("ca_cc_general_assistance_base_amount", period)
        # General Assistance serves adults without dependent children; families
        # with children are directed to CalWORKs.
        no_children = spm_unit("spm_unit_count_children", period.this_year) == 0
        return (income < base_amount) & no_children

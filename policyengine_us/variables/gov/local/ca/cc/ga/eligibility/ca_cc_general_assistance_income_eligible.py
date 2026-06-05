from policyengine_us.model_api import *


class ca_cc_general_assistance_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Contra Costa County General Assistance based on income requirements"
    definition_period = MONTH
    defined_for = "in_cc"
    reference = (
        "https://ehsd.org/aging-and-adult-services/general-assistance/",
        # Adults with dependent children apply for CalWORKs instead, so the unit
        # must have no children (GA-80 brochure, "adult without dependent children").
        "https://ehsd.org/wp-content/uploads/2024/08/GA-Brochure_ENGLISH_July2024_FA_Digital.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        income = spm_unit("ca_cc_general_assistance_countable_income", period)
        base_amount = spm_unit("ca_cc_general_assistance_base_amount", period)
        # General Assistance serves adults without dependent children; families
        # with children are directed to CalWORKs.
        no_children = spm_unit("spm_unit_count_children", period.this_year) == 0
        return (income < base_amount) & no_children

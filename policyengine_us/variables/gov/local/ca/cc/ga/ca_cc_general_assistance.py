from policyengine_us.model_api import *


class ca_cc_general_assistance(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Contra Costa County General Assistance"
    definition_period = MONTH
    defined_for = "ca_cc_general_assistance_income_eligible"
    reference = (
        "https://ehsd.org/aging-and-adult-services/general-assistance/",
        # Fill-the-gap: the grant standard minus net countable income.
        "https://ehsd.org/wp-content/uploads/2024/08/GA-Brochure_ENGLISH_July2024_FA_Digital.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        base_amount = spm_unit("ca_cc_general_assistance_base_amount", period)
        countable_income = spm_unit("ca_cc_general_assistance_countable_income", period)
        # Floor countable income at zero so net-negative flows (e.g. self-
        # employment losses) cannot inflate the grant above the standard.
        return max_(base_amount - max_(countable_income, 0), 0)

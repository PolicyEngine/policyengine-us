from policyengine_us.model_api import *


class ca_liheap_basic_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP common household eligibility"
    defined_for = StateCode.CA
    # Eligibility details: pages 9, 193, 202-203, 205, 219, and 279.
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=193"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.eligibility
        person = spm_unit.members
        qualified_adult = person("is_citizen_or_legal_immigrant", period) & (
            person("age", period) >= p.applicant_min_age
        )
        expense = spm_unit("heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        heating_type = spm_unit("heating_type", period)
        approved_wood_cost = (heating_type == heating_type.possible_values.WOOD) & (
            spm_unit("ca_liheap_approved_wood_delivery_cost", period) > 0
        )
        # Unsubsidized heat-in-rent is an energy-responsibility proxy; a
        # separately reported charge also permits subsidized households.
        energy_cost = (expense > 0) | (heat_in_rent & ~subsidized) | approved_wood_cost
        return (
            energy_cost
            & (spm_unit.sum(qualified_adult) > 0)
            & spm_unit("ca_liheap_income_eligible", period)
        )

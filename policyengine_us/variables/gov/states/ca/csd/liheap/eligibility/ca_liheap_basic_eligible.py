from policyengine_us.model_api import *


class ca_liheap_basic_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP common household eligibility"
    defined_for = StateCode.CA
    # PDF pages 9,66,193,202-203,205,219,221,264-265,279
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=9"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.eligibility
        person = spm_unit.members
        qualified_adult = person("is_citizen_or_legal_immigrant", period) & (
            person("age", period) >= p.applicant_min_age
        )
        expense = spm_unit("heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        # The guide asks for energy costs and pays electric or gas accounts, so
        # a bill on either account is an energy cost whatever the heating fuel.
        utility_bills = add(
            spm_unit, period, ["pre_subsidy_electricity_expense", "gas_expense"]
        )
        approved_wood_cost = (heating_type == heating_type.possible_values.WOOD) & (
            spm_unit("ca_liheap_approved_wood_delivery_cost", period) > 0
        )
        # Heat in rent stands in for the documented charge of guide 3.3, for
        # subsidized tenants too. A subsidized household with neither a bill nor
        # heat in rent has no energy cost (guide 1.6).
        energy_cost = (
            (expense > 0) | (utility_bills > 0) | heat_in_rent | approved_wood_cost
        )
        return (
            energy_cost
            & (spm_unit.sum(qualified_adult) > 0)
            & spm_unit("ca_liheap_income_eligible", period)
        )

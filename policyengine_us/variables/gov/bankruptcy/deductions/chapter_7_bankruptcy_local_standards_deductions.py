from policyengine_us.model_api import *


class chapter_7_bankruptcy_local_standards_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy local standards deductions"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=3"
    documentation = "Line 8 to line 15 (expect line 12)in form 122A-2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.bankruptcy.local_standards
        size = spm_unit("spm_unit_size", period)
        state = spm_unit.household("state_code", period)
        insurance_and_operating_allowance = (
            p.housing_and_utilities.insurance_and_operating[state][size]
        )

        mortgage_or_rent_allowance = p.housing_and_utilities.mortgage_or_rent[
            state
        ][size]
        housing_expense = spm_unit("housing_cost", period)
        net_mortgage_or_rent_expense = max_(
            mortgage_or_rent_allowance - housing_expense, 0
        )

        qualify_vehicles_owned = spm_unit("vehicles_loan_count", period)
        qualify_vehicles_owned_capped = clip(
            qualify_vehicles_owned, 1, p.vehicle_operation.vehicles_owned_cap
        )
        ownership_costs_allowance = where(
            qualify_vehicles_owned > 0,
            p.vehicle_operation.ownership_costs[qualify_vehicles_owned_capped],
            0,
        )
        vehicle_mortgage_expense = add(
            spm_unit, period, ["vehicle_mortgage_expense"]
        )

        net_vehicle_ownership_expense = max_(
            ownership_costs_allowance - vehicle_mortgage_expense, 0
        )

        public_transportation_allowance = (
            p.vehicle_operation.public_transportation
        )
        public_transportation_expense = add(
            spm_unit, period, ["public_transportation_expense"]
        )

        have_one_or_more_vehicles = qualify_vehicles_owned >= 1
        capped_public_transportation_expense = min_(
            public_transportation_expense, public_transportation_allowance
        )
        additional_public_transportation_allowance = where(
            have_one_or_more_vehicles, capped_public_transportation_expense, 0
        )

        return (
            insurance_and_operating_allowance
            + net_mortgage_or_rent_expense
            + net_vehicle_ownership_expense
            + public_transportation_allowance
            + additional_public_transportation_allowance
        )

from policyengine_us.model_api import *


class chapter_7_bankruptcy_vehicle_operation_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy vehicle operation expense deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=4"
    documentation = "Line 12 in form 122A-2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.bankruptcy.local_standards.vehicle_operation

        qualify_vehicles_owned = spm_unit("vehicles_loan_count", period)
        qualify_vehicles_owned_capped = clip(
            qualify_vehicles_owned, 1, p.vehicles_owned_cap
        )
        northeast = spm_unit.household("northeastern_county", period)
        midwest = spm_unit.household("midwestern_county", period)
        south = spm_unit.household("southern_county", period)
        west = spm_unit.household("western_county", period)
        vehicle_operating_expense_northeast = (
            p.region_operating_costs.northeast[northeast][
                qualify_vehicles_owned_capped
            ]
        )
        vehicle_operating_expense_midwest = p.region_operating_costs.midwest[
            midwest
        ][qualify_vehicles_owned_capped]
        vehicle_operating_expense_south = p.region_operating_costs.south[
            south
        ][qualify_vehicles_owned_capped]
        vehicle_operating_expense_west = p.region_operating_costs.west[west][
            qualify_vehicles_owned_capped
        ]

        return where(
            qualify_vehicles_owned > 0,
            (
                vehicle_operating_expense_northeast
                + vehicle_operating_expense_midwest
                + vehicle_operating_expense_south
                + vehicle_operating_expense_west
            ),
            0,
        )

from policyengine_us.model_api import *


class chapter_7_bankruptcy_vehicle_operation_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vehicle operation expense deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=4"
    documentation = "Line 12 in form 122A-2"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_operating_costs

        qualify_vehicles_owned = add(spm_unit,period,["has_a_vehicle_loan"])
        qualify_vehicles_owned_cap = min_(qualify_vehicles_owned, 2)
        northeast = spm_unit("northeast_county", period)
        midwest = spm_unit("midwest_county", period)
        south = spm_unit("south_county", period)
        west = spm_unit("west_county", period)
        vehicle_operating_expense_northeast = p.northeast[northeast][
            qualify_vehicles_owned_cap
        ]
        vehicle_operating_expense_midwest = p.midwest[midwest][
            qualify_vehicles_owned_cap
        ]
        vehicle_operating_expense_south = p.south[south][
            qualify_vehicles_owned_cap
        ]
        vehicle_operating_expense_west = p.west[west][
            qualify_vehicles_owned_cap
        ]

        return (
            vehicle_operating_expense_northeast
            + vehicle_operating_expense_midwest
            + vehicle_operating_expense_south
            + vehicle_operating_expense_west
        )

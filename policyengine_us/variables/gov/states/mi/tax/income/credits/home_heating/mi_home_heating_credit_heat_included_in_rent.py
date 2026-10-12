from policyengine_us.model_api import *


class mi_home_heating_credit_heat_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Heating costs are included in rent for the Michigan home heating credit"
    documentation = "Whether the claimant's heating costs are included in rent at the time of filing. The standard credit is halved and the alternate credit is unavailable in that case. Defaults to the SPM unit's heat_expense_included_in_rent; set this fact directly when the claimant's arrangement differs. The broader utilities_included_in_rent input does not establish that heat is included."
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-527a",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR-7-Book.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit.spm_unit("heat_expense_included_in_rent", period)

from policyengine_us.model_api import *


class az_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    documentation = (
        "Arizona other subtractions from Arizona gross income reported on "
        "Form 140, Line 36 (Other Subtractions), entered as a positive amount. "
        "Do not include U.S. government interest, public pensions, capital gains, "
        "military pay/retirement, Social Security, 529/ABLE contributions, "
        "adoption expenses, federal Schedule 1-A deductions, the Arizona Families Tax Rebate "
        "(line 36 item U, reported on az_families_tax_rebate_subtraction_reported), "
        "or from 2026 the dependent care expense and 530A distribution subtractions, "
        "which PolicyEngine computes separately."
    )
    reference = "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=16"

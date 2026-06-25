from policyengine_us.model_api import *


class cbo_net_business_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "CBO net business income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.cbo.gov/system/files/2026-02/"
        "51138-2026-02-Revenue-Projections.xlsx"
    )
    adds = [
        "self_employment_income",
        "tax_unit_partnership_s_corp_income",
        "tax_unit_rental_income",
        "farm_rent_income",
    ]

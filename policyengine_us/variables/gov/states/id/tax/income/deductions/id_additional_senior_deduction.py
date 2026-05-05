from policyengine_us.model_api import *


class id_additional_senior_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho additional senior deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3004/",
        "https://legislature.idaho.gov/sessioninfo/2026/legislation/H0559/",
        "https://tax.idaho.gov/pressrelease/update-on-filing-2025-idaho-income-taxes-now-that-conformity-is-law/",
    )
    adds = ["additional_senior_deduction"]

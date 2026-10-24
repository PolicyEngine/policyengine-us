from policyengine_us.model_api import *


class other_medical_expenses(Variable):
    value_type = float
    entity = Person
    label = "Other medical expenses"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
    # CPS ASEC medical care question (PMED_VAL), PDF pages 2-3.
    reference = "https://www.census.gov/content/dam/Census/library/working-papers/2015/demo/Medical-Out-of-pocket-Expenses-CPSASEC-2013-2014.pdf#page=2"
    documentation = (
        "Out-of-pocket costs of this person's own medical care other than "
        "insurance premiums and over-the-counter products, such as copays for "
        "doctor and dentist visits, diagnostic tests, prescription medicine, "
        "glasses and contacts, and medical supplies. Unlike premium inputs, "
        "which sit on the person who paid, these sit on the person cared for "
        "and include amounts other household members paid on that person's "
        "behalf, as the CPS ASEC question asks."
    )

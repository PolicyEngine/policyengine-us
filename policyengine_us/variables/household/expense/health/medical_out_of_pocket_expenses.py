from policyengine_us.model_api import *


class medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medical out of pocket expenses"
    unit = USD
    definition_period = YEAR
    adds = [
        "health_insurance_premiums",
        "other_medical_expenses",
        # Note: Excludes over_the_counter_health_expenses
        # as IRS does not include them in the itemized deduction, and
        # USDA only includes doctor-approved over-the-counter medications
        # in their medical out-of-pocket expenses definition for SNAP.
    ]

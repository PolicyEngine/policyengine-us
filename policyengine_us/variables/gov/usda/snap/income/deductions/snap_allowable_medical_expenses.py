from policyengine_us.model_api import *


class snap_allowable_medical_expenses(Variable):
    value_type = float
    entity = Person
    label = "SNAP allowable medical expenses"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/7/2014#e_5",
        "https://www.law.cornell.edu/cfr/text/7/273.9#d_3",
    ]
    documentation = (
        "Medical expenses allowable for SNAP's excess medical expense "
        "deduction. Federal statute allows actual allowable medical expenses "
        "incurred by elderly or disabled household members, excluding special "
        "diets, above the monthly disregard. The SNAP regulation identifies "
        "allowable costs including medical and dental care, prescription "
        "drugs, practitioner-approved over-the-counter medication, health "
        "insurance premiums, Medicare premiums, cost sharing, medical "
        "supplies, transportation, and related services. Current modeling "
        "uses health insurance premiums and other medical expenses, excluding "
        "general over-the-counter health expenses."
    )

    adds = [
        "medical_expense_health_insurance_premiums",
        "other_medical_expenses",
    ]

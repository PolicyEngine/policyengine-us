from policyengine_us.model_api import *


class heating_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit heating cost (legacy, Michigan home heating credit only)"
    unit = USD
    definition_period = YEAR
    documentation = "Migration to the SPM-unit heating_expense is deferred: the MI home heating credit allows one claimant per household, so the tax-unit allocation rule needs the MCL 206.527a claimant definition first."

    adds = ["heating_expense_person"]

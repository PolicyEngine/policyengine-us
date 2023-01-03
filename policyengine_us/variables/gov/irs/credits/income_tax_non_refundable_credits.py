from policyengine_us.model_api import *


class income_tax_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax non-refundable credits"
    documentation = (
        "Total non-refundable credits used to reduce positive tax liability"
    )
    unit = USD
    adds = [
        "cdcc",
        "elderly_disabled_credit",
        "non_refundable_ctc",
        "non_refundable_american_opportunity_credit",
        "lifetime_learning_credit",
        "retirement_savings_credit",
        "residential_clean_energy_credit",
        "energy_efficient_home_improvement_credit",
        "new_clean_vehicle_credit",
        "used_clean_vehicle_credit",
    ]


c07100 = variable_alias("c07100", income_tax_non_refundable_credits)

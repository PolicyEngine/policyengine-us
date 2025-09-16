from policyengine_us.model_api import *


class mt_agi_before_aggregation(Variable):
    value_type = float
    entity = Person
    label = "Montana Adjusted Gross Income before dependent aggregation"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    documentation = "Calculates Montana AGI at the person level before any aggregation to tax unit head"

    def formula(person, period, parameters):
        # Start with federal AGI
        federal_agi = person("adjusted_gross_income_person", period)

        # Add Montana additions
        additions = person("mt_additions", period)

        # Subtract Montana subtractions
        subtractions = person("mt_subtractions", period)

        # Calculate base Montana AGI
        reduced_agi = max_(federal_agi + additions - subtractions, 0)

        # Apply social security adjustment if applicable (2021-2023)
        p = parameters(period).gov.states.mt.tax.income.social_security
        if p.applies:
            # 2021-2023: apply social security adjustment
            taxable_ss = person("taxable_social_security", period)
            mt_taxable_ss = person("mt_taxable_social_security", period)
            ss_adjustment = mt_taxable_ss - taxable_ss
            return max_(reduced_agi + ss_adjustment, 0)
        else:
            # 2024 and after: no social security adjustment
            return reduced_agi

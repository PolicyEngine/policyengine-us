from policyengine_us.model_api import *


class de_additional_standard_deduction(Variable):
    value_type = float
    entity = Person
    label = "Delaware additional standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.de.tax.income.deductions.standard.additional
        age_eligible = (person("age", period) >= p.age_threshold).astype(int)
        blind_eligible = person("is_blind", period).astype(int)

        return (age_eligible + blind_eligible) * p.amount

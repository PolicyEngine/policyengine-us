from policyengine_us.model_api import *


class az_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://dbmefaapolicy.azdes.gov/index.html#page/FAA6/Dependent_Care_Amount_for_CA.html#wwpID0E0HO0HA"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.income.earned.care_expenses

        person = spm_unit.members
        age = person("age", period.this_year)

        # Actual care expenses (childcare + adult care)
        care_expenses = add(
            spm_unit, period, ["childcare_expenses", "care_expenses"]
        )

        # Calculate eligible deduction for children (based on age)
        is_child = person("is_child", period)
        child_amount = p.child_amounts.calc(age) * is_child

        # Calculate eligible deduction for disabled adults
        disabled_adult = person("is_disabled", period.this_year) & ~is_child
        adult_amount = disabled_adult * p.adult

        # Total eligible deduction
        total_eligible = spm_unit.sum(child_amount + adult_amount)

        # Deduction is capped at actual care expenses
        return min_(care_expenses, total_eligible)

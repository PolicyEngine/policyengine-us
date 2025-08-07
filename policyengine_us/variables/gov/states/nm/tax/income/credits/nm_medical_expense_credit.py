from policyengine_us.model_api import *


class nm_medical_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico unreimbursed medical expense care credit"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503776/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDswgGwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        pcredits = parameters(period).gov.states.nm.tax.income.credits
        p = pcredits.unreimbursed_medical_care_expense
        age = person("age", period)
        medical_expense = add(
            tax_unit, period, ["medical_out_of_pocket_expenses"]
        )
        age_eligible = tax_unit.any(age >= p.age_eligibility)
        expense_eligible = medical_expense >= p.min_expenses
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
        eligible = age_eligible & expense_eligible & ~dependent_elsewhere
        # exemption is halved for married filing separately
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        denominator = where(separate, 2, 1)
        numerator = eligible * p.amount
        return numerator / denominator

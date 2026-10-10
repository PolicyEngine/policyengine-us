from policyengine_us.model_api import *


class nm_medical_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico unreimbursed medical expense care credit"
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503776/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDswgGwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA",
        # PDF pages 2, 9
        "https://realfile.tax.newmexico.gov/2025pit-rc-ins.pdf#page=2",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        pcredits = parameters(period).gov.states.nm.tax.income.credits
        p = pcredits.unreimbursed_medical_care_expense
        age = person("age", period)
        medical_expense = tax_unit("itemized_medical_expenses", period)
        expense_eligible = medical_expense >= p.min_expenses
        # NMSA 7-2-18.13(A) allows the credit to "a taxpayer ... who is
        # sixty-five years of age or older and who is not a dependent of
        # another taxpayer", so both tests apply to the same filer: a
        # dependent aged 65 or older does not qualify the return (PIT-RC line
        # 23: "If you or your spouse are 65 years of age or older"), and on a
        # joint return a spouse who is not a dependent may still qualify
        # ("If you are a dependent with a spouse who was not a dependent of
        # another taxpayer, your spouse may still qualify").
        filer = person("is_tax_unit_head_or_spouse", period)
        claimable = person("claimable_as_dependent_on_another_return", period)
        qualifying_filer = filer & (age >= p.age_eligibility) & ~claimable
        eligible = tax_unit.any(qualifying_filer) & expense_eligible
        # exemption is halved for married filing separately
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        denominator = where(separate, 2, 1)
        numerator = eligible * p.amount
        return numerator / denominator

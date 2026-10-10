from policyengine_us.model_api import *


class nm_medical_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico unreimbursed medical expense care credit"
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503776/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDswgGwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA",
        "https://realfile.tax.newmexico.gov/2025pit-rc-ins.pdf#page=2",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        pcredits = parameters(period).gov.states.nm.tax.income.credits
        p = pcredits.unreimbursed_medical_care_expense
        age = person("age", period)
        medical_expense = tax_unit("itemized_medical_expenses", period)
        aged = age >= p.age_eligibility
        expense_eligible = medical_expense >= p.min_expenses
        # NMSA 7-2-18.13(A) allows the credit to a taxpayer "who is sixty-five
        # years of age or older and who is not a dependent of another
        # taxpayer", and the PIT-RC instructions let a spouse who is not a
        # dependent claim it when the other spouse is. So when a filer is a
        # dependent elsewhere, a filer who is not must be 65 or older.
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimable_as_dependent_on_another_return", period)
        independent_aged_filer = tax_unit.any(filer & ~claimed & aged)
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        age_eligible = where(
            dependent_filer, independent_aged_filer, tax_unit.any(aged)
        )
        eligible = age_eligible & expense_eligible
        # exemption is halved for married filing separately
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        denominator = where(separate, 2, 1)
        numerator = eligible * p.amount
        return numerator / denominator

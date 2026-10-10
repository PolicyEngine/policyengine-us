from policyengine_us.model_api import *


class nm_medical_expense_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico unreimbursed medical expense care exemption"
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503680/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsADh4BKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA",
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/0558a902-6362-47ca-8e3b-7cca3bc69b9d/2025%20PIT%20Packet_Final.pdf#page=50",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.nm.tax.income.exemptions.unreimbursed_medical_care_expense
        age = person("age", period)
        medical_expense = tax_unit("itemized_medical_expenses", period)
        # NMSA 7-2-5.9(A) allows the exemption to "any individual sixty-five
        # years of age or older" for expenses paid "for that individual or
        # for the individual's spouse or dependent", and PIT-ADJ line 18 asks
        # whether "you or your spouse are 65 years of age or older". A
        # dependent aged 65 or older does not qualify the return.
        filer = person("is_tax_unit_head_or_spouse", period)
        age_eligible = tax_unit.any(filer & (age >= p.age_eligibility))
        # NMSA 7-2-5.9(A) requires expenses that "exceed twenty-eight thousand
        # dollars ($28,000)"; PIT-ADJ line 18 instructions allow expenses "of
        # $28,000 or more". This keeps the instructions' reading, under which
        # expenses of exactly $28,000 qualify, until the conflict is resolved.
        expense_eligible = medical_expense >= p.min_expenses
        eligible = age_eligible & expense_eligible
        # Neither 7-2-5.9 nor the PIT-ADJ line 18 instructions halve the
        # exemption for married individuals filing separately. Sections that
        # do, such as the 65+ medical care credit (7-2-18.13(B)) and the organ
        # donation deduction (7-2-36(B), the next PIT-ADJ line), say so.
        return eligible * p.amount

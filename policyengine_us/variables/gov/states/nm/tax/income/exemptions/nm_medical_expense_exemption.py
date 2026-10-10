from policyengine_us.model_api import *


class nm_medical_expense_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico unreimbursed medical expense care exemption"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503680/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsADh4BKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    documentation = (
        "Senior medical exemption based on gross unreimbursed costs paid, "
        "preserving premiums deducted through the federal self-employed health "
        "insurance ALD. The federal medical amount plus excluded premiums "
        "preserves both caller-supplied subtotals and computed gross costs. "
        "This assumes qualifying costs were funded from income "
        "included in AGI. Premium inputs use payer attribution: each person "
        "reports premiums that person paid, including family coverage regardless "
        "of whom it covers. "
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.nm.tax.income.exemptions.unreimbursed_medical_care_expense
        age = person("age", period)
        # Restore gross paid costs while retaining supplied federal subtotals.
        medical_expense = add(
            tax_unit,
            period,
            [
                "itemized_medical_expenses",
                "itemized_medical_expenses_excluded_premiums",
            ],
        )
        age_eligible = tax_unit.any(age >= p.age_eligibility)
        expense_eligible = medical_expense >= p.min_expenses
        eligible = age_eligible & expense_eligible
        # Exemption is halved for married filing separately
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        denominator = where(separate, 2, 1)
        numerator = eligible * p.amount
        return numerator / denominator

from policyengine_us.model_api import *


class mo_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri adjusted gross income"
    documentation = (
        "Each filer adds Missouri additions to federal adjusted gross income "
        "and subtracts Missouri subtractions on Form MO-1040, Line 5. "
        "Spouses can report negative amounts and add both columns on Line 6."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf",
        # PDF pages 7, 22: spouses can report negative Missouri AGI on
        # Line 5 and add their two columns on Line 6. A spouse with negative
        # income uses zero percent on Line 7.
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2023.pdf#page=7",
        # 12 CSR 10-2.010(4)(A)2 (effective February 29, 2024): a spouse's
        # Missouri AGI of -$4,000 after a subtraction.
        "https://dor.mo.gov/resources/official-final-rules/documents/12_CSR_10-2_010.pdf#page=5",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.121",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        federal_agi = person("mo_federal_adjusted_gross_income", period)
        additions = person("mo_additions", period)
        income_before_subtractions = federal_agi + additions
        subtractions = person("mo_agi_subtractions", period)
        p = parameters(period).gov.states.mo.tax.income.subtractions
        if p.plan_529_contributions.limited_to_own_agi:
            # Under 12 CSR 10-2.010(4)(A)3 (effective February 29, 2024), each
            # spouse limits the MOST subtraction to their own Missouri AGI.
            # We take MOST after other subtractions.
            most = person("mo_529_deduction", period)
            other_subtractions = max_(0, subtractions - most)
            allowed_most = min_(
                most, max_(0, income_before_subtractions - other_subtractions)
            )
            subtractions = other_subtractions + allowed_most
        # A tax unit dependent's Missouri AGI is on their own return.
        filer = ~person("is_tax_unit_dependent", period)
        return filer * (income_before_subtractions - subtractions)

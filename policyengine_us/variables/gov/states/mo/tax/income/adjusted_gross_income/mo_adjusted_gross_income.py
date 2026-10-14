from policyengine_us.model_api import *


class mo_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri adjusted gross income"
    documentation = (
        "Each filer's Missouri adjusted gross income on Form MO-1040, Line 5: "
        "their federal adjusted gross income less their Missouri "
        "subtractions. A spouse's amount can be negative; Line 6 adds the two "
        "columns."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf",
        # PDF pages 7, 22: the Line 7 note on a spouse with negative income;
        # Line 5, "Subtract Line 4 from Line 3", and Line 6, "Add columns 5Y
        # and 5S".
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2023.pdf#page=7",
        # 12 CSR 10-2.010(4)(A)2 (effective February 29, 2024): a spouse's
        # Missouri AGI of -$4,000 after a subtraction.
        "https://dor.mo.gov/resources/official-final-rules/documents/12_CSR_10-2_010.pdf#page=5",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.121",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        federal_agi = person("mo_federal_adjusted_gross_income", period)
        # Missouri additions (Line 2) are not modeled.
        subtractions = person("mo_agi_subtractions", period)
        p = parameters(period).gov.states.mo.tax.income.subtractions
        if p.plan_529_contributions.limited_to_own_agi:
            # 12 CSR 10-2.010(4)(A)3 (effective February 29, 2024): "the MOST
            # subtraction is limited to the spouse's Missouri adjusted gross
            # income". It is taken after the other subtractions.
            most = person("mo_529_deduction", period)
            other_subtractions = max_(0, subtractions - most)
            allowed_most = min_(most, max_(0, federal_agi - other_subtractions))
            subtractions = other_subtractions + allowed_most
        # A tax unit dependent's Missouri AGI is on their own return.
        filer = ~person("is_tax_unit_dependent", period)
        return filer * (federal_agi - subtractions)

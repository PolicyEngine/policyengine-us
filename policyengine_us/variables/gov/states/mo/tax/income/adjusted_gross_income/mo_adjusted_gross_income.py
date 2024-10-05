from policyengine_us.model_api import *


class mo_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.121",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        gross_income = person("irs_gross_income", period)
        # subtract federal above-the-line deductions (ALDs) by person
        # ... subtract some ALDs explicitly by person
        PERSONAL_ALDS = [
            "self_employment_tax_ald_person",
            "self_employed_health_insurance_ald_person",
            "self_employed_pension_contribution_ald_person",
        ]
        tax_unit = person.tax_unit
        ind_total_personal_alds = add(person, period, PERSONAL_ALDS)
        unit_total_personal_alds = add(tax_unit, period, PERSONAL_ALDS)
        # ... subtract remaining ALDs by adhoc allocation between spouses
        unit_total_alds = tax_unit("above_the_line_deductions", period)
        unit_remaining_alds = unit_total_alds - unit_total_personal_alds
        filing_status = person.tax_unit("filing_status", period)
        is_married = filing_status == filing_status.possible_values.JOINT
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        allocated_alds = where(
            is_head | is_spouse,
            unit_remaining_alds / where(is_married, 2, 1),
            0,
        )
        fed_agi = gross_income - ind_total_personal_alds - allocated_alds
        # return MO AGI including MO additions and MO subtractions
        subtractions = person("mo_qualified_health_insurance_premiums", period)
        return max_(0, fed_agi - subtractions)

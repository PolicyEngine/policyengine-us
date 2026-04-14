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
        # Allocate remaining ALDs proportionally based on gross income
        # to avoid losing deductions when one spouse has no income.
        # Use np.divide with mask to avoid divide-by-zero warnings.
        unit_gross_income = tax_unit.sum(gross_income)
        mask = unit_gross_income > 0
        # Default: head gets 100%, others get 0% (used when unit has no income)
        default_share = where(is_head, 1.0, 0.0)
        allocation_share = np.divide(
            gross_income,
            unit_gross_income,
            out=default_share.copy(),  # Copy to avoid modifying default_share
            where=mask,
        )
        allocated_alds = where(
            is_head | is_spouse,
            unit_remaining_alds * allocation_share,
            0,
        )
        fed_agi = gross_income - ind_total_personal_alds - allocated_alds
        # return MO AGI including MO additions and MO subtractions
        subtractions = person("mo_agi_subtractions", period)
        return max_(0, fed_agi - subtractions)

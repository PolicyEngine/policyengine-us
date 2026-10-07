from policyengine_us.model_api import *


# Above-the-line deductions the model attributes to the person who has them.
TAX_UNIT_AGI_ALDS_WITH_PERSON_LEVEL_EQUIVALENTS = {
    "self_employment_tax_ald": "self_employment_tax_ald_person",
    "self_employed_health_insurance_ald": "self_employed_health_insurance_ald_person",
    "self_employed_pension_contribution_ald": "self_employed_pension_contribution_ald_person",
    "alimony_expense_ald": "alimony_expense_ald_person",
    # Each educator's own capped expenses, a tax unit dependent's included,
    # since the dependent deducts them on their own return.
    "educator_expense_ald": "educator_expense_ald_person",
}


class medicaid_adjusted_gross_income_person(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income for Medicaid MAGI household rules"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    def formula(person, period, parameters):
        gross_income = person("medicaid_irs_gross_income", period)
        p = parameters(period).gov.irs.ald
        all_alds = p.deductions
        # Each listed deduction with a person-level equivalent goes to the
        # person who has it, reconciled to the tax-unit amount when that is an
        # input or a reform changes it.
        ald_sum_person = 0
        for ald in all_alds:
            if ald in TAX_UNIT_AGI_ALDS_WITH_PERSON_LEVEL_EQUIVALENTS:
                ald_sum_person = ald_sum_person + person_share_of_tax_unit_amount(
                    person,
                    period,
                    ald,
                    TAX_UNIT_AGI_ALDS_WITH_PERSON_LEVEL_EQUIVALENTS[ald],
                )
        other_alds = [
            ald
            for ald in all_alds
            if ald not in TAX_UNIT_AGI_ALDS_WITH_PERSON_LEVEL_EQUIVALENTS
        ]
        # The head's and spouse's deductions are shared between them, as on
        # their return. A tax unit dependent's own person-level deductions,
        # such as their IRA deduction, reduce the dependent's own AGI, since
        # the dependent's income is figured on the dependent's own return.
        # Amounts that are the filer's even when recorded on a dependent stay
        # with the head and spouse.
        filer_amounts = p.filer_amounts_recorded_on_dependents
        ald_sum_taxunit = tax_unit_non_dep_add(
            person.tax_unit,
            period,
            other_alds,
            include_dependents=filer_amounts,
        )
        person_level_other_alds = [
            ald
            for ald in other_alds
            if person.entity.get_variable(ald, check_existence=True).entity.is_person
            and ald not in filer_amounts
        ]
        is_dependent = person("is_tax_unit_dependent", period)
        dependent_own_ald = is_dependent * add(person, period, person_level_other_alds)
        filing_status = person.tax_unit("filing_status", period)
        frac = where(
            filing_status == filing_status.possible_values.JOINT,
            0.5,
            1.0,
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        shared_ald = head_or_spouse * ald_sum_taxunit * frac
        agi = gross_income - ald_sum_person - dependent_own_ald - shared_ald

        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            basic_income = person.tax_unit("basic_income", period)
            agi += head_or_spouse * basic_income * frac

        return agi

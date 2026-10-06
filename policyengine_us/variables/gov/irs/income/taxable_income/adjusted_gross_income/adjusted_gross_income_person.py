from policyengine_us.model_api import *


class adjusted_gross_income_person(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    def formula(person, period, parameters):
        gross_income = person("irs_gross_income", period)
        # A tax unit dependent's deductions are on their own return, as
        # irs_gross_income leaves their income off this one.
        not_dependent = ~person("is_tax_unit_dependent", period)
        # calculate ald sums by person
        PERSON_ALDS = [
            "self_employment_tax_ald",
            "self_employed_health_insurance_ald",
            "self_employed_pension_contribution_ald",
        ]
        person_ald_vars = [f"{ald}_person" for ald in PERSON_ALDS]
        ald_sum_person = not_dependent * add(person, period, person_ald_vars)
        # split other alds evenly between head and spouse
        p = parameters(period).gov.irs.ald
        all_alds = p.deductions
        other_alds = sorted(set(all_alds) - set(PERSON_ALDS))
        ald_sum_taxunit = tax_unit_non_dep_add(
            person.tax_unit,
            period,
            other_alds,
            include_dependents=p.filer_amounts_recorded_on_dependents,
        )
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        fstatus = person.tax_unit("filing_status", period)
        frac = where(fstatus == fstatus.possible_values.JOINT, 0.5, 1.0)
        ald_sum_taxunit_shared = (is_head | is_spouse) * ald_sum_taxunit * frac
        # calculate AGI by person
        agi = gross_income - ald_sum_person - ald_sum_taxunit_shared
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            basic_income = person.tax_unit("basic_income", period)
            # split basic income evenly between head and spouse
            basic_income_shared = (is_head | is_spouse) * basic_income * frac
            agi += basic_income_shared
        return agi

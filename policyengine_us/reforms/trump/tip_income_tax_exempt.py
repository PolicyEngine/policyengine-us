from policyengine_us.model_api import *


def create_trump_tip_income_tax_exempt() -> Reform:
    class adjusted_gross_income(Variable):
        value_type = float
        entity = TaxUnit
        label = "Adjusted gross income"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/62"

        def formula(tax_unit, period, parameters):
            total_gross_income = add(tax_unit, period, ["irs_gross_income"])
            tip_income = add(tax_unit, period, ["tip_income"])
            gross_income = max_(0, total_gross_income - tip_income)
            above_the_line_deductions = tax_unit(
                "above_the_line_deductions", period
            )
            agi = gross_income - above_the_line_deductions
            if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
                agi += add(tax_unit, period, ["basic_income"])
            return agi

    class adjusted_gross_income_person(Variable):
        value_type = float
        entity = Person
        label = "Federal adjusted gross income for each person"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/62"

        def formula(person, period, parameters):
            total_gross_income = person("irs_gross_income", period)
            tip_income = person("tip_income", period)
            gross_income = max_(0, total_gross_income - tip_income)
            # calculate ald sums by person
            PERSON_ALDS = [
                "self_employment_tax_ald",
                "self_employed_health_insurance_ald",
                "self_employed_pension_contribution_ald",
            ]
            person_ald_vars = [f"{ald}_person" for ald in PERSON_ALDS]
            ald_sum_person = add(person, period, person_ald_vars)
            # split other alds evenly between head and spouse
            all_alds = parameters(period).gov.irs.ald.deductions
            other_alds = list(set(all_alds) - set(PERSON_ALDS))
            ald_sum_taxunit = add(person.tax_unit, period, other_alds)
            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)
            fstatus = person.tax_unit("filing_status", period)
            frac = where(fstatus == fstatus.possible_values.JOINT, 0.5, 1.0)
            ald_sum_taxunit_shared = (
                (is_head | is_spouse) * ald_sum_taxunit * frac
            )
            # calculate AGI by person
            agi = gross_income - ald_sum_person - ald_sum_taxunit_shared
            if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
                basic_income = person.tax_unit("basic_income", period)
                # split basic income evenly between head and spouse
                basic_income_shared = (
                    (is_head | is_spouse) * basic_income * frac
                )
                agi += basic_income_shared
            return agi

    class payroll_tax_gross_wages(Variable):
        value_type = float
        entity = Person
        label = "Gross wages and salaries for payroll taxes"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            income = person("irs_employment_income", period)
            p = parameters(period).gov.contrib.trump.tip_income_tax_exempt
            if p.payroll_tax_exempt:
                tip_income = person("tip_income", period)
                return max_(income - tip_income, 0)
            return income

    class tip_income(Variable):
        value_type = float
        entity = Person
        label = "Tip income"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/cfr/text/26/31.3402(k)-1"

    class reform(Reform):
        def apply(self):
            self.update_variable(adjusted_gross_income)
            self.update_variable(tip_income)
            self.update_variable(payroll_tax_gross_wages)
            self.update_variable(adjusted_gross_income_person)

    return reform


def create_trump_tip_income_tax_exempt_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_trump_tip_income_tax_exempt()

    p = parameters(period).gov.contrib.trump.tip_income_tax_exempt

    if p.in_effect:
        return create_trump_tip_income_tax_exempt()
    else:
        return None


tip_income_tax_exempt = create_trump_tip_income_tax_exempt_reform(
    None, None, bypass=True
)

from policyengine_us.model_api import *


def create_ny_working_families_tax_credit() -> Reform:
    class ny_working_families_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York Working Families Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.wftc
            income = tax_unit("ny_agi", period)
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            reduction = where(joint, p.reduction.married.calc(income), p.reduction.single.calc(income))
            children = tax_unit("ny_wftc_eligible_children", period)
            max_amount = p.amount.max * children
            min_amount = p.amount.min * children
            return max_(min_amount, max_amount - reduction)


    class ny_wftc_eligible_children(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York Working Families Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            p = parameters(period).gov.contrib.states.ny.wftc
            age_eligible = age < p.child_age_threshold
            eligible_child = is_dependent & age_eligible
            return tax_unit.sum(eligible_child)

    

    class ny_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York EITC"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/bills/2023/S277/amendment/B"  
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            federal_eitc = tax_unit("eitc", period)
            p = parameters(period).gov.contrib.states.ny.wftc.eitc
            tentative_nys_eitc = federal_eitc * p.match
            household_credit = tax_unit("ny_household_credit", period)
            return max_(0, tentative_nys_eitc - household_credit)


# TOINCLUDE: THE  REDUCTION  DESCRIBED  IN  THIS  PARAGRAPH SHALL APPLY ONLY TO THE
# PORTION OF A TAXPAYER'S EARNED INCOME CREDIT  THAT  IS  ATTRIBUTABLE  TO
# QUALIFYING  CHILDREN  AS DEFINED IN PARAGRAPH ONE OF SUBSECTION (C-2) OF
# THIS SECTION. A TAXPAYER SHALL CONTINUE TO BE ALLOWED THE EARNED  INCOME
# CREDIT  FOR THE PORTIONS OF SUCH CREDIT ATTRIBUTABLE TO ANOTHER QUALIFY-
# ING CHILD, AS DEFINED IN 26 USC  §152(C),  OR  QUALIFYING  RELATIVE,  AS
# DEFINED  IN 26 USC §152(D), WHO DO NOT MEET THE DEFINITION OF QUALIFYING
# CHILD IN PARAGRAPH ONE OF SUBSECTION (C-2) OF THIS SECTION.


    class ny_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY exemptions"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/laws/TAX/616"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            dependent = person("is_tax_unit_dependent", period)
            p = parameters(period).gov.contrib.states.ny.wftc.dependent_exemption
            age = person("age", period)
            eligible_dependent = dependent & (age >= p.child_age_threshold)
            count_dependents = tax_unit.sum(eligible_dependent)
            dependent_exemption = parameters(
                period
            ).gov.states.ny.tax.income.exemptions.dependent
            return dependent_exemption * count_dependents



    class reform(Reform):
        def apply(self):
            self.add_variable(ny_working_families_tax_credit)
            self.add_variable(ny_wftc_eligible_children)
            self.update_variable(ny_eitc)
            self.neutralize_variable("ny_ctc")
            self.update_variable(ny_exemptions)

    return reform


def create_ny_working_families_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ny_working_families_tax_credit()

    p = parameters(period).gov.contrib.states.ny.wftc

    if p.in_effect:
        return create_ny_working_families_tax_credit()
    else:
        return None


ny_working_families_tax_credit = create_ny_working_families_tax_credit_reform(
    None, None, bypass=True
)

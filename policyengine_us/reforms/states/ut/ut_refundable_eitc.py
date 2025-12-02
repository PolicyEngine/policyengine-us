from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ut_refundable_eitc() -> Reform:
    class ut_has_qualifying_child_for_refundable_eitc(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Utah tax unit has qualifying child for refundable EITC"
        defined_for = StateCode.UT
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            p = parameters(period).gov.contrib.states.ut.eitc
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            is_qualifying_child = (age <= p.max_age) & is_dependent
            return tax_unit.any(is_qualifying_child)

    class ut_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah refundable EITC"
        unit = USD
        definition_period = YEAR
        defined_for = "ut_has_qualifying_child_for_refundable_eitc"

        adds = ["ut_eitc"]

    class ut_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah Earned Income Tax Credit"
        unit = USD
        documentation = "This credit is a fraction of the federal EITC."
        definition_period = YEAR
        defined_for = StateCode.UT
        reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1044.html?v=C59-10-S1044_2022050420220504"

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.states.ut.tax.income.credits.earned_income
            federal_eitc = tax_unit("eitc", period)
            return p.rate * federal_eitc

    class ut_non_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah non-refundable EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        adds = ["ut_eitc"]
        subtracts = ["ut_refundable_eitc"]

    class ut_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah non-refundable tax credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        adds = [
            "ut_non_refundable_eitc",
            "ut_retirement_credit",
            "ut_ss_benefits_credit",
            "ut_at_home_parent_credit",
            "ut_ctc",
        ]

    class ut_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        adds = ["ut_refundable_eitc"]

    class reform(Reform):
        def apply(self):
            self.update_variable(ut_has_qualifying_child_for_refundable_eitc)
            self.update_variable(ut_refundable_eitc)
            self.update_variable(ut_non_refundable_eitc)
            self.update_variable(ut_eitc)
            self.update_variable(ut_non_refundable_credits)
            self.update_variable(ut_refundable_credits)

    return reform


def create_ut_refundable_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_refundable_eitc()

    p = parameters.gov.contrib.states.ut.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_refundable_eitc()
    else:
        return None


ut_refundable_eitc = create_ut_refundable_eitc_reform(None, None, bypass=True)

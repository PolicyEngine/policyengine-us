from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ut_dependent_exemption_reform() -> Reform:
    class ut_personal_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah personal exemption"
        unit = USD
        defined_for = StateCode.UT
        definition_period = YEAR
        reference = (
            "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323",  # Form TC-40, Line 11
            "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html",  # 59-10-1018 (1)(g)
            "https://tax.utah.gov/forms/current/tc-40inst.pdf#page=4",  # What's New, Additional dependent for taxpayer tax credit
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ut.tax.income.credits.taxpayer
            pc = parameters(period).gov.contrib.states.ut.dependent_exemption
            person = tax_unit.members
            age = person("age", period)
            dependent = person("is_tax_unit_dependent", period)
            # Dependents under the age threshold (all dependents when the
            # age limit is off) take the contrib amount; older dependents
            # keep the baseline (uprated) personal-exemption amount.
            if pc.age_limit.in_effect:
                young = dependent & (age < pc.age_limit.threshold)
            else:
                young = dependent
            count_young = tax_unit.sum(young)
            count_older = tax_unit.sum(dependent) - count_young
            if pc.amount < 0:
                reform_amount = p.personal_exemption
            else:
                reform_amount = pc.amount
            exemption = reform_amount * count_young + p.personal_exemption * count_older
            if p.in_effect:
                # 59-10-1018 (1)(g): the extra exemption for dependents born
                # during the tax year. Newborns are always under any age
                # threshold, so the extra exemption takes the reform amount.
                additional_dependents = tax_unit(
                    "ut_personal_exemption_additional_dependents", period
                )
                exemption += reform_amount * additional_dependents
            return exemption

    class reform(Reform):
        def apply(self):
            self.update_variable(ut_personal_exemption)

    return reform


def create_ut_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_dependent_exemption_reform()

    p = parameters.gov.contrib.states.ut.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_dependent_exemption_reform()
    else:
        return None


ut_dependent_exemption_reform = create_ut_dependent_exemption_reform_fn(
    None, None, bypass=True
)

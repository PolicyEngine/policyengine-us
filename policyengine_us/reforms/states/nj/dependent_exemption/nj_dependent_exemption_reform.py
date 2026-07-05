from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nj_dependent_exemption() -> Reform:
    class nj_dependents_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "New Jersey qualified and other dependent children exemption"
        reference = "https://casetext.com/statute/new-jersey-statutes/title-54a-new-jersey-gross-income-tax-act/chapter-54a3-personal-exemptions-and-deductions/section-54a3-1-personal-exemptions-and-deductions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NJ

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.nj.dependent_exemption
            baseline = parameters(
                period
            ).gov.states.nj.tax.income.exemptions.dependents.amount
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            # Age gate: when in effect, only dependents under the chosen age
            # are re-priced to the reform amount; older dependents keep the
            # baseline exemption. Otherwise every dependent is re-priced,
            # matching the baseline tax_unit_dependents count at the default.
            if p.age_limit.in_effect:
                age = person("age", period)
                young = is_dependent & (age < p.age_limit.threshold)
                older = is_dependent & (age >= p.age_limit.threshold)
                young_count = tax_unit.sum(young)
                older_count = tax_unit.sum(older)
                return young_count * p.amount + older_count * baseline
            count = tax_unit.sum(is_dependent)
            return count * p.amount

    class reform(Reform):
        def apply(self):
            self.update_variable(nj_dependents_exemption)

    return reform


def create_nj_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_nj_dependent_exemption()

    p = parameters.gov.contrib.states.nj.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nj_dependent_exemption()
    else:
        return None


nj_dependent_exemption_reform = create_nj_dependent_exemption_reform_fn(
    None, None, bypass=True
)

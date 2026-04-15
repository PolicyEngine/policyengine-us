from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_mt_ctc() -> Reform:
    """Flexible Montana Child Tax Credit reform for general policy modeling.

    Key differences from HB268:
    - No investment income requirement
    - Earned income requirement is toggled via parameter
    - Three-bracket age-based credit amounts
    - Phase-out by filing status (same as newborn credit)
    """

    class mt_ctc(Variable):
        value_type = float
        entity = Person
        label = "Montana Child Tax Credit"
        definition_period = YEAR
        unit = USD
        defined_for = StateCode.MT

        def formula(person, period, parameters):
            eligible = person.tax_unit("mt_ctc_eligible", period)
            p = parameters(period).gov.contrib.states.mt.ctc
            age = person("age", period)
            # Include ctc_qualifying_child (0-16) plus 17-year-old dependents
            is_ctc_child = person("ctc_qualifying_child", period)
            is_17_dependent = (age == 17) & person("is_tax_unit_dependent", period)
            is_qualifying = is_ctc_child | is_17_dependent
            # Calculate credit amount based on age brackets
            child_credit = p.amount.calc(age) * is_qualifying
            credit_amount = person.tax_unit.sum(child_credit)
            # Credit gets reduced by an amount for each increment
            # that AGI exceeds the threshold (by filing status)
            agi = person.tax_unit("adjusted_gross_income", period)
            filing_status = person.tax_unit("filing_status", period)
            threshold = p.reduction.threshold[filing_status]
            excess = max_(agi - threshold, 0)
            # Ceiling: any fraction of an increment triggers reduction
            increments = np.ceil(excess / p.reduction.increment)
            reduction = p.reduction.amount * increments
            credit = max_(credit_amount - reduction, 0)
            is_head = person("is_tax_unit_head", period)
            return is_head * eligible * credit

    class mt_ctc_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for the Montana Child Tax Credit"
        definition_period = YEAR
        defined_for = StateCode.MT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mt.ctc
            # Must have at least one qualifying child (0-17)
            has_ctc_child = tax_unit("ctc_qualifying_children", period) > 0
            person = tax_unit.members
            age = person("age", period)
            has_17_dependent = tax_unit.any(
                (age == 17) & person("is_tax_unit_dependent", period)
            )
            has_qualifying_child = has_ctc_child | has_17_dependent
            # Earned income requirement is optional
            earned_income_required = p.earned_income_requirement.in_effect
            earned_income = tax_unit("tax_unit_earned_income", period)
            has_earned_income = earned_income > 0
            earned_income_eligible = where(
                earned_income_required,
                has_earned_income,
                True,
            )
            return has_qualifying_child & earned_income_eligible

    def modify_parameters(parameters):
        parameters.gov.states.mt.tax.income.credits.refundable.update(
            start=instant("2023-01-01"),
            stop=instant("2031-12-31"),
            value=["mt_ctc", "mt_eitc"],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(mt_ctc)
            self.update_variable(mt_ctc_eligible)
            self.modify_parameters(modify_parameters)

    return reform


def create_mt_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mt_ctc()

    p = parameters.gov.contrib.states.mt.ctc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mt_ctc()
    else:
        return None


mt_ctc = create_mt_ctc_reform(None, None, bypass=True)

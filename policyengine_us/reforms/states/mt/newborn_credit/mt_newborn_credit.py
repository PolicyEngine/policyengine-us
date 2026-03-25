from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_mt_newborn_credit() -> Reform:
    """Montana newborn credit reform.

    Provides a $1,000 refundable credit per qualifying child under
    age 1 with phase-out based on AGI. This is a PolicyEngine-designed
    contrib reform; no enacted legislation exists.
    """

    class mt_newborn_credit_eligible_child(Variable):
        value_type = bool
        entity = Person
        label = "Montana newborn credit eligible child"
        definition_period = YEAR
        defined_for = StateCode.MT

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.states.mt.newborn_credit
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            has_ssn = person("meets_eitc_identification_requirements", period)
            return (age < p.age_limit) & is_dependent & has_ssn

    class mt_newborn_credit_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for the Montana newborn credit"
        definition_period = YEAR
        defined_for = StateCode.MT

        def formula(tax_unit, period, parameters):
            has_earned_income = tax_unit("tax_unit_earned_income", period) > 0
            has_qualifying_children = (
                add(
                    tax_unit,
                    period,
                    ["mt_newborn_credit_eligible_child"],
                )
                > 0
            )
            person = tax_unit.members
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            has_ssn = person("meets_eitc_identification_requirements", period)
            # Uses any() not all(): at least one filer needs SSN,
            # unlike EITC which requires all filers to have SSN.
            filer_has_ssn = tax_unit.any(head_or_spouse & has_ssn)
            return has_earned_income & has_qualifying_children & filer_has_ssn

    class mt_newborn_credit(Variable):
        value_type = float
        entity = Person
        label = "Montana newborn credit"
        definition_period = YEAR
        unit = USD
        defined_for = StateCode.MT

        def formula(person, period, parameters):
            # Check tax unit eligibility
            eligible = person.tax_unit("mt_newborn_credit_eligible", period)
            p = parameters(period).gov.contrib.states.mt.newborn_credit
            qualifying_children = add(
                person.tax_unit, period, ["mt_newborn_credit_eligible_child"]
            )
            base_credit = p.amount * qualifying_children
            filing_status = person.tax_unit("filing_status", period)
            agi = person.tax_unit("adjusted_gross_income", period)
            threshold = p.reduction.threshold[filing_status]
            excess = max_(agi - threshold, 0)
            # Ceiling: any fraction of an increment triggers reduction
            increments = np.ceil(excess / p.reduction.increment)
            reduction = p.reduction.amount * increments
            credit = max_(base_credit - reduction, 0)
            # Assign credit only to head to avoid duplication
            is_head = person("is_tax_unit_head", period)
            return is_head * eligible * credit

    def modify_parameters(parameters):
        # NOTE: MT HB268 reform hard-codes the refundable credits list,
        # so this reform must run after MT HB268 in reforms.py to
        # correctly append mt_newborn_credit via read-then-append.
        refundable = parameters.gov.states.mt.tax.income.credits.refundable
        current_refundable = refundable(instant("2027-01-01"))
        if "mt_newborn_credit" not in current_refundable:
            new_refundable = list(current_refundable) + ["mt_newborn_credit"]
            refundable.update(
                start=instant("2027-01-01"),
                stop=instant("2100-12-31"),
                value=new_refundable,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(mt_newborn_credit_eligible_child)
            self.update_variable(mt_newborn_credit_eligible)
            self.update_variable(mt_newborn_credit)
            self.modify_parameters(modify_parameters)

    return reform


def create_mt_newborn_credit_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mt_newborn_credit()

    p = parameters.gov.contrib.states.mt.newborn_credit

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mt_newborn_credit()
    else:
        return None


mt_newborn_credit = create_mt_newborn_credit_reform(None, None, bypass=True)

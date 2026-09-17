from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ma_commonwealth_credit() -> Reform:
    """Massachusetts Commonwealth Credit reform.

    Replaces the Massachusetts EITC match for tax units with EITC-qualifying
    children with a credit that:
    - Pays a maximum amount by number of qualifying children, plus an
      additional amount per child beyond the base child limit
    - Has no phase-in: the full credit is available at zero income
    - Phases out at a flat rate of the greater of earned income and AGI
      above a filing-status threshold
    - Excludes married-filing-separately filers unless
      separate_filer_eligible is true

    Tax units without qualifying children keep the existing EITC match.
    """

    class ma_commonwealth_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Massachusetts Commonwealth Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ma.commonwealth_credit
            children = tax_unit("eitc_child_count", period)
            base = p.max_amount.calc(min_(children, p.base_child_limit))
            additional = p.additional_child_amount * max_(
                children - p.base_child_limit, 0
            )
            max_credit = base + additional
            # The phase-out applies to the greater of earned income and
            # AGI, following the federal EITC (IRC Section 32(a)(2)(B)).
            earnings = tax_unit("eitc_earned_income", period)
            agi = tax_unit("adjusted_gross_income", period)
            income = max_(earnings, agi)
            filing_status = tax_unit("ma_filing_status", period)
            threshold = p.phase_out.threshold[filing_status]
            reduction = p.phase_out.rate * max_(income - threshold, 0)
            separate = filing_status == filing_status.possible_values.SEPARATE
            eligible = (children > 0) & (p.separate_filer_eligible | ~separate)
            return eligible * max_(max_credit - reduction, 0)

    class ma_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "MA EITC"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6"  # (h)
        )
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            # The Commonwealth Credit replaces the match for tax units with
            # EITC-qualifying children; childless units keep the match.
            has_children = tax_unit("eitc_child_count", period) > 0
            federal_eitc = tax_unit("eitc", period)
            rate = parameters(period).gov.states.ma.tax.income.credits.eitc.match
            return ~has_children * federal_eitc * rate

    def modify_parameters(parameters):
        parameters.gov.states.ma.tax.income.credits.refundable.update(
            start=instant("2027-01-01"),
            stop=instant("2037-12-31"),
            value=[
                "ma_eitc",
                "ma_commonwealth_credit",
                "ma_child_and_family_credit_or_dependent_care_credit",
                "ma_senior_circuit_breaker",
                "ma_covid_19_essential_employee_premium_pay_program",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.add_variable(ma_commonwealth_credit)
            self.update_variable(ma_eitc)
            self.modify_parameters(modify_parameters)

    return reform


def create_ma_commonwealth_credit_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ma_commonwealth_credit()

    p = parameters.gov.contrib.states.ma.commonwealth_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ma_commonwealth_credit()
    else:
        return None


ma_commonwealth_credit = create_ma_commonwealth_credit_reform(None, None, bypass=True)

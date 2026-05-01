from policyengine_us.model_api import *


def create_refundable_credit_conversion() -> Reform:
    """Refundable credit conversion reform.

    Repeals (configurable) the federal standard deduction, itemized
    deductions, above-the-line deductions, Head of Household filing
    status, CTC, CDCC, and EITC, and replaces them with a flat
    refundable credit composed of per-taxpayer, per-dependent,
    per-household, and wage-credit components.

    The repeals operate at the federal computation level: the underlying
    ``ctc``, ``eitc``, ``cdcc``, ``standard_deduction``,
    ``itemized_taxable_income_deductions``, ``above_the_line_deductions``,
    and ``head_of_household_eligible`` variables continue to compute their
    baseline values so that state programs that read them still work.
    Repeal is achieved by (a) overriding deduction/HoH variables to
    return 0 / False at the federal level, and (b) filtering the
    repealed credit names out of the federal refundable / non-refundable
    credit lists.
    """

    class flat_refundable_credit(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Refundable credit conversion flat credit"
        unit = USD
        documentation = (
            "Flat refundable credit replacing federal CTC, CDCC, EITC, "
            "standard deduction, itemized deductions, above-the-line "
            "deductions, and Head of Household filing status."
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.refundable_credit_conversion

            person = tax_unit.members
            is_filer = person("is_tax_unit_head_or_spouse", period)
            taxpayer_count = tax_unit.sum(is_filer)

            # 0 = EITC-qualifying children (default), 1 = CTC-qualifying
            # children, 2 = all claimed tax-unit dependents.
            definition = int(p.credit.dependent_definition)
            if definition == 1:
                dependent_count = tax_unit("ctc_qualifying_children", period)
            elif definition == 2:
                dependent_count = tax_unit("tax_unit_count_dependents", period)
            else:
                dependent_count = tax_unit("eitc_child_count", period)

            taxpayer_amount = taxpayer_count * p.credit.per_taxpayer
            dependent_amount = dependent_count * p.credit.per_dependent
            household_amount = p.credit.per_household

            earnings = person("earned_income", period)
            capped_earnings = min_(max_(earnings, 0), p.wage_credit.cap)
            person_wage_credit = capped_earnings * p.wage_credit.rate
            wage_credit_amount = tax_unit.sum(person_wage_credit)

            return (
                taxpayer_amount
                + dependent_amount
                + household_amount
                + wage_credit_amount
            )

    class standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Standard deduction"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/63#c"

        def formula(tax_unit, period, parameters):
            if parameters(
                period
            ).gov.contrib.refundable_credit_conversion.repeals.standard_deduction:
                return 0
            return add(
                tax_unit,
                period,
                [
                    "basic_standard_deduction",
                    "additional_standard_deduction",
                    "bonus_guaranteed_deduction",
                ],
            )

    class itemized_taxable_income_deductions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Itemized taxable income deductions"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            if parameters(
                period
            ).gov.contrib.refundable_credit_conversion.repeals.itemized:
                return 0
            total_deductions = tax_unit(
                "total_itemized_taxable_income_deductions", period
            )
            reduction = tax_unit("itemized_taxable_income_deductions_reduction", period)
            return max_(0, total_deductions - reduction)

    class above_the_line_deductions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Above-the-line deductions"
        unit = USD
        documentation = (
            "Deductions applied to reach adjusted gross income from gross income."
        )
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/62"

        def formula(tax_unit, period, parameters):
            if parameters(
                period
            ).gov.contrib.refundable_credit_conversion.repeals.above_the_line_deductions:
                return 0
            ald_variables = list(parameters(period).gov.irs.ald.deductions)
            return add(tax_unit, period, ald_variables)

    class head_of_household_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        definition_period = YEAR
        label = "Qualifies for head of household filing status"
        reference = "https://www.law.cornell.edu/uscode/text/26/2#b"

        def formula(tax_unit, period, parameters):
            if parameters(
                period
            ).gov.contrib.refundable_credit_conversion.repeals.head_of_household:
                return False
            married = tax_unit("tax_unit_married", period)
            person = tax_unit.members
            is_qualifying_child = person("is_qualifying_child_dependent", period)
            is_disabled_dependent = person(
                "is_permanently_and_totally_disabled", period
            ) & person("is_tax_unit_dependent", period)
            is_qualifying_relative = person("is_qualifying_relative_dependent", period)
            is_related = person("is_related_to_head_or_spouse", period)
            is_hoh_qualifying = (
                is_qualifying_child
                | is_disabled_dependent
                | (is_qualifying_relative & is_related)
            )
            has_qualifying_person = tax_unit.sum(is_hoh_qualifying) > 0
            return (
                has_qualifying_person
                & ~married
                & ~tax_unit("surviving_spouse_eligible", period)
            )

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            repeals = parameters(
                period
            ).gov.contrib.refundable_credit_conversion.repeals
            base = list(parameters(period).gov.irs.credits.refundable)
            CREDITS = []
            for c in base:
                if c == "eitc" and repeals.eitc:
                    continue
                if c == "refundable_ctc" and repeals.ctc:
                    continue
                if c == "cdcc" and repeals.cdcc:
                    continue
                CREDITS.append(c)
            CREDITS.append("flat_refundable_credit")
            return add(tax_unit, period, CREDITS)

    class income_tax_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal non-refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            repeals = parameters(
                period
            ).gov.contrib.refundable_credit_conversion.repeals
            base = list(parameters(period).gov.irs.credits.non_refundable)
            CREDITS = []
            for c in base:
                if c == "non_refundable_ctc" and repeals.ctc:
                    continue
                if c == "cdcc" and repeals.cdcc:
                    continue
                CREDITS.append(c)
            return add(tax_unit, period, CREDITS)

    class reform(Reform):
        def apply(self):
            self.update_variable(flat_refundable_credit)
            self.update_variable(standard_deduction)
            self.update_variable(itemized_taxable_income_deductions)
            self.update_variable(above_the_line_deductions)
            self.update_variable(head_of_household_eligible)
            self.update_variable(income_tax_refundable_credits)
            self.update_variable(income_tax_non_refundable_credits)

    return reform


def create_refundable_credit_conversion_reform(
    parameters, period, bypass: bool = False
):
    """Auto-application function for the refundable credit conversion reform."""
    if bypass:
        return create_refundable_credit_conversion()

    from policyengine_core.periods import period as period_

    p = parameters.gov.contrib.refundable_credit_conversion

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_refundable_credit_conversion()
    else:
        return None


refundable_credit_conversion = create_refundable_credit_conversion()

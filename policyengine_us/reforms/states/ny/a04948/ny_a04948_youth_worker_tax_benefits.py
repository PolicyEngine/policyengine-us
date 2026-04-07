from policyengine_us.model_api import *
from policyengine_core.periods import instant
from policyengine_core.periods import period as period_


def create_ny_a04948_youth_worker_tax_benefits() -> Reform:
    """
    NY Assembly Bill A04948 - Youth Worker Tax Benefits Act

    Creates three tax benefits for young workers in New York:
    1. Youth EITC: 130% of federal childless EITC for ages 17-24
    2. Youth Standard Deduction: $10,000 for single filers ages 18-24
    3. Student Loan Interest Deduction: Federal IRC 221 deduction for NY

    Reference: https://www.nysenate.gov/legislation/bills/2025/A4948
    Effective: 2026-2031 (sunset December 31, 2031)
    """

    class ny_a04948_youth_eitc_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Eligible for NY A04948 youth EITC"
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/bills/2025/A4948"
        defined_for = StateCode.NY

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.states.ny.a04948
            # Age requirements: 17-24
            # Note: max_age=24 is derived from IRC 32(c)(1)(A)(ii)(II) which sets
            # federal EITC minimum age at 25; thus max age for youth credit is 24.
            age = person("age", period)
            age_eligible = (age >= p.youth_eitc.min_age) & (age <= p.youth_eitc.max_age)
            # Cannot be claimed as dependent
            not_dependent = ~person("is_tax_unit_dependent", period)
            # Cannot be a parent (no qualifying children)
            tax_unit = person.tax_unit
            has_qualifying_children = tax_unit("eitc_child_count", period) > 0
            is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            not_parent = ~(is_head_or_spouse & has_qualifying_children)
            return age_eligible & not_dependent & not_parent

    class ny_a04948_youth_eitc_childless_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth EITC childless maximum amount"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            # Calculate federal childless EITC maximum (0 children)
            eitc = parameters(period).gov.irs.credits.eitc
            return eitc.max.calc(0)

    class ny_a04948_youth_eitc_phase_in_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth EITC phase-in rate"
        unit = "/1"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#b"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            eitc = parameters(period).gov.irs.credits.eitc
            return eitc.phase_in_rate.calc(0)

    class ny_a04948_youth_eitc_phased_in(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth EITC phased-in amount"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("ny_a04948_youth_eitc_childless_maximum", period)
            phase_in_rate = tax_unit("ny_a04948_youth_eitc_phase_in_rate", period)
            earnings = tax_unit("filer_adjusted_earnings", period)
            phased_in_amount = earnings * phase_in_rate
            return min_(maximum, phased_in_amount)

    class ny_a04948_youth_eitc_phase_out_start(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth EITC phase-out start"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#b"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            eitc = parameters(period).gov.irs.credits.eitc
            is_joint = tax_unit("tax_unit_is_joint", period)
            joint_bonus = eitc.phase_out.joint_bonus.calc(0)
            phase_out_start = eitc.phase_out.start.calc(0)
            return phase_out_start + is_joint * joint_bonus

    class ny_a04948_youth_eitc_phase_out_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth EITC phase-out rate"
        unit = "/1"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#b"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            eitc = parameters(period).gov.irs.credits.eitc
            return eitc.phase_out.rate.calc(0)

    class ny_a04948_youth_eitc_reduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth EITC reduction"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            earnings = tax_unit("filer_adjusted_earnings", period)
            agi = tax_unit("adjusted_gross_income", period)
            highest_income = max_(earnings, agi)
            phase_out_start = tax_unit("ny_a04948_youth_eitc_phase_out_start", period)
            phase_out_rate = tax_unit("ny_a04948_youth_eitc_phase_out_rate", period)
            phase_out_region = max_(0, highest_income - phase_out_start)
            return phase_out_rate * phase_out_region

    class ny_a04948_youth_eitc_federal_amount(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 federal childless EITC amount"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            # Calculate federal childless EITC (as if 0 qualifying children)
            maximum = tax_unit("ny_a04948_youth_eitc_childless_maximum", period)
            phased_in = tax_unit("ny_a04948_youth_eitc_phased_in", period)
            reduction = tax_unit("ny_a04948_youth_eitc_reduction", period)
            limitation = max_(0, maximum - reduction)
            return min_(phased_in, limitation)

    class ny_a04948_youth_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth earned income tax credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.nysenate.gov/legislation/bills/2025/A4948",
            "https://www.nysenate.gov/legislation/laws/TAX/606",
        )
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.a04948
            # Check if any member is eligible for the youth EITC
            person = tax_unit.members
            eligible = person("ny_a04948_youth_eitc_eligible", period)
            any_eligible = tax_unit.any(eligible)
            # Calculate 130% of federal childless EITC
            federal_childless_eitc = tax_unit(
                "ny_a04948_youth_eitc_federal_amount", period
            )
            youth_eitc_amount = federal_childless_eitc * p.youth_eitc.match
            return where(any_eligible, youth_eitc_amount, 0)

    class ny_a04948_youth_standard_deduction_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Eligible for NY A04948 youth enhanced standard deduction"
        definition_period = YEAR
        reference = (
            "https://www.nysenate.gov/legislation/bills/2025/A4948",
            "https://www.nysenate.gov/legislation/laws/TAX/614",
        )
        defined_for = StateCode.NY

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.states.ny.a04948
            youth_std_ded = p.youth_standard_deduction
            min_age = youth_std_ded.min_age
            max_age = youth_std_ded.max_age
            # Age requirements: 18-24
            age = person("age", period)
            age_eligible = (age >= min_age) & (age <= max_age)
            # Cannot be claimed as dependent
            not_dependent = ~person("is_tax_unit_dependent", period)
            # Filing status: must be Single
            filing_status = person.tax_unit("filing_status", period)
            is_single = filing_status == filing_status.possible_values.SINGLE
            # Must be the filer
            is_filer = person("is_tax_unit_head_or_spouse", period)
            # Amount must be > 0 (effective 2027+, amount is 0 in 2026)
            amount_available = youth_std_ded.amount > 0
            return (
                age_eligible & not_dependent & is_single & is_filer & amount_available
            )

    class ny_a04948_youth_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth enhanced standard deduction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.nysenate.gov/legislation/bills/2025/A4948",
            "https://www.nysenate.gov/legislation/laws/TAX/614",
        )
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.a04948
            # Check if filer is eligible
            person = tax_unit.members
            eligible = person("ny_a04948_youth_standard_deduction_eligible", period)
            filer_eligible = tax_unit.any(eligible)
            enhanced_deduction = p.youth_standard_deduction.amount
            return where(filer_eligible, enhanced_deduction, 0)

    class ny_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY standard deduction"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/laws/TAX/614"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            # Get standard NY standard deduction based on filing status
            dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
            p = parameters(period).gov.states.ny.tax.income.deductions.standard
            filing_status = tax_unit("filing_status", period)
            standard = where(
                dependent_elsewhere,
                p.dependent_elsewhere,
                p.amount[filing_status],
            )
            # Check for youth enhanced standard deduction
            youth_deduction = tax_unit("ny_a04948_youth_standard_deduction", period)
            # Use the greater of standard or youth enhanced deduction
            return max_(standard, youth_deduction)

    class ny_a04948_student_loan_interest_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 student loan interest deduction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.nysenate.gov/legislation/bills/2025/A4948",
            "https://www.nysenate.gov/legislation/laws/TAX/615",
            "https://www.law.cornell.edu/uscode/text/26/221",
        )
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            # Per Section 3 of A04948, the deduction is "to the extent and as
            # provided in section 221" of the IRC. The federal student_loan_interest_ald
            # already applies the $2,500 cap, income-based phase-out, MFS exclusion,
            # and dependent exclusion per IRC 221.
            return add(tax_unit, period, ["student_loan_interest_ald"])

    def modify_parameters(parameters):
        # Add youth EITC to NY refundable credits list
        refundable = parameters.gov.states.ny.tax.income.credits.refundable
        current_refundable = refundable(instant("2026-01-01"))
        if "ny_a04948_youth_eitc" not in current_refundable:
            new_refundable = list(current_refundable) + ["ny_a04948_youth_eitc"]
            refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2031-12-31"),
                value=new_refundable,
            )

        # Add student loan interest deduction to NY AGI subtractions
        subtractions = parameters.gov.states.ny.tax.income.agi.subtractions.sources
        current_subtractions = subtractions(instant("2026-01-01"))
        if "ny_a04948_student_loan_interest_deduction" not in current_subtractions:
            new_subtractions = list(current_subtractions) + [
                "ny_a04948_student_loan_interest_deduction"
            ]
            subtractions.update(
                start=instant("2026-01-01"),
                stop=instant("2031-12-31"),
                value=new_subtractions,
            )

        return parameters

    class reform(Reform):
        def apply(self):
            # Youth EITC variables
            self.update_variable(ny_a04948_youth_eitc_eligible)
            self.update_variable(ny_a04948_youth_eitc_childless_maximum)
            self.update_variable(ny_a04948_youth_eitc_phase_in_rate)
            self.update_variable(ny_a04948_youth_eitc_phased_in)
            self.update_variable(ny_a04948_youth_eitc_phase_out_start)
            self.update_variable(ny_a04948_youth_eitc_phase_out_rate)
            self.update_variable(ny_a04948_youth_eitc_reduction)
            self.update_variable(ny_a04948_youth_eitc_federal_amount)
            self.update_variable(ny_a04948_youth_eitc)
            # Youth standard deduction variables
            self.update_variable(ny_a04948_youth_standard_deduction_eligible)
            self.update_variable(ny_a04948_youth_standard_deduction)
            self.update_variable(ny_standard_deduction)
            # Student loan interest deduction
            self.update_variable(ny_a04948_student_loan_interest_deduction)
            # Modify parameters to add credits/deductions to lists
            self.modify_parameters(modify_parameters)

    return reform


def create_ny_a04948_youth_worker_tax_benefits_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ny_a04948_youth_worker_tax_benefits()

    p = parameters.gov.contrib.states.ny.a04948
    reform_active = False
    current_period = period_(period)
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ny_a04948_youth_worker_tax_benefits()
    return None


ny_a04948_youth_worker_tax_benefits = create_ny_a04948_youth_worker_tax_benefits_reform(
    None, None, bypass=True
)

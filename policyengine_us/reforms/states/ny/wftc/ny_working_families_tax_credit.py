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
            reduction = where(
                joint,
                p.reduction.married.calc(income),
                p.reduction.single.calc(income),
            )
            children = tax_unit("ny_wftc_eligible_children", period)
            max_amount = p.amount.max * children
            min_amount = p.amount.min * children
            return max_(min_amount, max_amount - reduction)

    class ny_wftc_eligible_child(Variable):
        value_type = bool
        entity = Person
        label = "New York Working Families Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY

        def formula(person, period, parameters):
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            p = parameters(period).gov.contrib.states.ny.wftc
            age_eligible = age <= p.child_age_threshold
            return is_dependent & age_eligible

    class ny_wftc_eligible_children(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York Working Families Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY

        adds = ["ny_wftc_eligible_child"]

    # Replicating the relevant parts of the EITC for for younger
    # and older dependents separately

    class is_younger_child_dependent(Variable):
        value_type = bool
        entity = Person
        label = "Is a younger child dependents"
        reference = "https://legislation.nysenate.gov/pdf/bills/2023/S277C"
        definition_period = YEAR

        def formula(person, period, parameters):
            is_dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            p = parameters(period).gov.contrib.states.ny.wftc
            age_eligible = age < p.child_age_threshold
            return is_dependent & age_eligible

    class eitc_younger_children_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "EITC-qualifying younger children"
        unit = USD
        documentation = "Number of children qualifying as children for the EITC, excluding dependents over 18."
        definition_period = YEAR

        adds = ["is_younger_child_dependent"]

    class eitc_younger_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum EITC for younger children"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD

        def formula(tax_unit, period, parameters):
            younger_child_count = tax_unit(
                "eitc_younger_children_count", period
            )
            older_child_count = tax_unit("eitc_older_children_count", period)
            child_count = older_child_count + younger_child_count
            eitc = parameters(period).gov.irs.credits.eitc
            # We will reduce the maximum credit amount by the amount for self
            # as it is attributed to the younger children EITC
            # We also need to reduce it by the amount attributed to the younger children
            base_credit = eitc.max.calc(child_count)
            amount_for_older = eitc.max.calc(older_child_count)
            return base_credit - amount_for_older

    class eitc_younger_phase_in_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-in rate"
        unit = "/1"
        documentation = "Rate at which the EITC phases in with income."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            child_count = tax_unit("eitc_younger_children_count", period)
            eitc = parameters(period).gov.irs.credits.eitc
            return eitc.phase_in_rate.calc(child_count)

    class eitc_younger_phased_in(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-in amount"
        unit = USD
        documentation = "EITC maximum amount, taking into account earnings."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("eitc_younger_maximum", period)
            phase_in_rate = tax_unit("eitc_younger_phase_in_rate", period)
            earnings = tax_unit("filer_adjusted_earnings", period)
            phased_in_amount = earnings * phase_in_rate
            return min_(maximum, phased_in_amount)

    class eitc_younger_phase_out_start(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-out start"
        unit = USD
        documentation = "Earnings above this level reduce EITC entitlement."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            count_children = tax_unit("eitc_younger_children_count", period)
            eitc = parameters(period).gov.irs.credits.eitc
            is_joint = tax_unit("tax_unit_is_joint", period)
            joint_bonus = eitc.phase_out.joint_bonus.calc(count_children)
            phase_out_start = eitc.phase_out.start.calc(count_children)
            return phase_out_start + is_joint * joint_bonus

    class eitc_younger_phase_out_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-out rate"
        unit = USD
        documentation = "Percentage of earnings above the phase-out threshold that reduce the EITC."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            eitc = parameters(period).gov.irs.credits.eitc
            num_children = tax_unit("eitc_younger_children_count", period)
            return eitc.phase_out.rate.calc(num_children)

    class eitc_younger_reduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC reduction"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a_2"

        def formula(tax_unit, period, parameters):
            earnings = tax_unit("filer_adjusted_earnings", period)
            agi = tax_unit("adjusted_gross_income", period)
            highest_income_variable = max_(earnings, agi)
            phase_out_start = tax_unit("eitc_younger_phase_out_start", period)
            phase_out_rate = tax_unit("eitc_younger_phase_out_rate", period)
            phase_out_region = max_(
                0, highest_income_variable - phase_out_start
            )
            return phase_out_rate * phase_out_region

    class eitc_younger_demographic_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Meets demographic eligibility for EITC"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

        def formula(tax_unit, period, parameters):
            return tax_unit("eitc_younger_children_count", period) > 0

    class younger_eitc_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for EITC"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

        def formula(tax_unit, period, parameters):
            eitc = parameters.gov.irs.credits.eitc(period)
            investment_income_eligible = tax_unit(
                "eitc_investment_income_eligible", period
            )
            demographic_eligible = tax_unit(
                "eitc_younger_demographic_eligible", period
            )
            # Define eligibility before considering separate filer limitation.
            eligible = demographic_eligible & investment_income_eligible
            # This parameter is true if separate filers are eligible.
            if eitc.eligibility.separate_filer:
                return eligible
            # If separate filers are not eligible, check if the filer is separate.
            filing_status = tax_unit("filing_status", period)
            separate = filing_status == filing_status.possible_values.SEPARATE
            return eligible & ~separate

    class younger_eitc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Federal earned income credit"
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD
        defined_for = "younger_eitc_eligible"

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("eitc_younger_maximum", period)
            phased_in = tax_unit("eitc_younger_phased_in", period)
            reduction = tax_unit("eitc_younger_reduction", period)
            limitation = max_(0, maximum - reduction)
            return min_(phased_in, limitation)

    class is_older_child_dependent(Variable):
        value_type = bool
        entity = Person
        label = "Is a older child dependents"
        reference = "https://legislation.nysenate.gov/pdf/bills/2023/S277C"
        definition_period = YEAR
        defined_for = StateCode.NY

        def formula(person, period, parameters):
            is_dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            p_irs = parameters(period).gov.irs.dependent.ineligible_age
            student = person("is_full_time_student", period)
            student_age_eligible = age < p_irs.student
            p_ref = parameters(period).gov.contrib.states.ny.wftc
            older_student_age_eligible = p_ref.child_age_threshold <= age
            age_eligible = student_age_eligible & older_student_age_eligible
            return is_dependent & student & age_eligible

    class eitc_older_children_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "EITC-qualifying younger children"
        unit = USD
        documentation = "Number of children qualifying as children for the EITC, excluding dependents over 18."
        definition_period = YEAR

        adds = ["is_older_child_dependent"]

    class eitc_older_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum EITC for younger children"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD

        def formula(tax_unit, period, parameters):
            child_count = tax_unit("eitc_older_children_count", period)
            eitc = parameters(period).gov.irs.credits.eitc
            # We will reduce the maximum credit amount by the amount for self
            # as it is attributed to the younger children EITC
            # We also need to reduce it by the amount attributed to the younger children
            return eitc.max.calc(child_count)

    class eitc_older_phase_in_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-in rate"
        unit = "/1"
        documentation = "Rate at which the EITC phases in with income."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            child_count = tax_unit("eitc_older_children_count", period)
            eitc = parameters(period).gov.irs.credits.eitc
            return eitc.phase_in_rate.calc(child_count)

    class eitc_older_phased_in(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-in amount"
        unit = USD
        documentation = "EITC maximum amount, taking into account earnings."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("eitc_older_maximum", period)
            phase_in_rate = tax_unit("eitc_older_phase_in_rate", period)
            earnings = tax_unit("filer_adjusted_earnings", period)
            phased_in_amount = earnings * phase_in_rate
            return min_(maximum, phased_in_amount)

    class eitc_older_phase_out_start(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-out start"
        unit = USD
        documentation = "Earnings above this level reduce EITC entitlement."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            count_children = tax_unit("eitc_older_children_count", period)
            eitc = parameters(period).gov.irs.credits.eitc
            is_joint = tax_unit("tax_unit_is_joint", period)
            joint_bonus = eitc.phase_out.joint_bonus.calc(count_children)
            phase_out_start = eitc.phase_out.start.calc(count_children)
            return phase_out_start + is_joint * joint_bonus

    class eitc_older_phase_out_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-out rate"
        unit = USD
        documentation = "Percentage of earnings above the phase-out threshold that reduce the EITC."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            eitc = parameters(period).gov.irs.credits.eitc
            num_children = tax_unit("eitc_older_children_count", period)
            return eitc.phase_out.rate.calc(num_children)

    class eitc_older_reduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC reduction"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a_2"

        def formula(tax_unit, period, parameters):
            earnings = tax_unit("filer_adjusted_earnings", period)
            agi = tax_unit("adjusted_gross_income", period)
            highest_income_variable = max_(earnings, agi)
            phase_out_start = tax_unit("eitc_older_phase_out_start", period)
            phase_out_rate = tax_unit("eitc_older_phase_out_rate", period)
            phase_out_region = max_(
                0, highest_income_variable - phase_out_start
            )
            return phase_out_rate * phase_out_region

    class eitc_older_demographic_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Meets demographic eligibility for EITC"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            has_child = tax_unit("eitc_older_children_count", period) > 0
            age = person("age", period)
            # Relative parameter reference break branching in some states that
            # modify EITC age limits.
            min_age_student = (
                parameters.gov.irs.credits.eitc.eligibility.age.min_student(
                    period
                )
            )
            max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(
                period
            )
            meets_age_requirements = (age >= min_age_student) & (
                age <= max_age
            )
            return has_child | tax_unit.any(meets_age_requirements)

    class older_eitc_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for EITC"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

        def formula(tax_unit, period, parameters):
            eitc = parameters.gov.irs.credits.eitc(period)
            investment_income_eligible = tax_unit(
                "eitc_investment_income_eligible", period
            )
            demographic_eligible = tax_unit(
                "eitc_older_demographic_eligible", period
            )
            # Define eligibility before considering separate filer limitation.
            eligible = demographic_eligible & investment_income_eligible
            # This parameter is true if separate filers are eligible.
            if eitc.eligibility.separate_filer:
                return eligible
            # If separate filers are not eligible, check if the filer is separate.
            filing_status = tax_unit("filing_status", period)
            separate = filing_status == filing_status.possible_values.SEPARATE
            return eligible & ~separate

    class older_eitc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Federal earned income credit"
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD
        defined_for = "older_eitc_eligible"

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("eitc_older_maximum", period)
            phased_in = tax_unit("eitc_older_phased_in", period)
            reduction = tax_unit("eitc_older_reduction", period)
            limitation = max_(0, maximum - reduction)
            return min_(phased_in, limitation)

    class ny_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York EITC"
        unit = USD
        definition_period = YEAR
        reference = "https://legislation.nysenate.gov/pdf/bills/2023/S277C"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            # The EITC match percentage is phased out for amounts attributed to
            # younger children
            federal_eitc = tax_unit("younger_eitc", period)
            p = parameters(period).gov.contrib.states.ny.wftc.eitc
            tentative_nys_eitc = federal_eitc * p.match
            # The EITC match amount remains flat attributed to older children
            older_child_eitc = tax_unit("older_eitc", period)
            p_ny = parameters(period).gov.states.ny.tax.income.credits
            older_ny_eitc = older_child_eitc * p_ny.eitc.match
            total_credit = tentative_nys_eitc + older_ny_eitc
            household_credit = tax_unit("ny_household_credit", period)
            return max_(0, total_credit - household_credit)

    class ny_exemptions_dependent(Variable):
        value_type = bool
        entity = Person
        label = "Dependent under the New York exemptions definition"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/laws/TAX/616"
        defined_for = StateCode.NY

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.states.ny.wftc.exemptions
            if p.in_effect:
                child_dependent = person("is_child_dependent", period)
                wftc_eligible_child = person("ny_wftc_eligible_child", period)
                return child_dependent & ~wftc_eligible_child
            return person("is_tax_unit_dependent", period)

    class ny_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY exemptions"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/laws/TAX/616"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):

            count_dependents = add(
                tax_unit, period, ["ny_exemptions_dependent"]
            )
            dependent_exemption = parameters(
                period
            ).gov.states.ny.tax.income.exemptions.dependent
            return dependent_exemption * count_dependents

    class ny_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ny.tax.income.credits
            older_credits = add(tax_unit, period, p.refundable)
            ny_wftc = tax_unit("ny_working_families_tax_credit", period)
            return older_credits + ny_wftc

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_working_families_tax_credit)
            self.update_variable(ny_wftc_eligible_child)
            self.update_variable(ny_wftc_eligible_children)
            self.update_variable(is_younger_child_dependent)
            self.update_variable(eitc_younger_children_count)
            self.update_variable(eitc_younger_maximum)
            self.update_variable(eitc_younger_phase_in_rate)
            self.update_variable(eitc_younger_phased_in)
            self.update_variable(eitc_younger_phase_out_start)
            self.update_variable(eitc_younger_phase_out_rate)
            self.update_variable(eitc_younger_reduction)
            self.update_variable(eitc_younger_demographic_eligible)
            self.update_variable(younger_eitc_eligible)
            self.update_variable(younger_eitc)
            self.update_variable(is_older_child_dependent)
            self.update_variable(eitc_older_children_count)
            self.update_variable(eitc_older_maximum)
            self.update_variable(eitc_older_phase_in_rate)
            self.update_variable(eitc_older_phased_in)
            self.update_variable(eitc_older_phase_out_start)
            self.update_variable(eitc_older_phase_out_rate)
            self.update_variable(eitc_older_reduction)
            self.update_variable(eitc_older_demographic_eligible)
            self.update_variable(older_eitc_eligible)
            self.update_variable(older_eitc)
            self.update_variable(ny_eitc)
            self.neutralize_variable("ny_ctc")
            self.update_variable(ny_exemptions_dependent)
            self.update_variable(ny_exemptions)
            self.update_variable(ny_refundable_credits)

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

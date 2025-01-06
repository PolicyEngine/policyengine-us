from policyengine_us.model_api import *


def create_expanded_ctc() -> Reform:
    class ctc_phase_in(Variable):
        value_type = float
        entity = TaxUnit
        label = "CTC phase-in"
        unit = USD
        definition_period = YEAR
        reference = "https://eppc.org/wp-content/uploads/2024/10/Tax-Teams-Comment-on-Working-Families.pdf"

        def formula(tax_unit, period, parameters):
            tax = tax_unit("income_tax_pre_ctc", period)
            total_benefits = add(
                tax_unit, period, ["snap", "free_school_meals", "tanf"]
            )
            max_benefit_amount = tax_unit("maximum_benefits", period)
            benefit_reduction = max_benefit_amount - total_benefits
            tax_with_benefit_reduction = tax + benefit_reduction
            p = parameters(period).gov.irs.credits.ctc.refundable.phase_in
            return max_(p.rate * tax_with_benefit_reduction, 0)

    class income_tax_non_refundable_credits_pre_ctc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal non-refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            non_ref_credits = parameters(period).gov.irs.credits.non_refundable
            credits = [
                credit
                for credit in non_ref_credits
                if credit not in ["non_refundable_ctc"]
            ]
            return add(tax_unit, period, credits)

    class income_tax_refundable_credits_pre_ctc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            ref_credits = parameters(period).gov.irs.credits.refundable
            credits = [
                credit
                for credit in ref_credits
                if credit not in ["refundable_ctc"]
            ]
            return add(tax_unit, period, credits)

    class income_tax_capped_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "non-refundable tax credits"
        unit = USD
        documentation = "Capped value of non-refundable tax credits"
        definition_period = YEAR
        adds = ["income_tax_non_refundable_credits_pre_ctc"]
        subtracts = ["income_tax_unavailable_non_refundable_credits"]

    class income_tax_unavailable_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "unavailable non-refundable tax credits"
        unit = USD
        documentation = "Total value of non-refundable tax credits that were not available to the filer due to having too low income tax."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            return -min_(
                tax_unit("income_tax_before_credits", period),
                tax_unit("income_tax_non_refundable_credits_pre_ctc", period),
            ) + tax_unit("income_tax_non_refundable_credits_pre_ctc", period)

    class income_tax_pre_ctc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "Federal income tax"
        documentation = "Total federal individual income tax liability."

        def formula(person, period, parameters):
            if parameters(
                period
            ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
                return 0
            else:
                added_components = add(
                    person, period, ["income_tax_before_refundable_credits"]
                )
                subtracted_components = add(
                    person, period, ["income_tax_refundable_credits_pre_ctc"]
                )
                return added_components - subtracted_components

    class income_tax(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "Federal income tax"
        documentation = "Total federal individual income tax liability."

        def formula(tax_unit, period, parameters):
            pre_ctc_tax = tax_unit("income_tax_pre_ctc", period)
            indiv_tax = tax_unit("income_tax_pre_ctc_indiv", period)
            filing_status = tax_unit("filing_status", period)
            is_joint = filing_status == filing_status.possible_values.JOINT
            non_ref_ctc = tax_unit("non_refundable_ctc", period)
            ref_ctc = tax_unit("refundable_ctc", period)
            base_tax = where(
                is_joint, min_(pre_ctc_tax, indiv_tax), pre_ctc_tax
            )
            return max_(base_tax - non_ref_ctc, 0) - ref_ctc

    class maximum_benefits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Maximum benefit amount to which the household is entitled"
        unit = USD
        # Currently only includes SNAP, free school meals, and TANF

        def formula(tax_unit, period, parameters):
            snap_max_allotment = tax_unit.spm_unit(
                "snap_max_allotment", period
            )
            # get maximum free school meal allotment
            state_group = tax_unit.spm_unit.household(
                "state_group_str", period
            )
            tier = "FREE"
            p_amount = parameters(period).gov.usda.school_meals.amount
            nslp_per_child = p_amount.nslp[state_group][tier]
            sbp_per_child = p_amount.sbp[state_group][tier]
            school_meals_daily_subsidy = nslp_per_child + sbp_per_child
            daily_paid_subsidy = tax_unit.spm_unit(
                "school_meal_paid_daily_subsidy", period
            )
            net_daily_subsidy_per_child = (
                school_meals_daily_subsidy - daily_paid_subsidy
            )
            p_school_meals = parameters(period).gov.usda.school_meals
            children = add(tax_unit, period, ["is_in_k12_school"])
            school_meal_max_value = (
                net_daily_subsidy_per_child
                * children
                * p_school_meals.school_days
            )
            # Get TANF grant standards (maximum amounts)
            max_federal_tanf = tax_unit.spm_unit("tanf_max_amount", period)
            max_ny_tanf = tax_unit.spm_unit("ny_tanf_grant_standard", period)
            tanf_dem_eligible = tax_unit.spm_unit(
                "is_demographic_tanf_eligible", period
            )
            max_dc_tanf = tax_unit.spm_unit("dc_tanf_grant_standard", period)
            max_co_tanf = tax_unit.spm_unit("co_tanf_grant_standard", period)
            max_tanf = (
                max_co_tanf + max_dc_tanf + max_federal_tanf + max_ny_tanf
            ) * tanf_dem_eligible
            return snap_max_allotment + school_meal_max_value + max_tanf

    # At the core of the reform, we want to coampre the tax liability of two individuals
    # filing as single people vs filing as a couple with the expanded CTC

    class basic_standard_deduction_indiv(Variable):
        value_type = float
        entity = Person
        label = "Basic standard deduction"
        definition_period = YEAR
        unit = USD
        reference = "https://www.law.cornell.edu/uscode/text/26/63#c_2"

        def formula(person, period, parameters):
            std = parameters(period).gov.irs.deductions.standard
            separate_filer_itemizes = person.tax_unit(
                "separate_filer_itemizes", period
            )
            dependent_elsewhere = person.tax_unit(
                "head_is_dependent_elsewhere", period
            )

            # Calculate secondary earner deduction using single filing status
            deduction_amount = std.amount["SINGLE"]

            standard_deduction_if_dependent = min_(
                deduction_amount,
                max_(
                    std.dependent.additional_earned_income
                    + person.tax_unit("tax_unit_earned_income", period),
                    std.dependent.amount,
                ),
            )

            return select(
                [
                    separate_filer_itemizes,
                    dependent_elsewhere,
                    True,
                ],
                [
                    0,
                    standard_deduction_if_dependent,
                    deduction_amount,
                ],
            )

    class taxable_income_deductions_person(Variable):
        value_type = float
        entity = Person
        label = "Taxable income deductions for each person"
        unit = USD
        definition_period = YEAR

        def formula(person, period, parameters):
            itemizes = person.tax_unit("tax_unit_itemizes", period)
            is_joint = person.tax_unit("tax_unit_is_joint", period)
            deductions_if_itemizing_amount = person.tax_unit(
                "taxable_income_deductions_if_itemizing", period
            )
            deductions_if_itemizing = where(
                is_joint,
                deductions_if_itemizing_amount / 2,
                deductions_if_itemizing_amount,
            )
            standard_deduction = person(
                "basic_standard_deduction_indiv", period
            )
            qbid = person("qualified_business_income_deduction_person", period)
            return where(
                itemizes, deductions_if_itemizing, standard_deduction + qbid
            )

    class taxable_income_indiv(Variable):
        value_type = float
        entity = Person
        label = "IRS taxable income for each person"
        unit = USD
        definition_period = YEAR

        def formula(person, period, parameters):
            agi = person("adjusted_gross_income_person", period)
            exemption_amount = person.tax_unit("exemptions", period)
            is_joint = person.tax_unit("tax_unit_is_joint", period)
            exemptions = where(
                is_joint, exemption_amount / 2, exemption_amount
            )
            deductions = person("taxable_income_deductions_person", period)
            return max_(0, agi - exemptions - deductions)

    class income_tax_main_rates_indiv(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Income tax main rates"
        reference = "https://www.law.cornell.edu/uscode/text/26/1"
        unit = USD

        def formula(tax_unit, period, parameters):
            # compute taxable income that is taxed at the main rates
            person = tax_unit.members
            full_taxable_income = person("taxable_income_indiv", period)
            cg_exclusion = (
                tax_unit("capital_gains_excluded_from_taxable_income", period)
                / 2
            )
            taxinc = max_(0, full_taxable_income - cg_exclusion)
            # compute tax using bracket rates and thresholds
            p = parameters(period).gov.irs.income
            bracket_tops = p.bracket.thresholds
            bracket_rates = p.bracket.rates

            tax = 0
            bracket_bottom = 0
            for i in range(1, len(list(bracket_rates.__iter__())) + 1):
                b = str(i)
                bracket_top = bracket_tops[b]["SINGLE"]
                tax += bracket_rates[b] * amount_between(
                    taxinc, bracket_bottom, bracket_top
                )
                bracket_bottom = bracket_top
            return tax_unit.sum(tax)

    class income_tax_before_credits_indiv(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "income tax before credits"
        unit = USD
        documentation = (
            "Total (regular + AMT) income tax liability before credits"
        )

        adds = [
            "income_tax_main_rates_indiv",
            "capital_gains_tax",
            "alternative_minimum_tax",
        ]

    class income_tax_capped_non_refundable_credits_indiv(Variable):
        value_type = float
        entity = TaxUnit
        label = "non-refundable tax credits"
        unit = USD
        documentation = "Capped value of non-refundable tax credits"
        definition_period = YEAR
        adds = ["income_tax_non_refundable_credits_pre_ctc"]
        subtracts = ["income_tax_unavailable_non_refundable_credits"]

    class income_tax_unavailable_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "unavailable non-refundable tax credits"
        unit = USD
        documentation = "Total value of non-refundable tax credits that were not available to the filer due to having too low income tax."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            return -min_(
                tax_unit("income_tax_before_credits", period),
                tax_unit("income_tax_non_refundable_credits_pre_ctc", period),
            ) + tax_unit("income_tax_non_refundable_credits_pre_ctc", period)

    class income_tax_before_refundable_credits_indiv(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "Federal income tax before refundable credits"
        documentation = "Income tax liability (including other taxes) after non-refundable credits are used, but before refundable credits are applied"

        def formula(tax_unit, period, parameters):
            if parameters(
                period
            ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
                return 0
            else:
                added_components = add(
                    tax_unit,
                    period,
                    [
                        "income_tax_before_credits_indiv",
                        "net_investment_income_tax",
                        "recapture_of_investment_credit",
                        "unreported_payroll_tax",
                        "qualified_retirement_penalty",
                    ],
                )
                subtracted_components = add(
                    tax_unit,
                    period,
                    ["income_tax_capped_non_refundable_credits_indiv"],
                )
                return added_components - subtracted_components

    class income_tax_pre_ctc_indiv(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "Federal income tax"
        documentation = "Total federal individual income tax liability."

        def formula(person, period, parameters):
            if parameters(
                period
            ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
                return 0
            else:
                added_components = add(
                    person,
                    period,
                    ["income_tax_before_refundable_credits_indiv"],
                )
                subtracted_components = add(
                    person, period, ["income_tax_refundable_credits_pre_ctc"]
                )
                return added_components - subtracted_components

    class reform(Reform):
        def apply(self):
            self.neutralize_variable("eitc")
            self.neutralize_variable("head_of_household_eligible")
            self.neutralize_variable("cdcc")
            self.update_variable(ctc_phase_in)
            self.update_variable(income_tax)
            self.update_variable(income_tax_pre_ctc)
            self.update_variable(income_tax_unavailable_non_refundable_credits)
            self.update_variable(income_tax_refundable_credits_pre_ctc)
            self.update_variable(income_tax_non_refundable_credits_pre_ctc)
            self.update_variable(income_tax_capped_non_refundable_credits)
            self.update_variable(maximum_benefits)
            self.update_variable(income_tax_before_refundable_credits_indiv)
            self.update_variable(income_tax_before_credits_indiv)
            self.update_variable(
                income_tax_capped_non_refundable_credits_indiv
            )
            self.update_variable(income_tax_main_rates_indiv)
            self.update_variable(taxable_income_indiv)
            self.update_variable(taxable_income_deductions_person)
            self.update_variable(basic_standard_deduction_indiv)
            self.update_variable(income_tax_pre_ctc_indiv)

    return reform


def create_expanded_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_expanded_ctc()

    p = parameters(period).gov.contrib.ctc.eppc.expanded_ctc

    if p.in_effect:
        return create_expanded_ctc()
    else:
        return None


expanded_ctc = create_expanded_ctc_reform(None, None, bypass=True)

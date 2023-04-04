from policyengine_us.model_api import *


class mn_elderly_disabled_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota elderly/disabled subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        mn_itax = parameters(period).gov.states.mn.tax.income
        p = mn_itax.subtractions.elderly_disabled
        filing_status = tax_unit("filing_status", period)
        # calculate the subtraction amount
        # ... determine starting amount
        person = tax_unit.members
        is_elderly = person("age", period) >= p.minimum_age
        is_head = person("is_tax_unit_head", period)
        elderly_head = is_head & is_elderly
        is_spouse = person("is_tax_unit_spouse", period)
        elderly_spouse = is_spouse & is_elderly
        # ... determine disability eligiblity
        is_disabled = person("is_permanently_and_totally_disabled", period)
        disabled_head = is_head & is_disabled
        disabled_spouse = is_spouse & is_disabled
        # ... determine start amount
        start_amount = where(
            tax_unit.any(elderly_head | elderly_spouse),
            p.base_amount[filing_unit],
            0,  # because federally-taxable disability income
            # included in federal Form 1040, line 1z, is unknown
        )
        # ... determine disability income as on federal Schedule R
        is_dependent = person("is_tax_unit_dependent", period)
        dinc_person = person("total_disability_payments", period)
        disinc_person = dinc_person * ~is_dependent * ~is_elderly
        disability_income = add(tax_unit, period, ["disinc_person"])
        # ... determine untaxed social security benefits
        untaxed_social_security = add(
            tax_unit, period, ["social_security"]
        ) - add(tax_unit, period, ["taxable_social_security"])
        # ... determine total disability and social security benefits
        benefits = disability_income + untaxed_social_security
        # ... subtract benefits from start_amount
        amount = max_(0, start_amount - benefits)
        # ... determine AGI eligibility for subtraction
        agi = tax_unit("adjusted_gross_income", period)
        agi += tax_unit("c05700", period)  # lump-sum Form 4972 distributions
        agi_limit = p.agi_base_limit[filing_status]
        joint = filing_status == filing_stauts.possible_values.JOINT
        head_eligible = tax_unit.any(elderly_head | disabled_head)
        spouse_eligible = tax_unit.any(elderly_spouse | disabled_spouse)
        joint_with_two_eligibles = joint & head_eligible & spouse_eligible
        agi_limit += p.agi_extra_limit * joint_with_two_eligibles
        net_agi = max_(0, agi - agi_limit)
        fraction_of_net_agi = p.agi_fraction * net_agi
        # ... subtract fracton_of_net_agi from amount to get final amount
        final_amount = max_(0, amount - fraction_of_net_agi)
        return where(head_eligible | spouse_eligible, final_amount, 0)

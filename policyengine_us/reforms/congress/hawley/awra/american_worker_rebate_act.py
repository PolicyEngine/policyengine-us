from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_american_worker_rebate_act() -> Reform:
    class american_worker_tax_rebate_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "American Worker Tax Rebate eligible"
        documentation = (
            "Eligible for tax rebate under the American Worker Rebate Act."
        )
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            immigration_status = person("immigration_status", period)
            immigration_status_str = immigration_status.decode_to_str()
            eligible_immigration_statuses = parameters(
                period
            ).gov.contrib.congress.hawley.awra.eligible_immigration_statuses
            is_eligible_immigration_status = np.isin(
                immigration_status_str, eligible_immigration_statuses
            )
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            meets_ctc_identification_requirements = person(
                "meets_ctc_identification_requirements", period
            )
            ineligible_head_or_spouse = head_or_spouse & ~(
                is_eligible_immigration_status
                & meets_ctc_identification_requirements
            )
            return ~tax_unit.any(ineligible_head_or_spouse)

    class american_worker_tax_rebate_base_amount(Variable):
        value_type = float
        entity = TaxUnit
        label = "American Worker Tax Rebate base amount"
        unit = USD
        documentation = (
            "Base amount of tax rebate under the American Worker Rebate Act."
        )
        definition_period = YEAR
        defined_for = "american_worker_tax_rebate_eligible"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.congress.hawley.awra
            multiplier = where(
                tax_unit("tax_unit_is_joint", period),
                p.amount.joint_multiplier,
                1,
            )
            return multiplier * p.amount.non_joint

    class american_worker_tax_rebate(Variable):
        value_type = float
        entity = TaxUnit
        label = "American Worker Tax Rebate"
        unit = USD
        documentation = (
            "Tax rebate amount under the American Worker Rebate Act."
        )
        definition_period = YEAR
        defined_for = "american_worker_tax_rebate_eligible"

        def formula(tax_unit, period, parameters):
            total_amount = add(
                tax_unit,
                period,
                [
                    "american_worker_tax_rebate_base_amount",
                    "american_worker_tax_rebate_child_amount",
                ],
            )
            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            p = parameters(period).gov.contrib.congress.hawley.awra
            agi_excess = max_(agi - p.phase_out.start[filing_status], 0)
            phase_out = agi_excess * p.phase_out.rate
            return max_(total_amount - phase_out, 0)

    class american_worker_tax_rebate_child_amount(Variable):
        value_type = float
        entity = Person
        label = "American Worker Tax Rebate child amount"
        unit = USD
        documentation = "The tax rebate amount for children, under the American Worker Rebate Act."
        definition_period = YEAR
        defined_for = "ctc_qualifying_child"

        adds = ["gov.contrib.congress.hawley.awra.amount.non_joint"]

    def modify_parameters(parameters):
        parameters.gov.irs.credits.refundable.update(
            start=instant("2024-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "eitc",
                "refundable_american_opportunity_credit",
                "refundable_ctc",
                "recovery_rebate_credit",
                "refundable_payroll_tax_credit",
                "american_worker_tax_rebate",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(american_worker_tax_rebate)
            self.update_variable(american_worker_tax_rebate_base_amount)
            self.update_variable(american_worker_tax_rebate_child_amount)
            self.update_variable(american_worker_tax_rebate_eligible)
            self.modify_parameters(modify_parameters)

    return reform


def create_american_worker_rebate_act_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_american_worker_rebate_act()

    p = parameters.gov.contrib.congress.hawley.awra

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_american_worker_rebate_act()
    else:
        return None


american_worker_rebate_act = create_american_worker_rebate_act_reform(
    None, None, bypass=True
)

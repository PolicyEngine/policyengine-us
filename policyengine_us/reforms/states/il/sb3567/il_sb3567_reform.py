from policyengine_core.periods import instant, period as period_
from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


def create_il_sb3567() -> Reform:
    class il_ctc_potential(Variable):
        value_type = float
        entity = TaxUnit
        label = "Illinois Child Tax Credit before non-refundable cap"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://ilga.gov/Legislation/BillStatus/FullText?DocNum=3567&DocTypeID=SB&GAID=18&LegId=166617&Print=1&SessionID=114",
            "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=003500050K244",
        )
        defined_for = StateCode.IL

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.il.tax.income.credits
            ctc = p.ctc
            person = tax_unit.members
            age = person("age", period)
            age_eligible_child = age < ctc.age_limit
            federal_ctc_eligible_child = person("ctc_qualifying_child", period)
            eligible_child = age_eligible_child & federal_ctc_eligible_child
            eligible_child_present = tax_unit.any(eligible_child)

            actual_credit = tax_unit("il_eitc", period) * ctc.rate

            # SB3567 keys the maximum credit amount to the dependent count.
            # The bill cites IRC § 152, but here we use the tax unit's child
            # dependent count, capped at 3 to match the federal EITC schedule.
            dependent_count = min_(tax_unit("tax_unit_child_dependents", period), 3)
            federal_eitc = parameters(period).gov.irs.credits.eitc
            federal_maximum = federal_eitc.max.calc(dependent_count)
            phase_in_rate = federal_eitc.phase_in_rate.calc(dependent_count)

            # The bill's "income threshold to qualify for the maximum federal
            # EITC" is the end of the phase-in range (start of the plateau).
            max_federal_eitc_threshold = federal_maximum / phase_in_rate
            max_credit = federal_maximum * p.eitc.match * ctc.rate

            agi = tax_unit("adjusted_gross_income", period)
            return eligible_child_present * where(
                agi <= max_federal_eitc_threshold,
                max_credit,
                actual_credit,
            )

    class il_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Illinois Child Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://ilga.gov/Legislation/BillStatus/FullText?DocNum=3567&DocTypeID=SB&GAID=18&LegId=166617&Print=1&SessionID=114",
            "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=003500050K244",
        )
        defined_for = StateCode.IL

        def formula(tax_unit, period, parameters):
            ordered_credits = parameters(
                period
            ).gov.states.il.tax.income.credits.non_refundable
            return applied_state_non_refundable_credit(
                tax_unit,
                period,
                ordered_credits,
                "il_income_tax_before_non_refundable_credits",
                "il_ctc",
                "il_ctc_potential",
            )

    def modify_parameters(parameters: ParameterNode) -> ParameterNode:
        refundable = parameters.gov.states.il.tax.income.credits.refundable
        refundable_credits = list(refundable(instant("2025-01-01")))
        if "il_ctc" in refundable_credits:
            refundable_credits.remove("il_ctc")
        refundable.update(
            start=instant("2025-01-01"),
            stop=instant("2100-12-31"),
            value=refundable_credits,
        )

        non_refundable = parameters.gov.states.il.tax.income.credits.non_refundable
        non_refundable_credits = list(non_refundable(instant("2025-01-01")))
        if "il_ctc" not in non_refundable_credits:
            non_refundable_credits.append("il_ctc")
        non_refundable.update(
            start=instant("2025-01-01"),
            stop=instant("2100-12-31"),
            value=non_refundable_credits,
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.add_variable(il_ctc_potential)
            self.update_variable(il_ctc)
            self.modify_parameters(modify_parameters)

    return reform


def create_il_sb3567_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_il_sb3567()

    p = parameters.gov.contrib.states.il.sb3567

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_il_sb3567()
    else:
        return None


il_sb3567 = create_il_sb3567_reform(None, None, bypass=True)

from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_pa_ctc_match() -> Reform:
    class pa_ctc_match(Variable):
        value_type = float
        entity = TaxUnit
        label = "Pennsylvania CTC match for young children"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.PA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.pa.ctc.ctc_match

            # Get person-level data
            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            # Child must have valid SSN to qualify for federal CTC
            has_valid_ssn = person(
                "meets_ctc_child_identification_requirements", period
            )
            ctc_eligible_child = is_dependent & has_valid_ssn
            young_child = ctc_eligible_child & (age < p.age_limit)

            # Get federal CTC maximum per child (person-level variable)
            federal_ctc_max_per_child = person(
                "ctc_child_individual_maximum", period
            )

            # Calculate the portion of federal CTC attributable to young children
            # Only include children with valid SSN who qualify for federal CTC
            young_child_max = tax_unit.sum(
                where(young_child, federal_ctc_max_per_child, 0)
            )
            total_child_max = tax_unit.sum(
                where(ctc_eligible_child, federal_ctc_max_per_child, 0)
            )

            # Calculate the ACTUAL federal CTC benefit received
            # This is the refundable portion (always received) plus
            # the nonrefundable portion (only to extent of tax liability)
            refundable_ctc = tax_unit("refundable_ctc", period)
            non_refundable_ctc = tax_unit("non_refundable_ctc", period)
            tax_liability = tax_unit("ctc_limiting_tax_liability", period)
            usable_non_refundable = min_(non_refundable_ctc, tax_liability)
            actual_federal_ctc = refundable_ctc + usable_non_refundable

            # Calculate the young child portion of the actual CTC
            # (proportional to their share of the maximum)
            young_child_share = where(
                total_child_max > 0, young_child_max / total_child_max, 0
            )
            young_child_ctc = actual_federal_ctc * young_child_share

            # Apply match rate
            return young_child_ctc * p.match

    def modify_parameters(parameters):
        # Add pa_ctc_match to refundable credits list
        refundable = parameters.gov.states.pa.tax.income.credits.refundable
        current_refundable = refundable(instant("2026-01-01"))
        if "pa_ctc_match" not in current_refundable:
            new_refundable = list(current_refundable) + ["pa_ctc_match"]
            refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=new_refundable,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(pa_ctc_match)
            self.modify_parameters(modify_parameters)

    return reform


def create_pa_ctc_match_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_pa_ctc_match()

    p = parameters.gov.contrib.states.pa.ctc.ctc_match

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_pa_ctc_match()
    else:
        return None


pa_ctc_match = create_pa_ctc_match_reform(None, None, bypass=True)

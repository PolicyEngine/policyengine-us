from policyengine_us.model_api import *


def create_eitc_winship_reform(parameters, period, bypass=False):
    if (
        not bypass
        and not parameters(period).gov.contrib.individual_eitc.enabled
    ):
        return None

    # Compute EITC under filer_adj_earnings = filer head adj earnings
    # Then compute EITC under filer_adj_earnings = filer spouse adj earnings
    # Then set EITC = sum of the two

    class original_eitc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Original EITC"
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD
        defined_for = "eitc_eligible"

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("eitc_maximum", period)
            phased_in = tax_unit("eitc_phased_in", period)
            reduction = tax_unit("eitc_reduction", period)
            limitation = max_(0, maximum - reduction)
            return min_(phased_in, limitation)

    class eitc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "EITC"
        unit = USD
        defined_for = "eitc_eligible"

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            simulation = tax_unit.simulation
            agi = tax_unit("adjusted_gross_income", period)
            adj_earnings = person("adjusted_earnings", period)
            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)

            filer_earned_head_only = tax_unit.sum(adj_earnings * is_head)
            filer_earned_spouse_only = tax_unit.sum(adj_earnings * is_spouse)

            head_only_branch = simulation.get_branch("head_only")
            head_only_branch.set_input(
                "filer_adjusted_earnings", period, filer_earned_head_only
            )
            # Phase out with respect to individual earnings instead of AGI
            head_only_branch.set_input(
                "adjusted_gross_income", period, filer_earned_head_only
            )
            head_eitc = head_only_branch.calculate("original_eitc", period)

            spouse_only_branch = simulation.get_branch("spouse_only")
            spouse_only_branch.set_input(
                "filer_adjusted_earnings", period, filer_earned_spouse_only
            )
            spouse_only_branch.set_input(
                "adjusted_gross_income", period, filer_earned_spouse_only
            )
            spouse_eitc = spouse_only_branch.calculate("original_eitc", period)

            agi_limit = parameters(
                period
            ).gov.contrib.individual_eitc.agi_eitc_limit

            return (agi < agi_limit) * (head_eitc + spouse_eitc)

    class winship_eitc_reform(Reform):
        def apply(self):
            self.update_variable(original_eitc)
            self.update_variable(eitc)

    return winship_eitc_reform


winship_reform = create_eitc_winship_reform(None, None, bypass=True)

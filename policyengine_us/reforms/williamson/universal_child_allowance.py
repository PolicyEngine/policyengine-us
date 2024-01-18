from policyengine_us.model_api import *


def create_universal_child_allowance() -> Reform:
    class universal_child_allowance(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "Marrianne Williamson's Universal Child Allowance"
        reference = "https://marianne2024.com/issues/universal-basic-income/"

        def formula_2022(tax_unit, period, parameters):
            # Filer credit.
            # Define eligibility based on age.
            children = tax_unit("tax_unit_children", period)
            p = parameters(
                period
            ).gov.contrib.congress.williamson.child_allowance


            return children * p.amount

    class eitc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Federal earned income credit"
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD
        defined_for = "eitc_eligible"

        def formula(tax_unit, period, parameters):
            return 0

    class ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Child Tax Credit"
        unit = USD
        documentation = "Total value of the non-refundable and refundable portions of the Child Tax Credit."
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/24#a"

        def formula(tax_unit, period, parameters):
            return 0

    class reform(Reform):
        def apply(self):
            self.update_variable(universal_child_allowance)
            self.update_variable(eitc)
            self.update_variable(ctc)

    return reform


def create_universal_child_allowance_reform(
     parameters, period, bypass: bool = False,
):
    if bypass:
        return create_universal_child_allowance()

    p = parameters(
        period
    ).gov.contrib.congress.tlaib.end_child_poverty_act.filer_credit


    if p.amount > 0:
        return create_universal_child_allowance()
    else:
        return None


universal_child_allowance = create_universal_child_allowance_reform( None, None, bypass=True)

from policyengine_us.model_api import *


class la_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana qualified dependents exemption"
    reference = [
        "https://dam.ldr.la.gov/taxforms/6935(11_02)F.pdf#page=1",
        "https://dam.ldr.la.gov/taxforms/IT540iWEB(2022)D1.pdf#page=2",
        "https://dam.ldr.la.gov/taxforms/IT540i(2021)%20Instructions.pdf#page=3",
        "https://dam.ldr.la.gov/taxforms/IT540i%20WEB%20(2024)D18%20INSTRUCTIONS.pdf#page=3",
    ]
    # Even though the tax computation worksheet refers "dependent exemption" as credits, the instructions for
    # preparing tax form line 6a-6b specifies it as exemption.
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        # Line 6C counts "the dependents claimed on your federal return". Under
        # IRC 152(b)(1) a federal return on which the filer (or, if joint,
        # either spouse) can be claimed has none. The filer's own exemption
        # (Line 6A) stays "even if someone else claimed you".
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents = where(
            filer_is_dependent, 0, tax_unit("tax_unit_dependents", period)
        )
        p = parameters(period).gov.states.la.tax.income.exemptions
        return dependents * p.dependent

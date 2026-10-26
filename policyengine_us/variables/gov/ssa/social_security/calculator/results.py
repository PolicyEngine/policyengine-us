"""Opt-in results; the public benefit source selector can consume these once."""

from policyengine_us.model_api import *
from policyengine_us.tools.social_security.engine import calculator_output


class ss_calculated_retirement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security retirement"
    documentation = (
        "Gross annual retirement checks on the selected supplied own record."
    )
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "retirement")


class ss_calculated_survivors(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security survivors"
    documentation = (
        "Gross annual survivor checks on the selected restricted survivor record."
    )
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "survivors")


class ss_calculated_annual_entitlement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security annual entitlement"
    documentation = (
        "Sum of payable entitlement months in the calendar year, before Medicare "
        "deductions, including partial earnings-test benefits awaiting settlement."
    )
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "annual_entitlement")


class ss_calculated_annual_payment(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security annual payment"
    documentation = (
        "Sum of gross checks paid in the calendar year, including explicitly "
        "dated settlements. Ordinary checks follow entitlement by one month; "
        "whole-month earnings-test withholding defers partial benefits until "
        "closed-year reporting unless immediate payment is explicitly requested."
    )
    reference = (
        "https://www.ssa.gov/OP_Home/handbook/handbook.18/handbook-1806.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0302501110",
    )

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "annual_payment")


class ss_calculated_earnings_test_reduction(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security earnings test reduction"
    documentation = (
        "Annual earnings-test reduction capped at affected entitlement benefits."
    )
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "earnings_test_reduction")


class ss_calculated_deferred_earnings_test_payment(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security deferred earnings test payment"
    documentation = (
        "Partial benefit withheld from this earnings year's ordinary checks, "
        "payable after closed-year earnings reporting. No settlement date is assumed."
    )
    reference = (
        "https://www.ssa.gov/OP_Home/handbook/handbook.18/handbook-1806.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0302501110",
    )

    def formula(person, period, parameters):
        return calculator_output(
            person, period, parameters, "deferred_earnings_test_payment"
        )


class ss_calculated_benefit(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Calculated Social Security benefit"
    documentation = (
        "Payable gross benefit for this entitlement month, including any partial "
        "earnings-test benefit whose payment is deferred until settlement."
    )
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "benefit")


class ss_calculated_payment(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Calculated Social Security payment"
    documentation = (
        "Gross benefit checks in this month, including explicitly dated settlements. "
        "The preceding entitlement month's partial earnings-test benefit is "
        "withheld pending closed-year reporting unless immediate payment is requested."
    )
    reference = (
        "https://www.ssa.gov/OP_Home/handbook/handbook.18/handbook-1806.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0302501110",
    )

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "payment")


class ss_calculated_eligibility_pia(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Calculated Social Security eligibility pia"
    documentation = "Reformed monthly eligibility PIA underlying this entitlement month, before COLAs."
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "eligibility_pia")


class ss_calculated_pia_lower(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security pia lower"
    documentation = (
        "Lower endpoint of the survivor source eligibility-PIA rounding interval."
    )
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "pia_lower")


class ss_calculated_pia_upper(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security pia upper"
    documentation = "Exclusive upper endpoint of the survivor source eligibility-PIA rounding interval."
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "pia_upper")


class ss_calculated_aime_lower(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security aime lower"
    documentation = "Lower-endpoint AIME inferred from the supplied baseline PIA when a PIA reform requires it."
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "aime_lower")


class ss_calculated_aime_upper(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Calculated Social Security aime upper"
    documentation = "Exclusive upper endpoint of inferred AIME including source payment-rounding uncertainty."
    reference = "https://www.ssa.gov/oact/cola/colaapplic.html"

    def formula(person, period, parameters):
        return calculator_output(person, period, parameters, "aime_upper")

"""Explicit source inputs for the opt-in supplied-record calculator.

The selector, rather than amount positivity, determines the source. These are
separate from reported public benefit inputs and carry no automatic uprating.
"""

from policyengine_us.model_api import *


class ss_calculator_source(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = "off"
    label = "Social Security calculator source"
    documentation = "Explicit source: off, aime, pia or survivor."


class ss_calculator_worker_id(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator worker id"
    documentation = (
        "Underlying worker record identifier; each own record has a distinct ID."
    )


class ss_calculator_birth_date(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator birth date"
    documentation = "Recipient exact birth date, YYYY-MM-DD; also the worker date for own retirement."


class ss_calculator_entitlement_month(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator entitlement month"
    documentation = (
        "First benefit entitlement month, YYYY-MM; the check follows one month later."
    )


class ss_calculator_eligibility_year(Variable):
    value_type = int
    entity = Person
    definition_period = ETERNITY
    default_value = 0
    label = "Social Security calculator eligibility year"
    documentation = "Own-retirement initial age-62 eligibility year."


class ss_calculator_supplied_aime(Variable):
    # Preserve fractional input so the service can reject it, rather than
    # Core silently truncating it while coercing an integer-valued variable.
    value_type = float
    entity = Person
    definition_period = ETERNITY
    default_value = -1
    label = "Social Security calculator supplied aime"
    documentation = "Unreformed eligibility AIME, whole monthly dollars; zero is a supplied zero and -1 means missing."
    unit = USD


class ss_calculator_supplied_pia(Variable):
    value_type = float
    entity = Person
    definition_period = ETERNITY
    default_value = -1
    label = "Social Security calculator supplied pia"
    documentation = "Unreformed eligibility PIA, monthly dollars valued before subsequent COLAs; -1 means missing."
    unit = USD


class ss_calculator_source_basis(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = "unreformed_eligibility"
    label = "Social Security calculator source basis"
    documentation = "Source valuation basis; only unreformed_eligibility is supported."


class ss_calculator_claiming_factor(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator claiming factor"
    documentation = "Optional exact claiming adjustment as a decimal string; empty computes exact months."


class ss_calculator_insured(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator insured"
    documentation = "Assert insured status for the selected underlying worker record."


class ss_calculator_no_special_monthly_test(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator no special monthly test"
    documentation = (
        "Assert the first-year monthly/service earnings test does not trigger."
    )


class ss_calculator_no_prior_withholding_adjustment(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator no prior withholding adjustment"
    documentation = (
        "Assert no actuarial adjustment for earlier withheld months is needed."
    )


class ss_calculator_earnings_test_no_trigger(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator earnings test no trigger"
    documentation = "Assert earnings do not trigger the annual earnings test in the requested years."


class ss_calculator_worker_birth_year(Variable):
    value_type = int
    entity = Person
    definition_period = ETERNITY
    default_value = 0
    label = "Social Security calculator worker birth year"
    documentation = "Deceased worker birth year for the restricted survivor route."


class ss_calculator_worker_birth_date(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator worker birth date"
    documentation = "Optional deceased worker exact birth date, YYYY-MM-DD."


class ss_calculator_death_year(Variable):
    value_type = int
    entity = Person
    definition_period = ETERNITY
    default_value = 0
    label = "Social Security calculator death year"
    documentation = "Deceased worker death year."


class ss_calculator_death_date(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator death date"
    documentation = "Optional exact worker death date, YYYY-MM-DD."


class ss_calculator_authoritative_year(Variable):
    value_type = int
    entity = Person
    definition_period = ETERNITY
    default_value = 0
    label = "Social Security calculator authoritative year"
    documentation = (
        "Optional authoritative survivor computation benchmark; zero means derive."
    )


class ss_calculator_basis_provenance(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator basis provenance"
    documentation = (
        "Provenance identifying the supplied or derived survivor computation basis."
    )


class ss_calculator_no_prior_disability(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator no prior disability"
    documentation = "Assert the deceased had no prior disability benefit computation."


class ss_calculator_ordinary_non_windex(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator ordinary non windex"
    documentation = "Assert an ordinary non-WINDEX survivor computation."


class ss_calculator_year_only_not_january_1(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator year only not january 1"
    documentation = "Assert the year-only deceased birth basis assumes a birthday other than January 1."


class ss_calculator_same_year_death_before_62(Variable):
    value_type = int
    entity = Person
    definition_period = ETERNITY
    default_value = -1
    label = "Social Security calculator same year death before 62"
    documentation = "Same-year death/age62 assertion: 1 before62, 0 after62, -1 requires exact dates."


class ss_calculator_monthly_amount(Variable):
    value_type = float
    entity = Person
    definition_period = ETERNITY
    default_value = -1
    label = "Social Security calculator monthly amount"
    documentation = "Supplied unreformed gross survivor monthly payment at the valuation month; -1 means missing."
    unit = USD


class ss_calculator_valuation_month(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator valuation month"
    documentation = (
        "Survivor source check month, YYYY-MM, including its baseline COLAs."
    )


class ss_calculator_composite_ratio(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator composite ratio"
    documentation = "Exact positive survivor-to-worker PIA ratio as a decimal string, including all reductions/credits."


class ss_calculator_ratio_description(Variable):
    value_type = str
    entity = Person
    definition_period = ETERNITY
    default_value = ""
    label = "Social Security calculator ratio description"
    documentation = (
        "Description of what the supplied survivor composite ratio includes."
    )


class ss_calculator_nonbinding_rib_lim(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator nonbinding rib lim"
    documentation = "Assert the survivor RIB-LIM is nonbinding."


class ss_calculator_nonbinding_family_maximum(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator nonbinding family maximum"
    documentation = "Assert the family maximum is nonbinding."


class ss_calculator_no_dual_entitlement(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator no dual entitlement"
    documentation = "Assert the survivor has no dual entitlement."


class ss_calculator_no_earnings_test_at_valuation(Variable):
    value_type = bool
    entity = Person
    definition_period = ETERNITY
    default_value = False
    label = "Social Security calculator no earnings test at valuation"
    documentation = (
        "Assert the supplied survivor valuation has no earnings-test withholding."
    )


class ss_calculator_annual_earnings(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    default_value = -1
    label = "Social Security calculator annual earnings"
    documentation = "Annual earnings subject to the annual test; -1 means missing."
    unit = USD


class ss_calculator_pre_fra_earnings(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    default_value = -1
    label = "Social Security calculator pre fra earnings"
    documentation = "Earnings only before the retirement FRA month; -1 means missing."
    unit = USD


class ss_calculator_withhold_cola(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    default_value = False
    label = "Social Security calculator withhold cola"
    documentation = "Already-resolved COLA withholding decision for this check year, for example from an E3 policy."

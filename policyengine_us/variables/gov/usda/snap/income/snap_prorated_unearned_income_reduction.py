from policyengine_us.model_api import *


PERSON_LEVEL_UNEARNED_SOURCES = [
    "ssi",
    "social_security",
    "pension_income",
    "veterans_benefits",
    "unemployment_compensation",
    "disability_benefits",
    "workers_compensation",
    "retirement_distributions",
    "child_support_received",
    "alimony_income",
]


class snap_prorated_unearned_income_reduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP prorated unearned income reduction"
    unit = USD
    documentation = (
        "The portion of prorated-disqualified members' Person-level "
        "unearned income that should not be counted per 7 CFR "
        "273.11(c)(2) / (c)(3). SPM-level and tax-unit-level sources "
        "(tanf, general_assistance, rental_income) cannot be "
        "attributed to specific persons for proration and are excluded."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3",
    )

    def formula(spm_unit, period, parameters):
        sources = list(parameters(period).gov.usda.snap.income.sources.unearned)
        applicable = [s for s in PERSON_LEVEL_UNEARNED_SOURCES if s in sources]
        person = spm_unit.members
        is_prorated = person("is_snap_disqualified_prorated", period)
        spm_size = person.spm_unit("spm_unit_size", period)
        prorated_count = person.spm_unit.sum(is_prorated)
        safe_size = where(spm_size > 0, spm_size, 1)
        exclusion_fraction = prorated_count / safe_size
        person_unearned = add(person, period, applicable) if applicable else 0
        return spm_unit.sum(person_unearned * is_prorated * exclusion_fraction)

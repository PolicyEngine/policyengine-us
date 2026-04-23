from policyengine_us.model_api import *


class snap_income_share(Variable):
    value_type = float
    entity = Person
    label = "SNAP income share"
    documentation = (
        "The fraction of this person's income and prorated deductions "
        "that count toward the SNAP unit's calculation, per 7 CFR "
        "273.11(c). For prorated-disqualified members (students, "
        "immigration-ineligible), this equals (total_size - "
        "prorated_count) / total_size so that only the eligible "
        "members' share of the member's income is counted. For all "
        "other persons (eligible members and entirety-disqualified "
        "members under c1), the share is 1.0: their income counts in "
        "full."
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3",
    )

    def formula(person, period, parameters):
        is_prorated = person("is_snap_disqualified_prorated", period)
        spm_size = person.spm_unit("spm_unit_size", period)
        prorated_count = person.spm_unit.sum(is_prorated)
        # Safe division: if spm_size is 0 there is no SPM unit to speak
        # of; the share is irrelevant because income aggregations will
        # also be zero. Guard to avoid NaN.
        safe_size = where(spm_size > 0, spm_size, 1)
        eligible_fraction = (safe_size - prorated_count) / safe_size
        return where(is_prorated, eligible_fraction, 1.0)

from policyengine_us.model_api import *


class mo_ssp_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Missouri SSP citizenship and immigrant status requirement"
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0405-000-00/0405-030-00/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0804-000-00/0804-005-00/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2018/10/appendix_k.pdf#page=1",
        "https://dssmanuals.mo.gov/wp-content/uploads/2018/10/appendix_k.pdf#page=3",
        "https://dssmanuals.mo.gov/wp-content/uploads/2018/10/appendix_k.pdf#page=5",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/1805-020-10-10/1805-020-10-10-05/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/1805-020-10-10/1805-020-10-10-10/",
    )

    def formula(person, period, parameters):
        # SAB (§ 0405.030.00) and Supplemental Nursing Care, which uses the
        # OAA and PTD eligibility requirements (MHABD § 0804.005.00 and
        # Appendix K), apply the MO HealthNet for Families citizenship and
        # immigrant status rules (§ 1805.020.10). Both are state-funded, so
        # the federal Medicaid status changes of October 2026 do not apply.
        p = parameters(period).gov.states.mo.dss.ssp.eligibility.immigration
        status = person("immigration_status", period)
        status_str = status.decode_to_str()
        citizen = status == status.possible_values.CITIZEN
        qualified = np.isin(status_str, p.qualified_statuses)
        no_waiting_period = np.isin(status_str, p.no_waiting_period_statuses)
        waited = person("years_since_us_entry", period) >= p.waiting_period
        # The waiting period does not apply to veterans, active-duty members,
        # their spouses, or their dependent children (§ 1805.020.10.10.10).
        military = person("is_veteran", period) | person("is_military", period)
        self_or_spouse_military = person.marital_unit.any(military)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        military_parent = person.tax_unit.any(military & head_or_spouse)
        dependent = person("is_tax_unit_dependent", period)
        military_exception = self_or_spouse_military | (dependent & military_parent)
        return citizen | (qualified & (no_waiting_period | waited | military_exception))

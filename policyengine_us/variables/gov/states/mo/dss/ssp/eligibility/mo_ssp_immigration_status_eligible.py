from policyengine_us.model_api import *


class mo_ssp_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Missouri SSP citizenship and immigrant status requirement"
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0405-000-00/0405-030-00/",
        "https://web.archive.org/web/20220519212253/https://dssmanuals.mo.gov/december-1973-eligibility-requirements/1010-000-00/",
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0605-000-00/0605-010-00/",
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/1805-020-10-10/1805-020-10-10-05/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-020-00/1805-020-10/1805-020-10-10/1805-020-10-10-10/",
        "https://www.law.cornell.edu/uscode/text/8/1622",
    )

    def formula(person, period, parameters):
        # SAB (§ 0405.030.00) and SNC, which uses the December 1973
        # requirements (SNC § 0605.010.00; December 1973 § 1010.000.00), apply
        # the MO HealthNet for Families citizenship and immigrant status rules
        # of § 1805.020.10, which have not been amended for the October 2026
        # federal Medicaid changes.
        p = parameters(period).gov.states.mo.dss.ssp.eligibility.immigration
        status = person("immigration_status", period)
        status_str = status.decode_to_str()
        citizen = status == status.possible_values.CITIZEN
        qualified = np.isin(status_str, p.qualified_statuses)
        no_waiting_period = np.isin(status_str, p.no_waiting_period_statuses)
        waited = person("years_since_us_entry", period) >= p.waiting_period
        # The waiting period does not apply to veterans, active-duty members,
        # their spouses, or their dependent children (§ 1805.020.10.10.10;
        # 8 USC 1622(b)(3)). A dependent child is under 18 or claimed as a
        # dependent; tax dependents who are parents or fail the qualifying
        # child age test do not count.
        military = person("is_veteran", period) | person("is_military", period)
        married = person.marital_unit.nb_persons() == 2
        spouse_military = married & person.marital_unit.any(military)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        military_parent = person.tax_unit.any(military & head_or_spouse)
        dependent = person("is_tax_unit_dependent", period)
        child = (
            person("is_child", period) | person("is_qualifying_child_dependent", period)
        ) & ~person("is_parent_of_filer_or_spouse", period)
        dependent_child_of_military = dependent & child & military_parent
        military_exception = military | spouse_military | dependent_child_of_military
        return citizen | (qualified & (no_waiting_period | waited | military_exception))

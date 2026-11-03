from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_is_married,
)


class is_ssi_ineligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible child"
    documentation = (
        "A child under the SSI ineligible-child deeming definition who is not "
        "eligible for SSI. "
        "Whose child the person is, and whether they live with the "
        "claimant, are tested where the allocation is summed."
    )
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://www.ecfr.gov/current/title-20/section-416.1856",
        "https://www.law.cornell.edu/uscode/text/42/1382c#c",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310115",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.eligibility.child
        # SI 01310.115 A.3: the ineligible-student deeming limit was under
        # 21 before June 16, 2008 and under 22 afterward. The general SSI
        # child definition remains distinct. Monthly status follows the
        # parameters at the start of the month; no mid-month proration is
        # modeled. Full-time attendance remains the model's proxy for
        # regularly attending school.
        annual_period = period.this_year
        student = person("is_full_time_student", annual_period) & (
            person("age", annual_period) < p.deeming_student_age_limit
        )
        # Marriage is distinct from the co-resident spouse lookup used for
        # deeming: legal spouses can live apart.
        child = (
            (person("is_child", annual_period) | student)
            & ~_ssi_is_married(person, annual_period)
            & ~person("is_household_head", annual_period)
        )
        # 'Is not eligible for SSI benefits': aged, blind or disabled people
        # who meet the citizenship or qualified-noncitizen condition are
        # treated as eligible. The income and resource tests are not read,
        # because they depend on deemed income and so on this allocation.
        immigration_status = person("immigration_status", annual_period)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        eligible = person("is_ssi_aged_blind_disabled", annual_period) & (
            is_citizen | person("is_ssi_qualified_noncitizen", annual_period)
        )
        return child & ~eligible

from policyengine_us.model_api import *


class nj_is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligibility for New Jersey TANF based on age."
    documentation = "Whether a person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."

    def formula(person, period, parameters):
        # title: State Plan for New Jersey TANF, 2021-2023, page 14
        # href: https://www.nj.gov/humanservices/dfd/programs/workfirstnj/tanf_2021_23_st_plan.pdf#page=14
        # title: New Jersey Administrative Code, 10:90-2.2, part (c)(d)
        # href: https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=f96f6864-3540-4a08-b41a-e523b7c5620a&nodeid=AAOAERAADAAC&nodepath=%2FROOT%2FAAO%2FAAOAER%2FAAOAERAAD%2FAAOAERAADAAC&level=4&haschildren=&populated=false&title=%C2%A7+10%3A90-2.2+WFNJ+TANF%2FGA+eligibility+requirements&config=00JAA1YTg5OGJlYi04MTI4LTRlNjQtYTc4Yi03NTQxN2E5NmE0ZjQKAFBvZENhdGFsb2ftaXPxZTR7bRPtX1Jok9kz&pddocfullpath=%2Fshared%2Fdocument%2Fadministrative-codes%2Furn%3AcontentItem%3A5XKV-PWF1-JKHB-61RG-00008-00&ecomp=8gf5kkk&prid=2fb77114-6c52-4b07-8969-f267ef81db7b
        child_under_18 = person("age", period) < 18
        is_under_19 = person("age", period) < 19
        full_time_student = person("is_full_time_student", period)
        school_enrolled_under_19_year_old = full_time_student & is_under_19
        return child_under_18 | school_enrolled_under_19_year_old

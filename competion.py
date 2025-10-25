import math
from sqlalchemy import select
from sqlalchemy.orm import Session

def g(p: int, k: int, m: float) -> int:
    return int(p * math.e ** (-4 * (k - 1) / m))

def act_t(session: Session) -> int:
    active_count = session.query(Team).filter_by(active=True).count()
    total        = session.query(Team).count()
    return max(total/2, active_count, 5)

def submit_answer(session: Session, team_id: int, q_id: int, answer: float) -> bool:
    team    = session.get(Team, team_id)
    question= session.get(Question, q_id)
    attempt = session.get(Attempt, (team_id, q_id))

    if not attempt.sts:
        team.active = True
        r = 0.0 if answer == 0 else answer / question.avg_val

        if question.min_val <= r <= question.max_val:
            question.ca += 1
            attempt.sts   = True
            attempt.bonus= g(20, question.ca, math.sqrt(4 * act_t(session)))

            all_ok = all(a.sts for a in team.attempts)
            if all_ok:
                fin_bonus = g(20 * session.query(Question).count(),
                              session.query(Question).filter(Question.ca>0).count(),
                              math.sqrt(2 * act_t(session)))
                team.bonus += fin_bonus

        else:
            attempt.err += 1

        session.commit()
        return True
    return False

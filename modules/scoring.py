from sqlalchemy import select, update
from modules.database import get_session
from modules.models import Prediction, User, Match


def calculate_points(
    pred_home: int, pred_away: int,
    real_home: int, real_away: int,
) -> int:
    if pred_home == real_home and pred_away == real_away:
        return 3  # placar exato

    pred_winner = _winner(pred_home, pred_away)
    real_winner = _winner(real_home, real_away)
    if pred_winner == real_winner:
        return 1  # acertou o vencedor ou empate

    return 0


def _winner(home: int, away: int) -> str:
    if home > away:
        return "home"
    if away > home:
        return "away"
    return "draw"


def update_scores_for_match(match_id: int) -> int:
    """
    Recalcula pontos de todos os palpites de uma partida finalizada.
    Retorna quantos palpites foram atualizados.
    """
    session = get_session()
    try:
        match = session.get(Match, match_id)
        if not match or match.home_score is None or match.away_score is None:
            return 0

        predictions = session.execute(
            select(Prediction).where(Prediction.match_id == match_id)
        ).scalars().all()

        updated = 0
        for pred in predictions:
            pts = calculate_points(
                pred.predicted_home_score, pred.predicted_away_score,
                match.home_score, match.away_score,
            )
            if pred.points_earned != pts:
                pred.points_earned = pts
                updated += 1

        # Recalcula total_score de cada usuario afetado
        user_ids = {p.user_id for p in predictions}
        for uid in user_ids:
            total = sum(
                p.points_earned for p in session.execute(
                    select(Prediction).where(Prediction.user_id == uid)
                ).scalars().all()
            )
            session.execute(
                update(User).where(User.id == uid).values(total_score=total)
            )

        session.commit()
        return updated
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

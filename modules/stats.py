from datetime import timedelta, timezone

BRT = timezone(timedelta(hours=-3))
FINISHED = ("FT", "AET", "PEN")
GROUP_STAGE_MIN = 1001
GROUP_STAGE_MAX = 1072


def aproveitamento(points_list):
    """points_list: points_earned do usuario em jogos encerrados onde palpitou.
    Retorna percentual inteiro 0-100, ou None se nao ha palpites encerrados."""
    if not points_list:
        return None
    scored = sum(1 for p in points_list if p > 0)
    return round(100 * scored / len(points_list))


def current_streak(points_desc):
    """points_desc: pontos por jogo encerrado, do mais recente para o mais antigo.
    None = usuario nao palpitou naquele jogo (quebra a sequencia)."""
    streak = 0
    for p in points_desc:
        if p is not None and p > 0:
            streak += 1
        else:
            break
    return streak


def ranking_positions(scores):
    """scores: lista de (username, pontos). Retorna dict username -> posicao 1-based."""
    ordered = sorted(scores, key=lambda s: s[1], reverse=True)
    return {name: i + 1 for i, (name, _) in enumerate(ordered)}


def movement(current_pos, previous_pos):
    """Compara posicoes. Retorna dict username -> 'up' | 'down' | 'same'."""
    result = {}
    for name, pos in current_pos.items():
        prev = previous_pos.get(name)
        if prev is None or prev == pos:
            result[name] = "same"
        elif pos < prev:
            result[name] = "up"
        else:
            result[name] = "down"
    return result


def round_top_scorers(points_by_user):
    """points_by_user: dict username -> pontos na ultima rodada.
    Retorna usernames com a maior pontuacao (se > 0); lista vazia caso contrario."""
    if not points_by_user:
        return []
    best = max(points_by_user.values())
    if best <= 0:
        return []
    return [u for u, p in points_by_user.items() if p == best]


def last_finished_day(matches):
    """matches: iteravel de Match. Retorna a date BRT do ultimo dia com jogo
    encerrado, ou None se nenhum jogo encerrou ainda."""
    days = [
        m.kickoff_time.astimezone(BRT).date()
        for m in matches if m.status in FINISHED
    ]
    return max(days) if days else None


def current_phase(matches):
    """Fase atual do torneio derivada dos jogos: 'Mata-Mata' quando toda a fase
    de grupos (match_id 1001-1072) encerrou, senao 'Fase de Grupos'."""
    group = [m for m in matches if GROUP_STAGE_MIN <= m.match_id <= GROUP_STAGE_MAX]
    if group and all(m.status in FINISHED for m in group):
        return "Mata-Mata"
    return "Fase de Grupos"


def load_phase():
    """Loader: fase atual do torneio a partir do banco."""
    from sqlalchemy import select
    from modules.database import get_session
    from modules.models import Match

    session = get_session()
    try:
        matches = session.execute(select(Match)).scalars().all()
    finally:
        session.close()
    return current_phase(matches)


def load_user_stats(user_id, username):
    """Loader: estatisticas pessoais do usuario para o card do dashboard."""
    from sqlalchemy import select
    from modules.database import get_session
    from modules.models import Match, Prediction, User

    session = get_session()
    try:
        users = session.execute(select(User.username, User.total_score)).all()
        finished = session.execute(
            select(Match)
            .where(Match.status.in_(FINISHED))
            .order_by(Match.kickoff_time.desc())
        ).scalars().all()
        preds = {
            p.match_id: p.points_earned
            for p in session.execute(
                select(Prediction).where(Prediction.user_id == user_id)
            ).scalars().all()
        }
    finally:
        session.close()

    positions = ranking_positions([(u, s) for u, s in users])
    pts_finished = [preds[m.match_id] for m in finished if m.match_id in preds]
    return {
        "pontos": dict(users).get(username, 0),
        "posicao": positions.get(username, 0),
        "total_users": len(positions),
        "aproveitamento": aproveitamento(pts_finished),
        "sequencia": current_streak([preds.get(m.match_id) for m in finished]),
    }

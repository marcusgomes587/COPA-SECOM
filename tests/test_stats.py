from modules.stats import (
    aproveitamento,
    current_streak,
    ranking_positions,
    movement,
    round_top_scorers,
)


# -- aproveitamento --

def test_aproveitamento_sem_palpites_retorna_none():
    assert aproveitamento([]) is None


def test_aproveitamento_todos_pontuaram():
    assert aproveitamento([5, 3, 1]) == 100


def test_aproveitamento_metade_pontuou():
    assert aproveitamento([5, 0, 3, 0]) == 50


def test_aproveitamento_arredonda():
    # 2 de 3 = 66.67 -> 67
    assert aproveitamento([3, 1, 0]) == 67


# -- current_streak --

def test_streak_vazia():
    assert current_streak([]) == 0


def test_streak_conta_consecutivos_do_mais_recente():
    # mais recente primeiro: pontuou, pontuou, errou, pontuou
    assert current_streak([3, 5, 0, 3]) == 2


def test_streak_zero_se_errou_o_ultimo():
    assert current_streak([0, 5, 3]) == 0


def test_streak_none_quebra_sequencia():
    # None = nao palpitou naquele jogo
    assert current_streak([3, None, 5]) == 1


# -- ranking_positions --

def test_ranking_ordena_por_pontos_desc():
    pos = ranking_positions([("ana", 10), ("bia", 30), ("caio", 20)])
    assert pos == {"bia": 1, "caio": 2, "ana": 3}


def test_ranking_vazio():
    assert ranking_positions([]) == {}


# -- movement --

def test_movement_subiu_desceu_manteve():
    current = {"ana": 1, "bia": 2, "caio": 3}
    previous = {"ana": 2, "bia": 1, "caio": 3}
    mov = movement(current, previous)
    assert mov == {"ana": "up", "bia": "down", "caio": "same"}


def test_movement_usuario_novo_e_same():
    mov = movement({"ana": 1}, {})
    assert mov == {"ana": "same"}


# -- round_top_scorers --

def test_craque_unico():
    assert round_top_scorers({"ana": 8, "bia": 5}) == ["ana"]


def test_craque_empate_retorna_todos():
    result = round_top_scorers({"ana": 8, "bia": 8, "caio": 3})
    assert sorted(result) == ["ana", "bia"]


def test_craque_ninguem_pontuou_retorna_vazio():
    assert round_top_scorers({"ana": 0, "bia": 0}) == []


def test_craque_dict_vazio():
    assert round_top_scorers({}) == []


# -- last_finished_day / current_phase --

from collections import namedtuple
from datetime import datetime, timezone as _tz

from modules.stats import last_finished_day, current_phase

FakeMatch = namedtuple("FakeMatch", "match_id status kickoff_time")


def _utc(y, mo, d, h):
    return datetime(y, mo, d, h, tzinfo=_tz.utc)


def test_last_finished_day_sem_jogos_encerrados():
    matches = [FakeMatch(1001, "NS", _utc(2026, 6, 11, 18))]
    assert last_finished_day(matches) is None


def test_last_finished_day_converte_para_dia_brt():
    # 01:00 UTC do dia 12 = 22:00 BRT do dia 11
    matches = [FakeMatch(1001, "FT", _utc(2026, 6, 12, 1))]
    assert last_finished_day(matches) == datetime(2026, 6, 11).date()


def test_last_finished_day_retorna_o_mais_recente():
    matches = [
        FakeMatch(1001, "FT", _utc(2026, 6, 11, 18)),
        FakeMatch(1002, "AET", _utc(2026, 6, 13, 18)),
        FakeMatch(1003, "NS", _utc(2026, 6, 15, 18)),
    ]
    assert last_finished_day(matches) == datetime(2026, 6, 13).date()


def test_current_phase_grupos_em_andamento():
    matches = [
        FakeMatch(1001, "FT", _utc(2026, 6, 11, 18)),
        FakeMatch(1002, "NS", _utc(2026, 6, 12, 18)),
    ]
    assert current_phase(matches) == "Fase de Grupos"


def test_current_phase_mata_mata_quando_grupos_encerraram():
    matches = [
        FakeMatch(1001, "FT", _utc(2026, 6, 11, 18)),
        FakeMatch(1002, "FT", _utc(2026, 6, 12, 18)),
        FakeMatch(2001, "NS", _utc(2026, 6, 29, 18)),
    ]
    assert current_phase(matches) == "Mata-Mata"


def test_current_phase_sem_jogos_cadastrados():
    assert current_phase([]) == "Fase de Grupos"

import os
import random
import json
import math
from pathlib import Path

pasta_relatos = "./out/geral" 
ranking_out = "./eval/ranking_elo_"+"geral"+".json"
k_factor = 32


# calcula o novo elo, com 1 ponto se A vence, 0 se B vence e 0.5 para empate
def calcular_elo(r_a: float, r_b: float, resultado: float) -> tuple[float, float]:
    """
    Calcula o novo ELO.
    resultado: 1.0 se A vence, 0.0 se B vence, 0.5 para empate.
    """
    e_a = 1 / (1 + 10 ** ((r_b - r_a) / 400))
    e_b = 1 / (1 + 10 ** ((r_a - r_b) / 400))

    novo_r_a = r_a + k_factor * (resultado - e_a)
    novo_r_b = r_b + k_factor * ((1 - resultado) - e_b)

    return round(novo_r_a, 1), round(novo_r_b, 1)


def carregar_ou_criar_ranking(arquivos: list[str]) -> dict:
    ranking = {}
    if os.path.exists(ranking_out):
        with open(ranking_out, "r", encoding="utf-8") as f:
            ranking = json.load(f)

    for arq in arquivos:
        if arq not in ranking:
            ranking[arq] = 1200.0  # ELO inicial padrão

    return ranking


def salvar_ranking(ranking: dict):
    with open(ranking_out, "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=4, ensure_ascii=False)


# Seleciona dois arquivos com ELOs próximos para um confronto equilibrado.
def selecionar_par_proximo(ranking: dict) -> tuple[str, str]:
    """Seleciona dois arquivos com ELOs próximos para um confronto equilibrado."""
    itens = list(ranking.items())
    if len(itens) < 2:
        return None, None

    # Ordena temporariamente para pegar pares vizinhos no ranking
    itens.sort(key=lambda x: x[1])
    idx = random.randint(0, len(itens) - 2)

    # Pega o item do índice e o seu vizinho (podendo aplicar um pequeno desvio aleatório)
    arq_a = itens[idx][0]
    arq_b = itens[idx + 1][0]

    # Em metade das vezes, inverte a ordem de apresentação A/B
    if random.choice([True, False]):
        return arq_a, arq_b
    return arq_b, arq_a


def ler_conteudo_arquivo(caminho: str) -> str:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            texto = f.read().strip()
            return texto[200:] 
    except Exception as e:
        return f"[Erro ao ler arquivo: {e}]"


def mostrar_ranking(ranking: dict):
    print("\n" + "="*40)
    print(" 🏆 RANKING ATUAL DE ELO 🏆")
    print("="*40)
    rank_ordenado = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    for i, (arq, elo) in enumerate(rank_ordenado, 1):
        print(f"{i:2d}. {elo:6.1f} pts | {arq}")
    print("="*40 + "\n")



def main():
    pasta = Path(pasta_relatos)

    arquivos = [f.name for f in pasta.iterdir() if f.is_file()
                and not f.name.startswith(".")]

    ranking = carregar_ou_criar_ranking(arquivos)
    num_iteracoes=0

    while True:
        doc_a_nome, doc_b_nome = selecionar_par_proximo(ranking)

        doc_a_path = pasta / doc_a_nome
        doc_b_path = pasta / doc_b_nome

        txt_a = ler_conteudo_arquivo(doc_a_path)
        txt_b = ler_conteudo_arquivo(doc_b_path)

        print("\n" + "─"*80)
        print(f"DOCUMENTO A:)")
        print("─"*80)
        print(txt_a)

        print("\n" + "─"*80)
        print(f"DOCUMENTO B:)")
        print("─"*80)
        print(txt_b)
        print("─"*80)

        while True:
            voto = input(
                "\nQual é o melhor? [1 / 2 / (e)mpate / (q)uit: ").strip().lower()

            if voto == 'q':
                salvar_ranking(ranking)
                mostrar_ranking(ranking)
                print("Encerrando e salvando pontuações...")
                return
            elif voto in ['1', '2', 'e']:
                break
            else:
                print("Opção inválida! Digite 1, 2, e ou q.")

        # Atualização das notas ELO
        res = 1.0 if voto == '1' else (0.0 if voto == '2' else 0.5)
        elo_a_antigo = ranking[doc_a_nome]
        elo_b_antigo = ranking[doc_b_nome]

        novo_a, novo_b = calcular_elo(elo_a_antigo, elo_b_antigo, res)

        ranking[doc_a_nome] = novo_a
        ranking[doc_b_nome] = novo_b

        num_iteracoes += 1

        salvar_ranking(ranking)

        # Output rápido de feedback
        diff_a = f"{novo_a - elo_a_antigo:+.1f}"
        diff_b = f"{novo_b - elo_b_antigo:+.1f}"
        print(f"\nRegistrado! {doc_a_nome}: {novo_a} ({diff_a}) | {doc_b_nome}: {novo_b} ({diff_b}) - interacao {num_iteracoes}")


if __name__ == "__main__":
    main()

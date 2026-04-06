from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime

from database.connection import get_db
from models.consumo import Consumo
from models.usuario import Usuario

router = APIRouter(prefix="/insights", tags=["Insights"])


def buscar_usuario(db: Session, usuario_id: int):
    # Garante que o usuário existe antes de fazer qualquer análise
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return usuario


def buscar_consumos_usuario(db: Session, usuario_id: int):
    # Busca todos os consumos do usuário
    consumos = db.query(Consumo).filter(Consumo.usuario_id == usuario_id).all()

    if not consumos:
        raise HTTPException(
            status_code=404,
            detail="Nenhum consumo encontrado para este usuário"
        )

    return consumos


def filtrar_ultimos_meses(consumos, quantidade_meses: int):
    # Descobre quais são os meses mais recentes presentes nos dados
    meses_disponiveis = sorted(
        {consumo.data.strftime("%Y-%m") for consumo in consumos}
    )

    # Pega apenas os últimos meses da janela escolhida
    meses_selecionados = set(meses_disponiveis[-quantidade_meses:])

    consumos_filtrados = [
        consumo for consumo in consumos
        if consumo.data.strftime("%Y-%m") in meses_selecionados
    ]

    return consumos_filtrados, sorted(meses_selecionados)


def agrupar_consumos_por_tipo_e_mes(consumos):
    # Organiza os dados por categoria e por mês
    dados = defaultdict(lambda: defaultdict(float))

    for consumo in consumos:
        mes = consumo.data.strftime("%Y-%m")
        dados[consumo.tipo][mes] += float(consumo.gasto)

    return dados


def calcular_tendencia(crescimento: float):
    # Traduz o número em uma classificação mais amigável
    if crescimento > 0.05:
        return "alta"
    elif crescimento < -0.05:
        return "queda"
    return "estavel"


def gerar_projecao_por_tipo(dados_usuario, meses_projetados: int):
    # Gera a projeção futura de cada categoria separadamente
    categorias = {}
    total_previsao = 0.0
    houve_tendencia_alta = False
    houve_tendencia_queda = False

    for tipo, meses_dict in dados_usuario.items():
        meses_ordenados = sorted(meses_dict.items(), key=lambda item: item[0])
        valores = [valor for _, valor in meses_ordenados]

        if len(valores) == 1:
            primeiro = valores[0]
            ultimo = valores[0]
            crescimento = 0
        else:
            primeiro = valores[0]
            ultimo = valores[-1]

            if primeiro == 0:
                crescimento = 0
            else:
                crescimento = (ultimo - primeiro) / primeiro

        tendencia = calcular_tendencia(crescimento)
        crescimento_percentual = round(crescimento * 100, 2)

        if tendencia == "alta":
            houve_tendencia_alta = True
        elif tendencia == "queda":
            houve_tendencia_queda = True

        previsoes = []
        valor_atual = ultimo

        for _ in range(meses_projetados):
            valor_atual = valor_atual * (1 + crescimento)
            previsoes.append(round(valor_atual, 2))

        total_tipo = round(sum(previsoes), 2)
        total_previsao += total_tipo

        categorias[tipo] = {
            "ultimo_mes": round(ultimo, 2),
            "crescimento_percentual": crescimento_percentual,
            "tendencia": tendencia,
            "previsao": previsoes,
            "total_projetado": total_tipo
        }

    return {
        "categorias": categorias,
        "previsao_total": round(total_previsao, 2),
        "houve_tendencia_alta": houve_tendencia_alta,
        "houve_tendencia_queda": houve_tendencia_queda
    }


def calcular_media_mensal_geral(consumos):
    # Soma tudo por mês e tira uma média geral mensal
    gastos_por_mes = defaultdict(float)

    for consumo in consumos:
        mes = consumo.data.strftime("%Y-%m")
        gastos_por_mes[mes] += float(consumo.gasto)

    valores = list(gastos_por_mes.values())

    if not valores:
        return 0.0

    return sum(valores) / len(valores)


def buscar_consumos_mesma_regiao(db: Session, regiao: str):
    # Busca usuários da mesma região
    usuarios_regiao = db.query(Usuario).filter(Usuario.regiao == regiao).all()
    ids_usuarios = [usuario.id for usuario in usuarios_regiao]

    if not ids_usuarios:
        return []

    consumos_regiao = db.query(Consumo).filter(
        Consumo.usuario_id.in_(ids_usuarios)
    ).all()

    return consumos_regiao


def calcular_media_regional(consumos_regiao):
    # Calcula a média mensal de cada usuário da região e depois a média geral da região
    gastos_por_usuario_mes = defaultdict(lambda: defaultdict(float))

    for consumo in consumos_regiao:
        mes = consumo.data.strftime("%Y-%m")
        gastos_por_usuario_mes[consumo.usuario_id][mes] += float(consumo.gasto)

    medias = []

    for _, meses_dict in gastos_por_usuario_mes.items():
        valores = list(meses_dict.values())
        if valores:
            medias.append(sum(valores) / len(valores))

    if not medias:
        return 0.0

    return sum(medias) / len(medias)


def calcular_media_mensal_por_tipo(consumos):
    # Para cada categoria, soma por mês e depois tira a média mensal daquela categoria
    gastos_por_tipo_mes = defaultdict(lambda: defaultdict(float))

    for consumo in consumos:
        mes = consumo.data.strftime("%Y-%m")
        gastos_por_tipo_mes[consumo.tipo][mes] += float(consumo.gasto)

    medias_por_tipo = {}

    for tipo, meses_dict in gastos_por_tipo_mes.items():
        valores = list(meses_dict.values())
        medias_por_tipo[tipo] = sum(valores) / len(valores) if valores else 0.0

    return medias_por_tipo


def calcular_media_regional_por_tipo(consumos_regiao):
    # Aqui a ideia é comparar o usuário com a média regional por categoria,
    # mas de forma mensal e por usuário
    gastos_tipo_usuario_mes = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for consumo in consumos_regiao:
        mes = consumo.data.strftime("%Y-%m")
        gastos_tipo_usuario_mes[consumo.tipo][consumo.usuario_id][mes] += float(consumo.gasto)

    medias_regionais_por_tipo = {}

    for tipo, usuarios_dict in gastos_tipo_usuario_mes.items():
        medias_usuarios = []

        for _, meses_dict in usuarios_dict.items():
            valores = list(meses_dict.values())
            if valores:
                medias_usuarios.append(sum(valores) / len(valores))

        medias_regionais_por_tipo[tipo] = (
            sum(medias_usuarios) / len(medias_usuarios)
            if medias_usuarios else 0.0
        )

    return medias_regionais_por_tipo


def montar_comparativo_por_tipo_mensal(consumos_usuario, consumos_regiao):
    # Compara a média mensal do usuário por categoria
    # com a média mensal regional daquela mesma categoria
    media_usuario_por_tipo = calcular_media_mensal_por_tipo(consumos_usuario)
    media_regional_por_tipo = calcular_media_regional_por_tipo(consumos_regiao)

    todos_os_tipos = set(media_usuario_por_tipo.keys()) | set(media_regional_por_tipo.keys())
    comparativo = {}

    for tipo in todos_os_tipos:
        media_usuario = media_usuario_por_tipo.get(tipo, 0.0)
        media_regional = media_regional_por_tipo.get(tipo, 0.0)

        if media_regional == 0:
            situacao = "sem dados suficientes"
        elif media_usuario > media_regional:
            situacao = "acima da média"
        elif media_usuario < media_regional:
            situacao = "abaixo da média"
        else:
            situacao = "igual à média"

        comparativo[tipo] = {
            "media_mensal_usuario": round(media_usuario, 2),
            "media_mensal_regional": round(media_regional, 2),
            "diferenca": round(media_usuario - media_regional, 2),
            "situacao": situacao
        }

    return comparativo


def calcular_situacao_regional(media_usuario: float, media_regional: float):
    # Resume a situação geral do usuário em relação à região
    if media_regional == 0:
        return "sem dados suficientes na região"
    elif media_usuario > media_regional:
        return "acima da média regional"
    elif media_usuario < media_regional:
        return "abaixo da média regional"
    return "igual à média regional"


def calcular_indice_concentracao(categorias):
    # Mede se o gasto está muito concentrado em uma única categoria
    totais = [dados["ultimo_mes"] for dados in categorias.values()]

    if not totais:
        return 0.0

    total = sum(totais)
    if total == 0:
        return 0.0

    maior_categoria = max(totais)
    return maior_categoria / total


def calcular_score_justo(
    media_usuario,
    media_regional,
    houve_tendencia_alta,
    houve_tendencia_queda,
    categorias
):
    # O score começa neutro e vai sendo ajustado conforme o comportamento
    score = 50
    motivos = []

    # Tendência geral
    if houve_tendencia_alta:
        score -= 10
        motivos.append("Foi detectada tendência de aumento em pelo menos uma categoria")

    if houve_tendencia_queda:
        score += 5
        motivos.append("Houve queda de gastos em pelo menos uma categoria")

    # Comparação regional
    if media_regional > 0:
        diferenca_percentual = (media_usuario - media_regional) / media_regional

        if diferenca_percentual > 0.20:
            score -= 15
            motivos.append("Seu gasto médio está muito acima da média da sua região")
        elif diferenca_percentual > 0.05:
            score -= 8
            motivos.append("Seu gasto médio está um pouco acima da média da sua região")
        elif diferenca_percentual < -0.15:
            score += 12
            motivos.append("Seu gasto médio está bem abaixo da média da sua região")
        elif diferenca_percentual < -0.05:
            score += 6
            motivos.append("Seu gasto médio está abaixo da média da sua região")

    # Crescimento por categoria
    crescimentos_altos = 0
    crescimentos_moderados = 0

    for tipo, dados_tipo in categorias.items():
        crescimento = dados_tipo["crescimento_percentual"]

        if crescimento > 25:
            crescimentos_altos += 1
        elif crescimento > 10:
            crescimentos_moderados += 1

    if crescimentos_altos > 0:
        score -= 12
        motivos.append("Uma ou mais categorias tiveram crescimento muito alto")
    elif crescimentos_moderados > 0:
        score -= 6
        motivos.append("Algumas categorias apresentaram crescimento moderado")

    # Concentração exagerada em uma única categoria
    indice_concentracao = calcular_indice_concentracao(categorias)

    if indice_concentracao > 0.65:
        score -= 8
        motivos.append("Seus gastos estão muito concentrados em uma única categoria")
    elif indice_concentracao < 0.40 and len(categorias) > 1:
        score += 4
        motivos.append("Seus gastos estão relativamente equilibrados entre as categorias")

    # Limites do score
    score = max(0, min(score, 100))

    if score >= 85:
        nivel = "Excelente"
    elif score >= 70:
        nivel = "Bom"
    elif score >= 50:
        nivel = "Regular"
    else:
        nivel = "Crítico"

    if not motivos:
        motivos.append("Seu comportamento financeiro está estável dentro da janela analisada")

    return {
        "valor": score,
        "nivel": nivel,
        "motivos": motivos
    }


@router.get("/projecao/{usuario_id}")
def projecao_por_tipo_v2(
    usuario_id: int,
    meses_projetados: int = 3,
    janela_meses: int = 3,
    db: Session = Depends(get_db)
):
    # 1. Garante que o usuário existe
    usuario = buscar_usuario(db, usuario_id)

    # 2. Busca os consumos do usuário
    consumos_usuario = buscar_consumos_usuario(db, usuario_id)

    # 3. Filtra somente a janela mais recente
    consumos_usuario_filtrados, meses_analisados = filtrar_ultimos_meses(
        consumos_usuario,
        janela_meses
    )

    if not consumos_usuario_filtrados:
        raise HTTPException(
            status_code=404,
            detail="Não há consumos suficientes na janela analisada"
        )

    # 4. Organiza os consumos por categoria e mês
    dados_usuario = agrupar_consumos_por_tipo_e_mes(consumos_usuario_filtrados)

    # 5. Faz a projeção futura
    resultado_projecao = gerar_projecao_por_tipo(dados_usuario, meses_projetados)

    # 6. Busca consumos da mesma região e aplica a mesma janela
    consumos_regiao = buscar_consumos_mesma_regiao(db, usuario.regiao)
    consumos_regiao_filtrados, _ = filtrar_ultimos_meses(consumos_regiao, janela_meses)

    # 7. Calcula médias gerais
    media_usuario = calcular_media_mensal_geral(consumos_usuario_filtrados)
    media_regional = calcular_media_regional(consumos_regiao_filtrados)

    # 8. Monta comparativo mensal por tipo
    comparativo_por_tipo = montar_comparativo_por_tipo_mensal(
        consumos_usuario_filtrados,
        consumos_regiao_filtrados
    )

    # 9. Situação geral do usuário em relação à região
    situacao_regional = calcular_situacao_regional(media_usuario, media_regional)

    # 10. Gera um score mais justo
    score = calcular_score_justo(
        media_usuario=media_usuario,
        media_regional=media_regional,
        houve_tendencia_alta=resultado_projecao["houve_tendencia_alta"],
        houve_tendencia_queda=resultado_projecao["houve_tendencia_queda"],
        categorias=resultado_projecao["categorias"]
    )

    return {
        "usuario_id": usuario_id,
        "regiao": usuario.regiao,
        "janela_meses_analisada": janela_meses,
        "meses_considerados": meses_analisados,
        "meses_projetados": meses_projetados,
        "previsao_total": round(resultado_projecao["previsao_total"], 2),
        "categorias": resultado_projecao["categorias"],
        "comparativo_regional": {
            "media_mensal_usuario": round(media_usuario, 2),
            "media_mensal_regional": round(media_regional, 2),
            "diferenca": round(media_usuario - media_regional, 2),
            "situacao": situacao_regional,
            "por_tipo": comparativo_por_tipo
        },
        "score": score
    }
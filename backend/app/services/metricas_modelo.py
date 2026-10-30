import re
import sqlite3
from pathlib import Path

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

DB_PATH = Path(__file__).resolve().parents[2] / "noticias_cepea.db"
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CAMINHO_AMOSTRA = DATA_DIR / "todas-noticias-e-amostra-classificada.csv"

ESTRATEGIA_PSEUDO = "Estrategia 2: TF-IDF + ML (pseudo-labels do lexico, holdout nas 611 amostras manuais)"
ESTRATEGIA_CV = "Estrategia 2: TF-IDF + ML (titulo + rotulo manual real, validacao cruzada 5-fold)"

KEYWORDS = re.compile(
    r"(dólar|exporta|compras|safra|prejuízo|superprodução|demanda|greve|seca|cotaç|preço|saca|mercado)",
    re.IGNORECASE,
)

EXTERNO_TERMS = ["eua", "china", "chicago", "global", "mundial", "exporta", "dólar", "dolar", "internacional", "outros países", "clima nos eua"]
INTERNO_TERMS = ["brasil", "brasileiro", "conab", "porto de", "paraná", "mato grosso", "rio grande do sul", "nacional", "interna", "greve", "bloqueio", "rodovia"]
POSITIVO_TERMS = ["alta", "puxa", "valoriz", "subir", "sobe", "aumento", "melhora", "aquecimento", "recorde", "ganho", "frustração de safra exterior"]
NEGATIVO_TERMS = ["queda", "caiu", "desvaloriz", "derruba", "prejuízo", "seca", "quebra", "redução", "trava", "paralisa", "baixo", "perda", "superprodução"]


def classificar_por_lexico(texto):
    # mesma regra da Estrategia 1 do notebook: conta termos de cada lista e decide por contagem
    texto = texto.lower()

    ext_score = sum(texto.count(termo) for termo in EXTERNO_TERMS)
    int_score = sum(texto.count(termo) for termo in INTERNO_TERMS)
    pos_score = sum(texto.count(termo) for termo in POSITIVO_TERMS)
    neg_score = sum(texto.count(termo) for termo in NEGATIVO_TERMS)

    escopo = "mercado externo" if ext_score >= int_score else "mercado interno"

    if abs(pos_score - neg_score) <= 1:
        impacto = "neutro"
    elif pos_score > neg_score:
        impacto = "positivo"
    else:
        impacto = "negativo"

    return f"{escopo} {impacto}"


def reduzir_texto(texto, max_sentencas=6):
    # replica a "Smart Reduction" do notebook: pega as frases com mais palavras-chave, mais intro/conclusao
    if not isinstance(texto, str) or len(texto.strip()) == 0:
        return ""

    frases = sent_tokenize(texto)
    if len(frases) <= max_sentencas:
        return texto

    pontuadas = []
    for i, frase in enumerate(frases):
        score = len(KEYWORDS.findall(frase))
        if i == 0:
            score += 1.5
        elif i == len(frases) - 1:
            score += 1.0
        pontuadas.append((score, i, frase))

    pontuadas.sort(key=lambda x: x[0], reverse=True)
    indices = sorted(x[1] for x in pontuadas[:max_sentencas])
    return " ".join(frases[i] for i in indices)


def carregar_dados():
    noticias = pd.read_csv(DATA_DIR / "noticias_classificadas_todas.csv", sep=";", on_bad_lines="skip", encoding="utf-8")
    noticias.columns = [c.replace('"', "").strip() for c in noticias.columns]
    noticias = noticias.drop_duplicates(subset="Título")

    amostra = pd.read_csv(DATA_DIR / "todas-noticias-e-amostra-classificada.csv", sep=",", on_bad_lines="skip", encoding="utf-8")
    amostra.columns = [c.replace('"', "").strip() for c in amostra.columns]
    amostra = amostra.dropna(subset=["Análise Manual"])

    titulos_avaliacao = set(amostra["Título"])
    treino = noticias[~noticias["Título"].isin(titulos_avaliacao)]

    return treino, amostra


def avaliar_cv_literal():
    # Estrategia 2 ao pe da letra: TF-IDF no Titulo treinado direto no rotulo manual, com CV de verdade
    amostra = pd.read_csv(CAMINHO_AMOSTRA, sep=",", on_bad_lines="skip", encoding="utf-8")
    amostra.columns = [c.replace('"', "").strip() for c in amostra.columns]
    amostra = amostra.dropna(subset=["Análise Manual"])
    titulo = amostra["Título"].fillna("")
    classe = amostra["Análise Manual"].astype(str).str.strip().str.lower()

    nltk.download("stopwords", quiet=True)
    pt_stopwords = stopwords.words("portuguese")
    vectorizer = TfidfVectorizer(max_features=100, stop_words=pt_stopwords)
    clf = LogisticRegression(C=0.8, class_weight="balanced", random_state=42)

    X = vectorizer.fit_transform(titulo)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    y_pred = cross_val_predict(clf, X, classe, cv=cv)

    return _montar_resultado(classe, y_pred)


def avaliar_pseudo_label():
    treino, amostra = carregar_dados()

    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

    textos_treino = treino["Texto"].fillna("").apply(reduzir_texto)
    pseudo_labels = textos_treino.apply(classificar_por_lexico)

    vectorizer = TfidfVectorizer(max_features=500, stop_words=None)
    X_treino = vectorizer.fit_transform(textos_treino)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_treino, pseudo_labels)

    # avaliacao: o modelo nunca treinou com estas 611 notas nem com Analise Manual em nenhum momento
    textos_eval = amostra["Texto"].fillna("").apply(reduzir_texto)
    X_eval = vectorizer.transform(textos_eval)
    y_true = amostra["Análise Manual"].astype(str).str.strip().str.lower()
    y_pred = clf.predict(X_eval)

    return _montar_resultado(y_true, y_pred)


def _montar_resultado(y_true, y_pred):
    acuracia = accuracy_score(y_true, y_pred)
    precisao, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    relatorio = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    return {
        "geral": {
            "acuracia": acuracia,
            "precisao": precisao,
            "recall": recall,
            "f1": f1,
            "amostras": len(y_true),
        },
        "por_classe": relatorio,
    }


def gravar(conn, estrategia, metodo_avaliacao, resultado):
    geral = resultado["geral"]
    conn.execute("DELETE FROM metricas_modelo WHERE estrategia = ?", (estrategia,))
    conn.execute(
        """
        INSERT INTO metricas_modelo (estrategia, acuracia, precisao, recall, f1, tempo_execucao, amostras, metodo_avaliacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            estrategia,
            geral["acuracia"],
            geral["precisao"],
            geral["recall"],
            geral["f1"],
            None,
            geral["amostras"],
            metodo_avaliacao,
        ),
    )

    conn.execute("DELETE FROM metricas_por_classe WHERE estrategia = ?", (estrategia,))
    for classe, m in resultado["por_classe"].items():
        if classe in ("accuracy", "macro avg", "weighted avg"):
            continue
        conn.execute(
            """
            INSERT INTO metricas_por_classe (estrategia, classe, precisao, recall, f1, suporte)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (estrategia, classe, m["precision"], m["recall"], m["f1-score"], int(m["support"])),
        )

    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)

    resultado_cv = avaliar_cv_literal()
    print(f"[CV literal] acuracia={resultado_cv['geral']['acuracia']:.4f} "
          f"f1={resultado_cv['geral']['f1']:.4f} amostras={resultado_cv['geral']['amostras']}")
    gravar(conn, ESTRATEGIA_CV, "validacao cruzada 5-fold (StratifiedKFold)", resultado_cv)

    resultado_pseudo = avaliar_pseudo_label()
    print(f"[pseudo-label] acuracia={resultado_pseudo['geral']['acuracia']:.4f} "
          f"f1={resultado_pseudo['geral']['f1']:.4f} amostras={resultado_pseudo['geral']['amostras']}")
    gravar(conn, ESTRATEGIA_PSEUDO, "holdout: treinado com pseudo-labels do lexico, nunca viu Analise Manual", resultado_pseudo)

    conn.close()
    print("metricas gravadas no banco")

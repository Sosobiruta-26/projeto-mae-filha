# VIBE BRIDGE — Especificação Técnica, Matemática e Algorítmica

## 1. Objetivo

O projeto parte da seguinte Guiding Question:

> Como um sistema de recomendação musical pode maximizar a descoberta de novas músicas, mantendo a compatibilidade sonora com as preferências do usuário?

O Vibe Bridge é um sistema de recomendação musical desenvolvido para equilibrar dois objetivos principais:

- **Compatibilidade sonora**: recomendar músicas que apresentem características sonoras compatíveis com as preferências do usuário.
- **Descoberta musical**: favorecer músicas que o usuário provavelmente ainda não conhece, priorizando inicialmente faixas de menor popularidade.

Dessa forma, o Vibe Bridge não busca simplesmente a música mais popular ou a música mais semelhante àquela que o usuário já conhece. O objetivo é explorar deliberadamente a região do espaço musical caracterizada por:

$$\boxed{\text{Alta Similaridade Sonora} \quad + \quad \text{Baixa Popularidade}}$$

---

## 2. Conceito

Cada música é representada por um vetor de características musicais.

Seja uma música $x$:

$$\mathbf{x} = [x_1, x_2, \ldots, x_n]$$

onde cada componente representa uma característica musical presente no conjunto de dados.

Por exemplo:

$$\mathbf{x} = [\,energy,\ danceability,\ valence,\ acousticness,\ tempo,\ \ldots\,]$$

A partir dessa representação vetorial, é possível calcular a proximidade entre diferentes músicas no espaço de características.

> **Questão em aberto:** como tratar as diferentes escalas das variáveis acústicas (ex.: $tempo$ em BPM $[0,240]$ vs. $valence$ $[0,1]$) no vetor $\mathbf{x}$ para evitar que atributos de maior magnitude dominem o cálculo de distância no espaço multidimensional? (ver Seção 17.2 — Normalização)

---

## 3. Espaço de Decisão

Embora a representação interna das músicas seja multidimensional, o problema de recomendação pode ser visualizado conceitualmente por meio de dois eixos principais:

**Eixo 1 — Similaridade sonora**: $S(x,A)$
Representa o grau de compatibilidade sonora entre uma música candidata $x$ e uma música ou preferência de referência $A$.

**Eixo 2 — Popularidade**: $P(x)$
Representa o nível de popularidade da música candidata $x$.

O objetivo é encontrar músicas que estejam simultaneamente próximas da preferência sonora do usuário e em uma região de menor popularidade.

### 3.1 Quadrantes de Decisão

```
                         ALTA SIMILARIDADE SONORA
                                  ↑
                                  │
             ❌                   │                  ⭐
       Popular + Similar          │           VIBE BRIDGE
       Recomendação               │       Alta Similaridade
       Convencional               │       Baixa Popularidade
                                  │
                                  │
             ❌                   │                  ?
       Popular + Diferente        │       Desconhecido + Diferente
       Irrelevante                │       Descoberta sem garantia
                                  │       de compatibilidade
                                  └────────────────────────→
                                      BAIXA POPULARIDADE
                                           ALTA
```

O quadrante prioritário do Vibe Bridge é o **superior direito**: alta similaridade sonora combinada com baixa popularidade.

---

## 4. Compatibilidade Sonora

A primeira etapa consiste em identificar músicas suficientemente compatíveis com a preferência do usuário.

Define-se:

$$S(x,A) \in [0,1]$$

como a similaridade sonora entre a música candidata $x$ e a referência $A$.

É estabelecido um limiar mínimo de similaridade:

$$\boxed{S(x,A) \geq \tau}$$

onde:

$$\tau \in [0,1]$$

representa o nível mínimo de compatibilidade considerado aceitável.

Assim, o sistema inicialmente elimina músicas que não apresentam compatibilidade suficiente. O conjunto de candidatas pode ser definido como:

$$\mathcal{C} = \{x \mid S(x,A) \geq \tau\}$$

Portanto: a descoberta ocorre dentro de uma região musicalmente compatível.

---

## 5. Popularidade e Potencial de Descoberta

A popularidade da música é representada por:

$$P(x) \in [0,1]$$

onde:
- $P(x) = 1$ representa alta popularidade
- $P(x) = 0$ representa baixa popularidade

A partir disso, define-se um potencial de descoberta:

$$\boxed{D(x) = 1 - P(x)}$$

Quanto menor a popularidade, maior o potencial de descoberta. Assim, $D(x) \rightarrow 1$ representa uma música com maior potencial de descoberta.

---

## 6. Otimização da Descoberta

Após restringir o espaço às músicas suficientemente compatíveis, o sistema pode buscar aquela com maior potencial de descoberta.

O problema pode ser formalizado como:

$$\boxed{\underset{x}{\operatorname{maximizar}} \; D(x)}$$

sujeito a:

$$\boxed{S(x,A) \geq \tau}$$

Em outras palavras: entre as músicas que apresentam compatibilidade sonora suficiente, selecionar aquelas com maior potencial de descoberta.

Essa restrição é fundamental. O sistema não deve maximizar a descoberta independentemente da similaridade, pois isso poderia resultar na recomendação de músicas pouco populares, porém musicalmente incompatíveis.

---

## 7. Função de Pontuação

Uma segunda abordagem — que **generaliza** a formulação da Seção 6 — consiste em combinar os dois objetivos em uma única função de pontuação, em vez de tratar a descoberta como o único critério de maximização.

Define-se:

$$\alpha \in [0,1]$$

como o peso atribuído à similaridade sonora. A função de pontuação é:

$$\boxed{Score(x) = \alpha S(x,A) + (1-\alpha)D(x)}$$

mantendo a restrição:

$$S(x,A) \geq \tau$$

O parâmetro $\alpha$ controla o equilíbrio entre compatibilidade e descoberta. Note que, quando $\alpha \rightarrow 0$, $Score(x)$ converge para a formulação pura de maximização de $D(x)$ apresentada na Seção 6 — ou seja, a Seção 6 é o caso particular de $\alpha = 0$ desta formulação mais geral.

---

## 8. Modos de Recomendação

O parâmetro $\alpha$ pode posteriormente ser associado a um controle de preferência do usuário.

**Modo Similaridade**
$$Score(x) = 0.9\,S(x,A) + 0.1\,D(x)$$
O sistema prioriza fortemente a compatibilidade sonora. 🎵 Muito parecido → 🎵 Muito parecido → 🎵 Parecido

**Modo Equilibrado**
$$Score(x) = 0.5\,S(x,A) + 0.5\,D(x)$$
O sistema busca um equilíbrio entre similaridade e descoberta. 🎵 Parecido → ⭐ Menos popular → 🎵 Parecido → ⭐ Menos popular

**Modo Descoberta**
$$Score(x) = 0.4\,S(x,A) + 0.6\,D(x)$$
O sistema dá maior importância à descoberta, mas continua sujeito ao limite mínimo de similaridade $S(x,A) \geq \tau$. 🎵 Compatível → ⭐ Pouco conhecido → ⭐ Pouco conhecido

> **Observação:** os valores de $\alpha$ apresentados são parâmetros iniciais para experimentação e deverão ser avaliados empiricamente.

---

## 9. Popularidade ≠ Familiaridade

Um aspecto importante da evolução do modelo é distinguir popularidade de familiaridade do usuário.

A popularidade representa o alcance da música no conjunto de dados: $P(x)$.

A familiaridade representa o quanto um determinado usuário provavelmente já conhece aquela música: $F(x \mid u)$.

Portanto:

$$\boxed{P(x) \neq F(x \mid u)}$$

Uma música pode ser muito popular e ainda assim ser desconhecida por determinado usuário. Da mesma forma, uma música pouco popular pode já fazer parte do histórico daquele usuário.

---

## 10. Descoberta Personalizada

Em uma futura evolução do sistema, o potencial de descoberta poderá ser calculado individualmente para cada usuário.

Define-se:

$$D(x \mid u) = 1 - F(x \mid u)$$

onde:

$$F(x \mid u) \in [0,1]$$

representa a familiaridade estimada do usuário $u$ com a música $x$. A função de pontuação personalizada seria então:

$$\boxed{Score(x \mid u) = \alpha S(x,u) + (1-\alpha)D(x \mid u)}$$

sujeita a:

$$S(x,u) \geq \tau$$

Nesse estágio, o sistema deixa de buscar apenas músicas de baixa popularidade e passa a buscar especificamente: músicas compatíveis que o usuário ainda não conhece.

---

## 11. O Conceito de "Bridge"

O conceito de Bridge pode ser expandido para representar uma transição entre diferentes regiões do espaço musical.

Considere duas músicas: $\mathbf{x}_A$ e $\mathbf{x}_B$.

Uma trajetória entre esses pontos pode ser representada por interpolação linear:

$$\boxed{\mathbf{x}(t) = (1-t)\mathbf{x}_A + t\mathbf{x}_B}$$

onde $t \in [0,1]$.

Essa interpolação gera uma trajetória conceitual:

```
A ───── X₁ ───── X₂ ───── X₃ ───── B
```

As músicas $X_1, X_2, X_3$ podem representar diferentes pontos intermediários no espaço de características musicais. O objetivo é investigar se essas regiões intermediárias podem ser utilizadas para criar transições musicais coerentes e favorecer a descoberta de novas músicas.

---

## 12. Seleção de Candidatos

Para cada ponto intermediário $\mathbf{x}(t)$, podem ser identificadas músicas próximas utilizando uma função de distância $d(\mathbf{x}, \mathbf{x}(t))$ ou uma função de similaridade $S(\mathbf{x}, \mathbf{x}(t))$.

O conjunto de candidatas pode ser definido como:

$$\mathcal{C}_t = \{x : S(x, \mathbf{x}(t)) \geq \tau\}$$

Posteriormente, essas candidatas podem ser ordenadas segundo o potencial de descoberta.

---

## 13. Pipeline Conceitual

```
                 PREFERÊNCIA DO USUÁRIO
                        │
                        ▼
              ┌──────────────────┐
              │  Características │
              │      musicais    │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   Representação  │
              │      vetorial    │
              └────────┬─────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   Similaridade   │
              │   sonora S(x,u)  │
              └────────┬─────────┘
                        │
                        ▼
                Limite mínimo τ
                        │
                 S(x,u) ≥ τ
                        │
                        ▼
              ┌──────────────────┐
              │ Músicas          │
              │ candidatas       │
              └────────┬─────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
      Popularidade P(x)     Familiaridade F(x|u)
             │                     │
             └──────────┬──────────┘
                         ▼
                Potencial de descoberta
                         │
                         ▼
              Ranking (Similaridade + Descoberta)
                         │
                         ▼
                   ⭐ DESCOBERTA
                         │
                         ▼
                Nova música / artista
```

---

## 14. Princípio Fundamental

O princípio central do Vibe Bridge pode ser resumido como:

$$\boxed{\text{Descobrir sem perder a vibe}}$$

Matematicamente:

$$\boxed{\max_{x} D(x \mid u) \quad \text{sujeito a} \quad S(x,u) \geq \tau}$$

O sistema procura, portanto, maximizar o potencial de descoberta dentro de uma região de compatibilidade sonora aceitável.

---

## 15. Hipótese de Pesquisa

A hipótese central do projeto é:

> Uma estratégia de recomendação que otimiza explicitamente a descoberta dentro de uma região de similaridade sonora pode expor usuários a músicas menos familiares, mantendo maior compatibilidade musical do que estratégias baseadas exclusivamente em popularidade ou similaridade.

Essa hipótese poderá ser investigada por meio da comparação entre diferentes estratégias de recomendação:

1. Recomendação baseada em popularidade
2. Recomendação baseada em similaridade
3. Similaridade + popularidade
4. Descoberta condicionada à similaridade
5. Descoberta personalizada baseada na familiaridade do usuário

---

## 16. Evolução do Projeto

A especificação matemática conduz naturalmente às próximas etapas de desenvolvimento:

```
ANÁLISE EXPLORATÓRIA
        │
        ▼
ENGENHARIA DE FEATURES
        │
        ▼
REPRESENTAÇÃO VETORIAL
        │
        ▼
MÉTRICA DE SIMILARIDADE
        │
        ▼
LIMIAR DE COMPATIBILIDADE τ
        │
        ▼
BUSCA DE CANDIDATOS
        │
        ▼
POTENCIAL DE DESCOBERTA
        │
        ▼
RANKING
        │
        ▼
INTERPOLAÇÃO VETORIAL
        │
        ▼
GERAÇÃO DA BRIDGE
        │
        ▼
AVALIAÇÃO
        │
        ▼
API / APLICAÇÃO
```

---

## 17. Especificação Algorítmica

Esta seção traduz a formulação matemática das seções anteriores em decisões concretas de implementação.

### 17.1 Visão geral do pipeline algorítmico

| Etapa | Algoritmo escolhido | Justificativa |
|---|---|---|
| Normalização de escala | Min-Max ou Z-score | Evita que `tempo` (BPM, 0–240) domine `valence` (0–1) no cálculo de distância |
| Redução de dimensionalidade | PCA (opcional) | Corrige a correlação observada entre variáveis (ex.: Energy ↔ Loudness) sem o custo de uma distância de Mahalanobis |
| Representação vetorial | Vetor de features normalizado $\mathbf{x} \in \mathbb{R}^n$ | Base para todo o cálculo de $S(x,A)$ |
| Métrica de similaridade | Similaridade de cosseno | Robusta a diferenças de escala residuais; equivalente a produto interno após normalização L2 |
| Busca de vizinhos / candidatos | **FAISS** (`IndexFlatIP` ou `IndexIVFFlat`) | Mantém latência de consulta abaixo de 100ms mesmo com atualizações no índice; mais flexível que Annoy para catálogos que crescem |
| Filtro de compatibilidade | $\mathcal{C} = \{x \mid S(x,A) \geq \tau\}$ | Implementado como filtro pós-busca sobre os $k$ vizinhos retornados pelo FAISS |
| Interpolação da Bridge | Interpolação linear $\mathbf{x}(t) = (1-t)\mathbf{x}_A + t\mathbf{x}_B$ | Simples, interpretável e suficiente para o MVP; Bézier/Autoencoder ficam como evolução futura, quando houver dados suficientes para treinar |
| Ranking / pontuação | $Score(x) = \alpha S(x,A) + (1-\alpha)D(x)$ | Já formalizado nas Seções 7–10; permite ajuste direto do trade-off via $\alpha$ |
| Mecanismo anti-repetição | **MMR** (Maximal Marginal Relevance) | Evita recomendar repetidamente as mesmas faixas "ponte" em sessões sucessivas |

### 17.2 Normalização

Cada componente do vetor $\mathbf{x}$ é normalizado antes do cálculo de similaridade. A normalização Min-Max é definida como:

$$x_i' = \frac{x_i - \min(x_i)}{\max(x_i) - \min(x_i)}$$

trazendo cada variável para o intervalo $[0,1]$ e resolvendo a questão em aberto levantada na Seção 2.

### 17.3 Cálculo de $S(x,A)$

Após a normalização (e normalização L2 do vetor), $S(x,A)$ é calculado como o produto interno entre os vetores normalizados, equivalente à similaridade de cosseno:

$$S(x, A) = \frac{x \cdot A}{\|x\| \|A\|}$$
### 17.4 Algoritmo de busca de candidatos (pseudocódigo)

```
função buscar_candidatos(A, k, τ):
    vetor_A ← normalizar(A)
    similaridades, indices ← indice_FAISS.buscar(vetor_A, k)
    candidatos ← [x para x em indices se similaridade(x) ≥ τ]
    retornar candidatos
```

### 17.5 Algoritmo de ranking (pseudocódigo)

```
função rankear(candidatos, α):
    para cada x em candidatos:
        D(x) ← 1 - P(x)
        Score(x) ← α · S(x,A) + (1-α) · D(x)
    retornar candidatos ordenados por Score decrescente
```

### 17.6 Algoritmo de geração da Bridge (pseudocódigo)

```
função gerar_bridge(A, B, n_pontos, k, τ, α):
    trajetoria ← []
    para t em linspace(0, 1, n_pontos):
        x_t ← (1-t) · A + t · B
        candidatos_t ← buscar_candidatos(x_t, k, τ)
        ranking_t ← rankear(candidatos_t, α)
        trajetoria.adicionar(ranking_t[0])  # melhor candidata no ponto t
    retornar trajetoria
```

### 17.7 Complexidade e escalabilidade

- Para o dataset atual (~80 mil faixas), `IndexFlatIP` (busca exaustiva) já atende ao requisito de latência sub-100ms.
- Caso o catálogo cresça para a ordem de milhões de faixas, a migração para `IndexIVFFlat` ou `IndexHNSWFlat` é recomendada, trocando exatidão marginal por ganho de velocidade.

---

## 18. Status de Especificação

Esta documentação representa a formulação conceitual, matemática e algorítmica do Vibe Bridge. Os parâmetros, funções e estratégias apresentados constituem hipóteses de modelagem que deverão ser implementadas, testadas e avaliadas empiricamente nas próximas etapas do projeto.

# 🎵 Vibe Bridge — O Tradutor de Vibes para o Spotify

> **Ponte de Descoberta Musical por Interpolacao em Espaço Multidimensional**

---

## 📌 O Problema
O **Spotify Blend** limita-se a intercalar faixas de dois perfis distintos, gerando transições caóticas (ex.: Pop acústico sucedido por Heavy Metal) e elevadas taxas de rejeição (*skip rate*).

## 💡 A Solução: Vibe Bridge
O **Vibe Bridge** atua como um "roteador de áudio" que calcula a distância matemática entre os gostos dos usuários para construir uma jornada sonora gradativa. 

### 🚀 O Diferencial Inédito (Long Tail)
Conecta dois extremos musicais utilizando faixas do **Long Tail** (artistas independentes com `popularity < 30`) que possuem os atributos acústicos exatos (`valence`, `energy`, `tempo`, `danceability`) para servirem de "ponte" de transição.

---

## 🎯 Impacto e Proposta de Valor

| Para o Usuário | Para a Plataforma (Spotify) |
| :--- | :--- |
| **Experiência Fluida:** Fim das quebras bruscas de clima em viagens, festas e treinos em dupla. | **Retenção de Sessão:** Aumento do tempo de reprodução contínua em ambientes sociais. |
| **Descoberta Relevante:** Conexão com faixas independentes que representam a "metade do caminho" entre os gostos. | **Eficiência Financeira:** Desvio de tráfego para a base da pirâmide musical, reduzindo a dependência de royalties de *megahits*. |

---

## 🛠️ Arquitetura e Funcionamento do Algoritmo

1. **Interpolação Vetorial de Atributos:** Mapeamento do Ponto A (Usuário 1) e Ponto B (Usuário 2) em um vetor de atributos contínuos ($Energy$, $Valence$, $Danceability$, $Tempo$).
2. **Controle de Dosagem (UI Slider):**
   * **`0%` (Direto):** Blend tradicional (intercala hits conhecidos sem amortecimento).
   * **`50%` (Transição Suave):** Insere faixas intermediárias de média popularidade.
   * **`100%` (Ponte de Descoberta):** Aplica o filtro Long Tail (`popularity < 30/100`) para preencher os nós do vetor.

---

## 📊 Análise Exploratória do Dataset

Com base no processamento do arquivo `dataset_tratado.csv` (**80.583 faixas** do Spotify distribuídas em **113 gêneros**):

| Métrica | Popularity | Danceability | Energy | Loudness (dB) | Valence | Tempo (BPM) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Média** | 34,75 | 0,56 | 0,64 | -8,56 | 0,46 | 122,21 |
| **Desvio Padrão** | 19,45 | 0,18 | 0,26 | 5,26 | 0,26 | 30,07 |
| **Mediana (50%)**| 35,00 | 0,57 | 0,68 | -7,25 | 0,45 | 122,05 |

### Principais Correlações Identificadas
* **Energia vs. Loudness ($r = 0.76$):** Forte correlação positiva. Faixas com maior nível energético exigem equalização de volume no momento da transição.
* **Dançabilidade vs. Valência ($r = 0.49$):** Músicas mais dançáveis tendem a apresentar tom emocional mais positivo.

---

## 🔍 Guiding Questions (Questões Investigáveis)

### 1. Dados
* **GQ 1 (Métrica de Similaridade):** Qual métrica de distância (Cosseno vs. Euclidiana) nas variáveis `energy`, `valence`, `danceability`, `tempo` e `acousticness` gera menor variância nas transições entre gêneros distantes?
* **GQ 2 (Filtro Long Tail):** Como isolar faixas de artistas independentes (`popularity < 30`) eliminando ruídos/vinhetas? (*Corte: `duration_ms > 60000` e coerência de danceability*).
* **GQ 3 (Deduplicação):** Como a remoção das faixas duplicadas afeta a densidade dos nós de transição do espaço vetorial?

### 2. Usuário
* **GQ 1 (Validação de Transição):** A ordenação por menor distância vetorial reduz a taxa de *skip* durante atividades de foco?
* **GQ 2 (Controle de Dosagem):** Como a variação do *slider* (0%, 50%, 100%) altera o percentual de descoberta de artistas independentes?
* **GQ 3 (Transparência):** A presença de um sinalizador visual (badge "Ponte de Descoberta") reduz a rejeição imediata da faixa desconhecida?

### 3. Modelo
* **GQ 1 (Mecanismo Anti-Loop):** Como introduzir amostragem probabilística (Top-$K$ Nucleus) e penalidade temporal de histórico para evitar loops sem perder a vibe?
  * *Função de Ranking:* $Score = \text{Similaridade} + \beta \cdot (1 - \text{Popularidade}) - \text{PenalidadeHistorico}$
* **GQ 2 (Otimização de Sequência):** Qual algoritmo (K-NN com amostragem vs. Curvas Bézier em Autoencoders) minimiza o gradiente de variação de energia em playlists longas?
* **GQ 3 (Métricas Offline):** Qual métrica avalia o equilíbrio entre fluidez de áudio e promoção de artistas independentes?

### 4. Produção
* **GQ 1 (Latência Vetorial):** Qual biblioteca (FAISS vs. Annoy) mantém o tempo de consulta da faixa "ponte" abaixo de 100ms para a base do catálogo?
* **GQ 2 (Estratégia de Processamento):** A reordenação deve ocorrer em lote (*batch*) no salvamento ou via *edge workers* durante a reprodução?
* **GQ 3 (Prefetching):** Como estruturar o *buffer* de áudio para evitar pausas antes da transição? (*Gatilho: 70% de reprodução da faixa atual*).

### 5. Ética, Governança e LGPD
* **GQ 1 (Equidade no Long Tail):** Avaliação da distribuição de recomendações via Coeficiente de Gini entre artistas independentes.
* **GQ 2 (Anti-Manipulação):** Trava algorítmica exigindo taxa mínima de salvamento por reprodução para evitar faixas sintéticas/fazendas de cliques.
* **GQ 3 (Restrição Explícita):** Garantia de cumprimento do filtro `explicit == False` durante a busca de vizinhos.

#### 🛡️ Conformidade LGPD
* **Classificação de Dados:**
  * *Propriedades do Áudio* (`energy`, `valence`, `tempo`): Dados técnicos objetivos (não associados a pessoas físicas).
  * *Dados Comportamentais* (histórico de escuta, *skips*, playlists): Dados Pessoais Comuns (Art. 5º, I).
* **Base Legal:** Legítimo Interesse (Art. 7º, IX) suportado por RIPD (Relatório de Impacto à Proteção de Dados) e Teste de Proporcionalidade.
* **Direitos do Titular:** Explicação da lógica automatizada de recomendação (Art. 20), acesso ao histórico e direito à anonimização/exclusão.

---

## 💻 Como Executar o Projeto Localmente

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/vibe-bridge.git](https://github.com/SEU_USUARIO/vibe-bridge.git)
   cd vibe-bridge

## 📚 Especificação Técnica
* Para conferir a formulação matemática, o modelo vetorial e os pseudocódigos do algoritmo, acesse a [Especificação Técnica Completa](./vibe-bridge-especificacao.md).

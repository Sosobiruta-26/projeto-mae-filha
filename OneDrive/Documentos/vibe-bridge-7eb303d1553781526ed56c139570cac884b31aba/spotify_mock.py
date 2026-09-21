from fastapi import FastAPI, HTTPException
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

app = FastAPI(title="Spotify API Mock & Recommendation Engine - Vibe Bridge")

# 1. Carrega e prepara os dados na inicialização do servidor
df = pd.read_csv("dataset_clean.csv")

# Seleciona as colunas acústicas numéricas usadas para calcular a similaridade
features_cols = ['danceability', 'energy', 'key', 'loudness', 'mode', 
                 'speechiness', 'acousticness', 'instrumentalness', 
                 'liveness', 'valence', 'tempo']

# Normaliza os dados para que nenhuma feature tenha peso desproporcional
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features_cols].fillna(0))

@app.get("/v1/search")
def mock_search(q: str, type: str = "track"):
    """Simula a busca de músicas por nome."""
    resultados = df[df['track_name'].str.contains(q, case=False, na=False)].head(10)
    
    tracks_json = []
    for idx, row in resultados.iterrows():
        tracks_json.append({
            "id": str(idx),
            "name": row['track_name'],
            "artists": [{"name": row.get('artists', 'Unknown Artist')}],
            "album": {"name": row.get('track_genre', 'Vibe Bridge Collection')},
            "external_urls": {"spotify": "https://spotify.com"}
        })
    
    return {"tracks": {"items": tracks_json}}

@app.get("/v1/audio-features/{track_id}")
def mock_audio_features(track_id: int):
    """Simula o retorno das características acústicas de uma música pelo ID (índice do DataFrame)."""
    try:
        row = df.loc[int(track_id)]
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Track not found")
        
    return {
        "danceability": float(row.get('danceability', 0.5)),
        "energy": float(row.get('energy', 0.5)),
        "key": int(row.get('key', 0)),
        "loudness": float(row.get('loudness', -10.0)),
        "mode": int(row.get('mode', 1)),
        "speechiness": float(row.get('speechiness', 0.05)),
        "acousticness": float(row.get('acousticness', 0.1)),
        "instrumentalness": float(row.get('instrumentalness', 0.0)),
        "liveness": float(row.get('liveness', 0.1)),
        "valence": float(row.get('valence', 0.5)),
        "tempo": float(row.get('tempo', 120.0))
    }

@app.get("/v1/recommendations")
def get_recommendations(seed_index: int, limit: int = 5):
    """
    Recebe o índice de uma música de referência (seed_index) 
    e retorna as músicas mais parecidas acusticamente usando similaridade de cosseno.
    """
    if seed_index < 0 or seed_index >= len(df):
        raise HTTPException(status_code=404, detail="Seed track index not found in dataset.")
    
    # Pega o vetor da música escolhida
    seed_vector = X_scaled[seed_index].reshape(1, -1)
    
    # Calcula a similaridade entre a música seed e todas as outras da base
    similarities = cosine_similarity(seed_vector, X_scaled)[0]
    
    # Ordena da mais similar para a menos similar
    indices_ordenados = similarities.argsort()[::-1]
    
    # Remove o próprio índice da música seed da lista de recomendações
    indices_recomendados = [idx for idx in indices_ordenados if idx != seed_index][:limit]
    
    # Monta a resposta no formato estruturado
    recommended_tracks = []
    for idx in indices_recomendados:
        row = df.loc[idx]
        recommended_tracks.append({
            "id": str(idx),
            "name": row['track_name'],
            "artists": [{"name": row.get('artists', 'Unknown Artist')}],
            "similarity_score": float(similarities[idx]),
            "album": {"name": row.get('track_genre', 'Vibe Bridge Collection')}
        })
        
    seed_row = df.loc[seed_index]
    return {
        "seed_track": {
            "id": str(seed_index),
            "name": seed_row['track_name'],
            "artists": seed_row.get('artists', 'Unknown Artist')
        },
        "tracks": recommended_tracks
    }
import time
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyClientCredentials


# ============================================================
# CONFIGURAÇÃO / AUTENTICAÇÃO
# ============================================================

@st.cache_resource
def get_spotify_client():
    try:
        client_id = st.secrets["SPOTIPY_CLIENT_ID"].strip()
        client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"].strip()

        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )

        return spotipy.Spotify(auth_manager=auth_manager)

    except Exception as e:
        st.error(f"Erro na autenticação com o Spotify: {e}")
        return None

sp = get_spotify_client()


# ============================================================
# MOTOR DE RECOMENDAÇÃO ESTÁTICO (Dataset + Similaridade de Cosseno)
# ============================================================

class StaticRecommender:
    def __init__(self, csv_path="dataset.csv"):
        self.df = None
        self.scaler = StandardScaler()
        self.scaled_matrix = None
        self.feature_columns = [
            'danceability', 'energy', 'key', 'loudness', 
            'mode', 'speechiness', 'acousticness', 
            'instrumentalness', 'liveness', 'valence', 'tempo'
        ]
        try:
            self.load_data(csv_path)
        except Exception:
            pass

    def load_data(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df = self.df.dropna(subset=self.feature_columns)
        scaled_features = self.scaler.fit_transform(self.df[self.feature_columns])
        self.scaled_matrix = scaled_features

    def recomendar_por_similaridade(self, track_name_seed, artist_seed, limit=5):
        if self.df is None or self.df.empty or self.scaled_matrix is None:
            return []

        # Tenta encontrar correspondência exata (track_name + artists)
        match = self.df[
            (self.df['track_name'].str.lower() == track_name_seed.lower()) & 
            (self.df['artists'].str.lower().str.contains(artist_seed.lower()))
        ]

        if match.empty:
            # Fallback: busca pelo menos pelo artista
            match = self.df[self.df['artists'].str.lower().str.contains(artist_seed.lower())]
            if match.empty:
                return []

        seed_index = match.index[0]
        seed_vector = self.scaled_matrix[seed_index].reshape(1, -1)

        # Calcula Similaridade de Cosseno
        similarities = cosine_similarity(seed_vector, self.scaled_matrix).flatten()

        temp_df = self.df.copy()
        temp_df['similarity_score'] = similarities
        temp_df = temp_df.drop(seed_index)

        recomendados = temp_df.sort_values(by='similarity_score', ascending=False).head(limit * 2)

        tracks_formatadas = []
        for _, row in recomendados.iterrows():
            tracks_formatadas.append({
                'name': row['track_name'],
                'artists': [{'name': row['artists']}],
                'external_urls': {'spotify': '#'},
                'preview_url': None,
                'similarity_score': round(float(row['similarity_score']), 2)
            })

        return tracks_formatadas

@st.cache_resource
def get_static_recommender():
    return StaticRecommender("dataset.csv")

static_rec = get_static_recommender()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def normalizar_texto(texto):
    if not texto:
        return ""
    return " ".join(texto.strip().lower().split())

def formatar_track(track, similarity_score=0.0):
    return {
        "id": track.get("id"),
        "name": track.get("name"),
        "artists": track.get("artists", []),
        "external_urls": track.get("external_urls", {}),
        "preview_url": track.get("preview_url"),
        "popularity": track.get("popularity", 0),
        "similarity_score": similarity_score
    }


# ============================================================
# BUSCA DE MÚSICAS E ARTISTAS
# ============================================================

def buscar_musica(q, limit=10):
    if not sp:
        return {"tracks": {"items": []}}

    limit = max(1, min(limit, 10))

    try:
        return sp.search(q=q, limit=limit, type="track")
    except Exception:
        st.warning("Instabilidade na busca. Tentando novamente...")
        time.sleep(1)
        try:
            return sp.search(q=q, limit=limit, type="track")
        except Exception:
            return {"tracks": {"items": []}}

def obter_musica(track_id):
    if not sp:
        return None
    try:
        return sp.track(track_id)
    except Exception as e:
        st.warning(f"Não foi possível obter a música: {e}")
        return None


# ============================================================
# RECOMENDAÇÕES HÍBRIDAS (Dataset Estático + Spotify API)
# ============================================================

def obter_recomendacoes(seed_track_id, limit=5, **kwargs):
    if not sp:
        return None

    try:
        seed_track = obter_musica(seed_track_id)
        if not seed_track:
            st.error("Não foi possível encontrar a música de referência.")
            return None

        seed_name = seed_track["name"]
        seed_artist = seed_track["artists"][0]["name"]

        # 1. Obtém recomendações calculadas pelo dataset estático via Cosseno
        recomendacoes_estaticas = static_rec.recomendar_por_similaridade(
            track_name_seed=seed_name,
            artist_seed=seed_artist,
            limit=limit
        )

        tracks_finais = []

        # 2. Enriquece as recomendações estáticas buscando IDs e capas reais no Spotify
        if recomendacoes_estaticas:
            for item in recomendacoes_estaticas:
                query_busca = f"track:{item['name']} artist:{item['artists'][0]['name']}"
                res = buscar_musica(query_busca, limit=1)
                items_sp = res.get("tracks", {}).get("items", [])

                if items_sp:
                    track_real = items_sp[0]
                    if track_real["id"] != seed_track_id:
                        tracks_finais.append(
                            formatar_track(track_real, similarity_score=item['similarity_score'])
                        )
                else:
                    tracks_finais.append(item)

                if len(tracks_finais) >= limit:
                    break

        # 3. Fallback caso o dataset não encontre exato
        if not tracks_finais:
            res_fallback = buscar_musica(f"artist:{seed_artist}", limit=limit + 1)
            for item in res_fallback.get("tracks", {}).get("items", []):
                if item["id"] != seed_track_id:
                    tracks_finais.append(formatar_track(item, similarity_score=0.85))
                if len(tracks_finais) >= limit:
                    break

        return {
            "seed_track": seed_track,
            "tracks": tracks_finais[:limit]
        }

    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {e}")
        return None
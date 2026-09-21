import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


class StaticRecommender:
    def __init__(self, csv_path="dataset.csv"):
        """Inicializa o recomendador estático carregando o dataset e

        preparando as features acústicas para cálculo de similaridade.
        """
        self.df = None
        self.scaler = StandardScaler()
        self.scaled_matrix = None
        self.feature_columns = [
            "danceability",
            "energy",
            "key",
            "loudness",
            "mode",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
        ]

        try:
            self.load_data(csv_path)
        except Exception:
            pass

    def load_data(self, csv_path):
        self.df = pd.read_csv(csv_path)
        # Remove valores nulos nas colunas essenciais
        self.df = self.df.dropna(subset=self.feature_columns)

        # Normaliza as features para que nenhuma tenha peso desproporcional
        scaled_features = self.scaler.fit_transform(
            self.df[self.feature_columns]
        )
        self.scaled_matrix = scaled_features

    def recomendar_por_similaridade(self, track_name_seed, artist_seed, limit=5):
        """Calcula a similaridade de cosseno entre a música seed e as demais do dataset."""
        if self.df is None or self.df.empty or self.scaled_matrix is None:
            return []

        # Tenta encontrar a música seed no dataset usando 'track_name'
        match = self.df[
            (self.df["track_name"].str.lower() == track_name_seed.lower())
            & (
                self.df["artists"]
                .str.lower()
                .str.contains(artist_seed.lower())
            )
        ]

        if match.empty:
            # Fallback: pega pelo menos pelo artista
            match = self.df[
                self.df["artists"].str.lower().str.contains(artist_seed.lower())
            ]
            if match.empty:
                return []

        seed_index = match.index[0]
        seed_vector = self.scaled_matrix[seed_index].reshape(1, -1)

        # Calcula a similaridade de cosseno
        similarities = cosine_similarity(
            seed_vector, self.scaled_matrix
        ).flatten()

        temp_df = self.df.copy()
        temp_df["similarity_score"] = similarities

        # Remove a própria música seed dos resultados
        temp_df = temp_df.drop(seed_index)

        # Ordena da maior para a menor similaridade
        recomendados = temp_df.sort_values(
            by="similarity_score", ascending=False
        ).head(limit)

        tracks_formatadas = []
        for _, row in recomendados.iterrows():
            tracks_formatadas.append(
                {
                    "name": row["track_name"],
                    "artists": [{"name": row["artists"]}],
                    "external_urls": {"spotify": row.get("external_url", "#")},
                    "preview_url": row.get("preview_url", None),
                    "similarity_score": round(
                        float(row["similarity_score"]), 2
                    ),
                }
            )

        return tracks_formatadas
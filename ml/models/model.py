import os
import json
import numpy as np
import torch
import faiss

from PIL import Image
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import clip


# =========================
# PATH CONFIG
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")


# =========================
# LOAD MODELS
device = "cuda" if torch.cuda.is_available() else "cpu"

clip_model, preprocess = clip.load("ViT-B/32", device=device)
text_model = SentenceTransformer('all-MiniLM-L6-v2')


# =========================
# LOAD METADATA
with open(METADATA_PATH, "r") as f:
    items = json.load(f)


# =========================
# EMBEDDING FUNCTIONS
def get_image_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    image = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        emb = clip_model.encode_image(image)

    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy()[0]


def get_text_embedding(text):
    return text_model.encode(text, normalize_embeddings=True)


# =========================
# SIMILARITY
def similarity(vec1, vec2):
    vec1 = vec1.reshape(1, -1)
    vec2 = vec2.reshape(1, -1)
    return cosine_similarity(vec1, vec2)[0][0]


def final_score(img_sim, text_sim):
    return 0.7 * img_sim + 0.3 * text_sim


# =========================
# MATCHING ENGINE
def find_matches(query_img_path, query_text, category=None, top_k=5):
    results = []

    query_img_emb = get_image_embedding(query_img_path)
    query_text_emb = get_text_embedding(query_text)

    for item in items:
        if category and item.get("category", item["text"]) != category:
            continue

        img_path = os.path.join(IMAGE_DIR, item["image"])

        try:
            img_emb = get_image_embedding(img_path)
            text_emb = get_text_embedding(item["text"])

            img_sim = similarity(query_img_emb, img_emb)
            text_sim = similarity(query_text_emb, text_emb)

            score = final_score(img_sim, text_sim)

            results.append({
                "image": item["image"],
                "score": float(score)
            })

        except Exception as e:
            print("Skipping:", img_path)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# =========================
# PRECOMPUTE EMBEDDINGS
def precompute_embeddings():
    image_embeddings = []
    image_paths = []

    for item in items:
        img_path = os.path.join(IMAGE_DIR, item["image"])

        try:
            emb = get_image_embedding(img_path)
            image_embeddings.append(emb)
            image_paths.append(item["image"])
        except:
            continue

    image_embeddings = np.array(image_embeddings)

    np.save(os.path.join(DATA_DIR, "image_embeddings.npy"), image_embeddings)
    np.save(os.path.join(DATA_DIR, "image_paths.npy"), image_paths)

    print("Embeddings saved!")


# =========================
# BUILD FAISS INDEX
def build_faiss_index():
    emb_path = os.path.join(DATA_DIR, "image_embeddings.npy")
    embeddings = np.load(emb_path)

    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(DATA_DIR, "faiss_index.bin"))

    print(" FAISS index built!")


# =========================
# FAISS SEARCH
def faiss_search(query_img_path, top_k=5):
    index_path = os.path.join(DATA_DIR, "faiss_index.bin")
    paths_path = os.path.join(DATA_DIR, "image_paths.npy")

    index = faiss.read_index(index_path)
    image_paths = np.load(paths_path, allow_pickle=True)

    query_emb = get_image_embedding(query_img_path)

    D, I = index.search(query_emb.reshape(1, -1), top_k)

    results = []
    for idx in I[0]:
        results.append(image_paths[idx])

    return results


# =========================
# DISPLAY RESULTS
def show_results(results):
    for r in results:
        img_path = os.path.join(IMAGE_DIR, r["image"])
        img = Image.open(img_path)

        plt.imshow(img)
        plt.title(f"Score: {r['score']:.2f}")
        plt.axis("off")
        plt.show()


# =========================
# MAIN (TESTING)
if __name__ == "__main__":

    # query_image = os.path.join(IMAGE_DIR, "headphones/000006.jpg")
    query_image = r"D:\Lost_and_Found\ml\test_images\headphones1.jpg"

    results = find_matches(
        query_image,
        "headphones",
        category="headphones"
    )

    for r in results:
        print(r)

    show_results(results)
import os
import io
import base64
import torch
import numpy as np
from PIL import Image
from typing import List, Union
import clip
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class ImageFeatureExtractor:
    _instance = None
    _clip_model = None
    _clip_preprocess = None
    _text_model = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_models()
        return cls._instance
    
    def _load_models(self):
        """Load CLIP and SentenceTransformer models"""
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading models on device: {self._device}")
        
        # Load CLIP model
        self._clip_model, self._clip_preprocess = clip.load("ViT-B/32", device=self._device)
        
        # Load SentenceTransformer for text embeddings
        self._text_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Models loaded successfully!")
    
    def extract_image_features(self, image_data: bytes) -> List[float]:
        """
        Extract image features using CLIP ViT-B/32
        Returns a 512-dimensional feature vector
        """
        try:
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            image_tensor = self._clip_preprocess(image).unsqueeze(0).to(self._device)
            
            with torch.no_grad():
                features = self._clip_model.encode_image(image_tensor)
            
            # Normalize
            features = features / features.norm(dim=-1, keepdim=True)
            
            return features.cpu().numpy()[0].tolist()
        except Exception as e:
            print(f"Error extracting image features: {e}")
            return [0.0] * 512
    
    def extract_text_features(self, text: str) -> List[float]:
        """
        Extract text features using SentenceTransformer
        Returns a 384-dimensional feature vector
        """
        try:
            features = self._text_model.encode(text, normalize_embeddings=True)
            return features.tolist()
        except Exception as e:
            print(f"Error extracting text features: {e}")
            return [0.0] * 384
    
    def extract_features_from_base64(self, base64_string: str) -> List[float]:
        """Extract image features from base64 encoded image"""
        try:
            if "base64," in base64_string:
                base64_string = base64_string.split("base64,")[1]
            
            image_data = base64.b64decode(base64_string)
            return self.extract_image_features(image_data)
        except Exception as e:
            print(f"Error extracting features from base64: {e}")
            return [0.0] * 512
    
    def calculate_image_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two image vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        vec1_np = np.array(vec1).reshape(1, -1)
        vec2_np = np.array(vec2).reshape(1, -1)
        
        return float(cosine_similarity(vec1_np, vec2_np)[0][0])
    
    def calculate_text_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two text vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        vec1_np = np.array(vec1).reshape(1, -1)
        vec2_np = np.array(vec2).reshape(1, -1)
        
        return float(cosine_similarity(vec1_np, vec2_np)[0][0])
    
    def combined_similarity(self, img_vec1: List[float], text_vec1: str, 
                           img_vec2: List[float], text_vec2: str) -> float:
        """
        Calculate combined similarity using both image and text features
        Uses the same formula as the ML model: 0.6 * img_sim + 0.4 * text_sim
        """
        img_sim = self.calculate_image_similarity(img_vec1, img_vec2)
        
        text_vec1_emb = self.extract_text_features(text_vec1)
        text_vec2_emb = self.extract_text_features(text_vec2)
        text_sim = self.calculate_text_similarity(text_vec1_emb, text_vec2_emb)
        
        return 0.6 * img_sim + 0.4 * text_sim


def get_feature_extractor() -> ImageFeatureExtractor:
    """Get singleton instance of ImageFeatureExtractor"""
    return ImageFeatureExtractor()

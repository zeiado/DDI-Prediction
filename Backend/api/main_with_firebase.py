"""
FastAPI Backend with Firebase Firestore Integration
Provides REST API endpoints with cloud data storage
"""

from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from predict import DDIPredictor
from firebase_service import FirebaseService

# Initialize FastAPI app
app = FastAPI(
    title="DDI Predictor API with Firebase",
    description="AI-powered Drug-Drug Interaction Prediction API with Cloud Storage",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
predictor = None
firebase = None


@app.on_event("startup")
async def startup_event():
    """Load model and initialize Firebase on startup"""
    global predictor, firebase
    
    try:
        # Load ML model
        predictor = DDIPredictor(
            model_path='../models/deepddi_model.pt',
            preprocessor_path='../data/preprocessor.pkl',
            model_info_path='../models/model_info.json'
        )
        print("✅ ML Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
    
    try:
        # Initialize Firebase
        firebase = FirebaseService()
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"⚠️ Firebase initialization failed: {e}")
        print("⚠️ API will run without cloud storage")


# ==================== Pydantic Models ====================

class UserCreate(BaseModel):
    """Model for user creation"""
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")
    display_name: Optional[str] = Field(None, description="Display name")


class DrugPair(BaseModel):
    """Request model for drug pair"""
    drug_a: str = Field(..., description="First drug name or SMILES")
    drug_b: str = Field(..., description="Second drug name or SMILES")
    use_smiles: bool = Field(False, description="Whether inputs are SMILES strings")
    user_id: Optional[str] = Field(None, description="User ID for saving to history")
    
    @validator('drug_a', 'drug_b')
    def validate_drug(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Drug name/SMILES cannot be empty")
        return v.strip()


class InteractionResponse(BaseModel):
    """Response model for interaction prediction"""
    success: bool
    drug_pair: str
    interaction_exists: bool
    severity: str
    risk_score: float
    description: str
    mechanism: str
    recommendations: List[str]
    sources: List[str]
    timestamp: str
    probabilities: Optional[Dict[str, float]] = None
    confidence: Optional[str] = None
    interaction_id: Optional[str] = None  # Firestore document ID


class SearchResponse(BaseModel):
    """Response model for drug search"""
    success: bool
    results: List[str]
    count: int


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    online: bool
    model_loaded: bool
    firebase_connected: bool
    timestamp: str
    version: str


# ==================== Helper Functions ====================

def get_user_id_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from authorization header (simplified)"""
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return None


# ==================== API Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "DDI Predictor API with Firebase",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "AI-powered drug interaction prediction",
            "Cloud storage with Firebase Firestore",
            "User authentication",
            "Interaction history",
            "Real-time sync"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    firebase_connected = firebase is not None and firebase.test_connection()
    
    return HealthResponse(
        status="ok" if predictor and firebase_connected else "degraded",
        online=True,
        model_loaded=predictor is not None,
        firebase_connected=firebase_connected,
        timestamp=datetime.now().isoformat(),
        version="2.0.0"
    )


# ==================== User Management ====================

@app.post("/users/create", tags=["Users"])
async def create_user(user_data: UserCreate):
    """Create a new user"""
    if not firebase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not available"
        )
    
    try:
        user = firebase.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name
        )
        return {
            "success": True,
            "user": user,
            "message": "User created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/users/{user_id}", tags=["Users"])
async def get_user(user_id: str):
    """Get user information"""
    if not firebase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not available"
        )
    
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"success": True, "user": user}


# ==================== Drug Search ====================

@app.get("/search-drugs", response_model=SearchResponse, tags=["Drugs"])
async def search_drugs(q: str = ""):
    """Search for drugs in the database"""
    if not predictor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    if len(q.strip()) < 2:
        return SearchResponse(success=True, results=[], count=0)
    
    try:
        # Search in local drug database
        query_lower = q.lower()
        matches = [
            drug for drug in predictor.drug_to_smiles.keys()
            if query_lower in drug.lower()
        ]
        
        # Limit results
        matches = sorted(matches)[:20]
        
        return SearchResponse(
            success=True,
            results=matches,
            count=len(matches)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


# ==================== Interaction Prediction ====================

@app.post("/check-interaction", response_model=InteractionResponse, tags=["Prediction"])
async def check_interaction(drug_pair: DrugPair):
    """Check drug-drug interaction with optional cloud storage"""
    if not predictor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # Get prediction from ML model
        result = predictor.get_detailed_prediction(
            drug_pair.drug_a,
            drug_pair.drug_b,
            is_smiles=drug_pair.use_smiles
        )
        
        # Generate description and mechanism
        description, mechanism = _generate_interaction_info(
            result['predicted_class'],
            result['drug_pair']
        )
        
        # Prepare response
        response_data = {
            "success": True,
            "drug_pair": result['drug_pair'],
            "interaction_exists": result['interaction_exists'],
            "severity": result['severity'],
            "risk_score": result['risk_score'],
            "description": description,
            "mechanism": mechanism,
            "recommendations": result['recommendations'],
            "sources": _get_sources(),
            "timestamp": datetime.now().isoformat(),
            "probabilities": result['probabilities'],
            "confidence": result.get('confidence', 'Medium'),
            "interaction_id": None
        }
        
        # Save to Firebase if user is authenticated
        if firebase and drug_pair.user_id:
            try:
                interaction_data = {
                    'userId': drug_pair.user_id,
                    'drugA': drug_pair.drug_a,
                    'drugB': drug_pair.drug_b,
                    'severity': result['severity'],
                    'riskScore': result['risk_score'],
                    'description': description,
                    'mechanism': mechanism,
                    'recommendations': result['recommendations'],
                    'probabilities': result['probabilities'],
                    'confidence': result.get('confidence', 'Medium'),
                    'timestamp': datetime.now()
                }
                
                interaction_id = firebase.save_interaction(interaction_data)
                response_data['interaction_id'] = interaction_id
                
            except Exception as e:
                print(f"⚠️ Failed to save to Firebase: {e}")
        
        return InteractionResponse(**response_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


# ==================== History Management ====================

@app.get("/history/{user_id}", tags=["History"])
async def get_user_history(user_id: str, limit: int = 50):
    """Get user's interaction history from Firebase"""
    if not firebase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not available"
        )
    
    try:
        interactions = firebase.get_user_interactions(user_id, limit)
        return {
            "success": True,
            "interactions": interactions,
            "count": len(interactions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/history/{user_id}/{interaction_id}", tags=["History"])
async def delete_interaction(user_id: str, interaction_id: str):
    """Delete a specific interaction"""
    if not firebase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not available"
        )
    
    success = firebase.delete_interaction(interaction_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found or unauthorized"
        )
    
    return {"success": True, "message": "Interaction deleted"}


@app.delete("/history/{user_id}/clear", tags=["History"])
async def clear_history(user_id: str):
    """Clear all interactions for a user"""
    if not firebase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not available"
        )
    
    count = firebase.clear_user_history(user_id)
    return {
        "success": True,
        "message": f"Cleared {count} interactions",
        "count": count
    }


# ==================== Helper Functions ====================

def _generate_interaction_info(severity_class: str, drug_pair: str) -> tuple:
    """Generate description and mechanism based on severity"""
    descriptions = {
        'Severe': f"The combination of {drug_pair} has been identified as having a severe interaction risk. "
                  f"This combination may lead to serious adverse effects including increased toxicity, "
                  f"reduced therapeutic efficacy, or life-threatening complications. Immediate medical "
                  f"consultation is strongly recommended.",
        
        'Moderate': f"The combination of {drug_pair} shows a moderate interaction risk. "
                    f"This combination may result in altered drug effectiveness or increased side effects. "
                    f"Close monitoring and possible dose adjustments may be necessary. "
                    f"Consult your healthcare provider for guidance.",
        
        'None': f"The combination of {drug_pair} appears to have minimal interaction risk based on "
                f"current analysis. However, individual patient factors may vary. "
                f"Always follow prescribed dosages and consult your healthcare provider if you "
                f"experience any unusual symptoms."
    }
    
    mechanisms = {
        'Severe': "The drugs may interact through multiple pathways including pharmacokinetic interactions "
                  "(affecting absorption, distribution, metabolism, or excretion) and pharmacodynamic "
                  "interactions (affecting drug action at target sites). These interactions can lead to "
                  "synergistic toxicity or antagonistic therapeutic effects.",
        
        'Moderate': "The drugs may interact through shared metabolic pathways or have additive effects "
                    "on certain physiological systems. This can result in altered drug concentrations "
                    "or enhanced/reduced therapeutic or adverse effects.",
        
        'None': "Based on current pharmacological knowledge, these drugs do not appear to have "
                "significant interactions through common metabolic pathways or receptor systems. "
                "However, rare or individual-specific interactions cannot be completely ruled out."
    }
    
    return descriptions.get(severity_class, descriptions['Moderate']), \
           mechanisms.get(severity_class, mechanisms['Moderate'])


def _get_sources() -> List[str]:
    """Return list of data sources"""
    return [
        "DrugBank Database",
        "AI Model Prediction (DeepDDI)",
        "Pharmacological Literature",
        "Clinical Guidelines"
    ]


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 Starting DDI Predictor API with Firebase")
    print("="*60)
    print("📍 API: http://localhost:5000")
    print("📚 Docs: http://localhost:5000/docs")
    print("🔥 Firebase: Enabled")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info",
        access_log=True
    )

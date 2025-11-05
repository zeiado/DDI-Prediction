"""
FastAPI Backend for Drug-Drug Interaction Prediction
Provides REST API endpoints for the Flutter mobile app
"""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from predict import DDIPredictor

# Initialize FastAPI app
app = FastAPI(
    title="DDI Predictor API",
    description="AI-powered Drug-Drug Interaction Prediction API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor (loaded once at startup)
predictor = None

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global predictor
    try:
        predictor = DDIPredictor(
            model_path='../models/deepddi_model.pt',
            preprocessor_path='../data/preprocessor.pkl',
            model_info_path='../models/model_info.json'
        )
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("⚠️ API will run but predictions will fail")


# Pydantic models for request/response
class DrugPair(BaseModel):
    """Request model for drug pair"""
    drug_a: str = Field(..., description="First drug name or SMILES")
    drug_b: str = Field(..., description="Second drug name or SMILES")
    use_smiles: bool = Field(False, description="Whether inputs are SMILES strings")
    
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
    timestamp: str
    version: str


# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "DDI Predictor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns API status and model availability
    """
    return HealthResponse(
        status="ok",
        online=True,
        model_loaded=predictor is not None,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/search-drugs", response_model=SearchResponse, tags=["Drugs"])
async def search_drugs(q: str = ""):
    """
    Search for drugs in the database
    
    Args:
        q: Search query (drug name)
        
    Returns:
        List of matching drug names
    """
    if not predictor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    if len(q.strip()) < 2:
        return SearchResponse(success=True, results=[], count=0)
    
    try:
        # Search in drug database
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


@app.post("/check-interaction", response_model=InteractionResponse, tags=["Prediction"])
async def check_interaction(drug_pair: DrugPair):
    """
    Check drug-drug interaction
    
    Args:
        drug_pair: DrugPair object with two drugs
        
    Returns:
        Interaction prediction with risk assessment
    """
    if not predictor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please try again later."
        )
    
    try:
        # Get prediction
        result = predictor.get_detailed_prediction(
            drug_pair.drug_a,
            drug_pair.drug_b,
            is_smiles=drug_pair.use_smiles
        )
        
        # Generate description and mechanism based on severity
        description, mechanism = _generate_interaction_info(
            result['predicted_class'],
            result['drug_pair']
        )
        
        # Format response
        response = InteractionResponse(
            success=True,
            drug_pair=result['drug_pair'],
            interaction_exists=result['interaction_exists'],
            severity=result['severity'],
            risk_score=result['risk_score'],
            description=description,
            mechanism=mechanism,
            recommendations=result['recommendations'],
            sources=_get_sources(),
            timestamp=datetime.now().isoformat(),
            probabilities=result['probabilities'],
            confidence=result.get('confidence', 'Medium')
        )
        
        return response
        
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


@app.post("/predict-smiles", tags=["Prediction"])
async def predict_smiles(smiles1: str, smiles2: str):
    """
    Predict interaction from SMILES strings (alternative endpoint)
    
    Args:
        smiles1: SMILES of first drug
        smiles2: SMILES of second drug
        
    Returns:
        Prediction result
    """
    drug_pair = DrugPair(drug_a=smiles1, drug_b=smiles2, use_smiles=True)
    return await check_interaction(drug_pair)


# Helper functions

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


# Error handlers

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "path": str(request.url),
            "available_endpoints": ["/health", "/search-drugs", "/check-interaction"]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 Starting DDI Predictor API Server")
    print("="*60)
    print("📍 API will be available at: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000/docs")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info",
        access_log=True
    )

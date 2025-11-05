"""
Drug-Drug Interaction Prediction Module
Loads trained model and makes predictions with risk assessment
"""

import torch
import torch.nn.functional as F
import numpy as np
import pickle
import json
from rdkit import Chem
from rdkit.Chem import AllChem
from model_training import DeepDDI


class DDIPredictor:
    """Drug-Drug Interaction Predictor"""
    
    def __init__(self, model_path='../models/deepddi_model.pt', 
                 preprocessor_path='../data/preprocessor.pkl',
                 model_info_path='../models/model_info.json'):
        """
        Initialize predictor
        
        Args:
            model_path: Path to trained model weights
            preprocessor_path: Path to saved preprocessor
            model_info_path: Path to model info JSON
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model info
        with open(model_info_path, 'r') as f:
            self.model_info = json.load(f)
        
        # Load preprocessor
        with open(preprocessor_path, 'rb') as f:
            preprocessor_data = pickle.load(f)
            self.label_encoder = preprocessor_data['label_encoder']
            self.drug_to_smiles = preprocessor_data['drug_to_smiles']
            self.fingerprint_size = preprocessor_data['fingerprint_size']
            self.radius = preprocessor_data['radius']
        
        # Initialize model
        self.model = DeepDDI(
            input_dim=self.model_info['input_dim'],
            num_classes=self.model_info['num_classes']
        )
        
        # Load weights
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ Model loaded successfully on {self.device}")
        print(f"Classes: {self.model_info['classes']}")
    
    def smiles_to_fingerprint(self, smiles):
        """
        Convert SMILES to Morgan fingerprint
        
        Args:
            smiles: SMILES string
            
        Returns:
            numpy array of fingerprint
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise ValueError(f"Invalid SMILES: {smiles}")
            
            fp = AllChem.GetMorganFingerprintAsBitVect(
                mol, self.radius, nBits=self.fingerprint_size
            )
            
            arr = np.zeros((self.fingerprint_size,))
            Chem.DataStructs.ConvertToNumpyArray(fp, arr)
            
            return arr
        except Exception as e:
            raise ValueError(f"Error processing SMILES: {e}")
    
    def get_drug_smiles(self, drug_name):
        """
        Get SMILES for a drug by name
        
        Args:
            drug_name: Drug name or ID
            
        Returns:
            SMILES string
        """
        smiles = self.drug_to_smiles.get(drug_name)
        if smiles is None:
            raise ValueError(f"Drug '{drug_name}' not found in database")
        return smiles
    
    def predict_from_smiles(self, smiles1, smiles2):
        """
        Predict interaction from SMILES strings
        
        Args:
            smiles1: SMILES of first drug
            smiles2: SMILES of second drug
            
        Returns:
            dict with prediction results
        """
        # Convert to fingerprints
        fp1 = self.smiles_to_fingerprint(smiles1)
        fp2 = self.smiles_to_fingerprint(smiles2)
        
        # Concatenate
        combined_fp = np.concatenate([fp1, fp2])
        
        # Convert to tensor
        input_tensor = torch.FloatTensor(combined_fp).unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = F.softmax(output, dim=1).cpu().numpy()[0]
        
        # Get predicted class
        predicted_idx = np.argmax(probabilities)
        predicted_class = self.label_encoder.classes_[predicted_idx]
        
        # Create result dictionary
        result = {
            'probabilities': {},
            'predicted_class': predicted_class,
            'risk_score': float(probabilities[predicted_idx] * 10),  # Scale to 0-10
            'risk_message': self._get_risk_message(probabilities, predicted_class)
        }
        
        # Add individual probabilities
        for i, class_name in enumerate(self.label_encoder.classes_):
            result['probabilities'][class_name] = float(probabilities[i] * 100)
        
        return result
    
    def predict_from_names(self, drug1_name, drug2_name):
        """
        Predict interaction from drug names
        
        Args:
            drug1_name: Name of first drug
            drug2_name: Name of second drug
            
        Returns:
            dict with prediction results
        """
        # Get SMILES
        smiles1 = self.get_drug_smiles(drug1_name)
        smiles2 = self.get_drug_smiles(drug2_name)
        
        # Predict
        result = self.predict_from_smiles(smiles1, smiles2)
        result['drug_pair'] = f"{drug1_name} + {drug2_name}"
        
        return result
    
    def _get_risk_message(self, probabilities, predicted_class):
        """
        Generate human-readable risk message
        
        Args:
            probabilities: Array of class probabilities
            predicted_class: Predicted class name
            
        Returns:
            Risk message string
        """
        # Find indices for each severity level
        class_to_idx = {name: i for i, name in enumerate(self.label_encoder.classes_)}
        
        severe_prob = probabilities[class_to_idx.get('Severe', -1)] if 'Severe' in class_to_idx else 0
        moderate_prob = probabilities[class_to_idx.get('Moderate', -1)] if 'Moderate' in class_to_idx else 0
        none_prob = probabilities[class_to_idx.get('None', -1)] if 'None' in class_to_idx else 0
        
        # Generate message based on probabilities
        if severe_prob > 0.7:
            return "⚠️ Dangerous combination — avoid taking these drugs together. Consult your healthcare provider immediately."
        elif severe_prob > 0.5:
            return "⚠️ High risk of severe interaction — use extreme caution and medical supervision."
        elif moderate_prob > 0.6:
            return "⚠️ Moderate risk — use with caution. Monitor for side effects and consult healthcare provider."
        elif moderate_prob > 0.4:
            return "⚠️ Potential interaction — consider monitoring. Discuss with your healthcare provider."
        elif none_prob > 0.7:
            return "✅ Safe combination — no major interaction detected. Always follow prescribed dosages."
        else:
            return "ℹ️ Uncertain prediction — consult healthcare provider before combining these medications."
    
    def get_detailed_prediction(self, drug1, drug2, is_smiles=False):
        """
        Get detailed prediction with additional information
        
        Args:
            drug1: First drug (name or SMILES)
            drug2: Second drug (name or SMILES)
            is_smiles: Whether inputs are SMILES strings
            
        Returns:
            Detailed prediction dictionary
        """
        if is_smiles:
            result = self.predict_from_smiles(drug1, drug2)
            result['drug_pair'] = f"Drug A + Drug B"
        else:
            result = self.predict_from_names(drug1, drug2)
        
        # Add severity classification
        predicted_class = result['predicted_class']
        
        if predicted_class == 'Severe':
            result['severity'] = 'High'
            result['interaction_exists'] = True
        elif predicted_class == 'Moderate':
            result['severity'] = 'Moderate'
            result['interaction_exists'] = True
        else:
            result['severity'] = 'Low'
            result['interaction_exists'] = False
        
        # Add recommendations based on severity
        result['recommendations'] = self._get_recommendations(predicted_class)
        
        # Add confidence level
        max_prob = max(result['probabilities'].values())
        if max_prob > 80:
            result['confidence'] = 'High'
        elif max_prob > 60:
            result['confidence'] = 'Medium'
        else:
            result['confidence'] = 'Low'
        
        return result
    
    def _get_recommendations(self, severity_class):
        """Generate recommendations based on severity"""
        recommendations = {
            'Severe': [
                'Avoid this drug combination if possible',
                'Consult your healthcare provider immediately',
                'Do not start or stop medications without medical supervision',
                'Monitor for serious adverse effects',
                'Consider alternative medications'
            ],
            'Moderate': [
                'Use this combination with caution',
                'Monitor for side effects regularly',
                'Inform your healthcare provider about all medications',
                'Follow prescribed dosages carefully',
                'Report any unusual symptoms immediately'
            ],
            'None': [
                'This combination appears safe',
                'Continue following prescribed dosages',
                'Maintain regular check-ups with your healthcare provider',
                'Report any unexpected side effects'
            ]
        }
        
        return recommendations.get(severity_class, recommendations['Moderate'])


def predict_interaction(smiles1, smiles2):
    """
    Convenience function for API use
    
    Args:
        smiles1: SMILES of first drug
        smiles2: SMILES of second drug
        
    Returns:
        Prediction result dictionary
    """
    predictor = DDIPredictor()
    return predictor.get_detailed_prediction(smiles1, smiles2, is_smiles=True)


def main():
    """Example usage"""
    print("="*60)
    print("Drug-Drug Interaction Predictor - Test")
    print("="*60)
    
    # Initialize predictor
    predictor = DDIPredictor()
    
    # Example 1: Predict from drug names
    print("\n📊 Example 1: Prediction from drug names")
    print("-"*60)
    try:
        result = predictor.get_detailed_prediction("Warfarin", "Aspirin", is_smiles=False)
        print(f"\nDrug Pair: {result['drug_pair']}")
        print(f"Predicted Class: {result['predicted_class']}")
        print(f"Severity: {result['severity']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Risk Score: {result['risk_score']:.2f}/10")
        print(f"\nProbabilities:")
        for class_name, prob in result['probabilities'].items():
            print(f"  {class_name}: {prob:.2f}%")
        print(f"\nRisk Message: {result['risk_message']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Predict from SMILES
    print("\n\n📊 Example 2: Prediction from SMILES")
    print("-"*60)
    aspirin_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    warfarin_smiles = "CC(=O)CC(C1=CC=CC=C1)C2=C(C3=CC=CC=C3OC2=O)O"
    
    try:
        result = predictor.get_detailed_prediction(aspirin_smiles, warfarin_smiles, is_smiles=True)
        print(f"\nPredicted Class: {result['predicted_class']}")
        print(f"Severity: {result['severity']}")
        print(f"Risk Score: {result['risk_score']:.2f}/10")
        print(f"\nProbabilities:")
        for class_name, prob in result['probabilities'].items():
            print(f"  {class_name}: {prob:.2f}%")
        print(f"\nRisk Message: {result['risk_message']}")
        print(f"\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

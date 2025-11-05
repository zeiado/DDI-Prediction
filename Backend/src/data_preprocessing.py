"""
Data Preprocessing Module for Drug-Drug Interaction Prediction
Converts drug SMILES to molecular fingerprints and prepares training data
"""

import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os
from tqdm import tqdm

class DrugDataPreprocessor:
    def __init__(self, fingerprint_size=2048, radius=2):
        """
        Initialize preprocessor
        
        Args:
            fingerprint_size: Size of Morgan fingerprint (default: 2048)
            radius: Radius for Morgan fingerprint (default: 2)
        """
        self.fingerprint_size = fingerprint_size
        self.radius = radius
        self.label_encoder = LabelEncoder()
        self.drug_to_smiles = {}
        self.fingerprint_cache = {}
        
    def smiles_to_fingerprint(self, smiles):
        """
        Convert SMILES string to Morgan fingerprint
        
        Args:
            smiles: SMILES string representation of molecule
            
        Returns:
            numpy array of fingerprint bits
        """
        if smiles in self.fingerprint_cache:
            return self.fingerprint_cache[smiles]
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return np.zeros(self.fingerprint_size)
            
            # Generate Morgan fingerprint
            fp = AllChem.GetMorganFingerprintAsBitVect(
                mol, 
                self.radius, 
                nBits=self.fingerprint_size
            )
            
            # Convert to numpy array
            arr = np.zeros((self.fingerprint_size,))
            Chem.DataStructs.ConvertToNumpyArray(fp, arr)
            
            # Cache the result
            self.fingerprint_cache[smiles] = arr
            return arr
        except Exception as e:
            print(f"Error processing SMILES {smiles}: {e}")
            return np.zeros(self.fingerprint_size)
    
    def load_drug_smiles(self, smiles_file):
        """
        Load drug SMILES data from CSV
        
        Args:
            smiles_file: Path to CSV file with columns [Name, Drug name, Smiles]
        """
        print("Loading drug SMILES data...")
        df = pd.read_csv(smiles_file)
        
        # Create mapping from drug name to SMILES
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing drugs"):
            drug_name = row['Name']
            drug_id = row['Drug name']
            smiles = row['Smiles']
            
            # Store both name and ID mappings
            self.drug_to_smiles[drug_name] = smiles
            self.drug_to_smiles[drug_id] = smiles
        
        print(f"Loaded {len(self.drug_to_smiles)} drug entries")
    
    def classify_interaction_severity(self, description):
        """
        Classify interaction severity based on description keywords
        
        Args:
            description: Interaction description text
            
        Returns:
            severity level: 'Severe', 'Moderate', or 'None'
        """
        if pd.isna(description):
            return 'None'
        
        description_lower = description.lower()
        
        # Severe interaction keywords
        severe_keywords = [
            'contraindicated', 'avoid', 'dangerous', 'fatal', 'death',
            'severe', 'serious', 'life-threatening', 'toxic', 'toxicity',
            'hemorrhage', 'bleeding', 'cardiac arrest', 'respiratory',
            'seizure', 'coma', 'overdose'
        ]
        
        # Moderate interaction keywords
        moderate_keywords = [
            'caution', 'monitor', 'may increase', 'may decrease',
            'reduce', 'adjust', 'moderate', 'careful', 'watch',
            'consider', 'potential', 'risk', 'effect'
        ]
        
        # Check for severe interactions
        for keyword in severe_keywords:
            if keyword in description_lower:
                return 'Severe'
        
        # Check for moderate interactions
        for keyword in moderate_keywords:
            if keyword in description_lower:
                return 'Moderate'
        
        return 'None'
    
    def preprocess_data(self, interactions_file, smiles_file, test_size=0.2, random_state=42):
        """
        Main preprocessing pipeline
        
        Args:
            interactions_file: Path to drug interactions CSV
            smiles_file: Path to drug SMILES CSV
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
            
        Returns:
            X_train, X_test, y_train, y_test, label_encoder
        """
        # Load drug SMILES
        self.load_drug_smiles(smiles_file)
        
        # Load interactions
        print("\nLoading drug interactions...")
        interactions_df = pd.read_csv(interactions_file)
        print(f"Loaded {len(interactions_df)} interactions")
        
        # Prepare data
        X = []
        y = []
        skipped = 0
        
        print("\nProcessing drug pairs...")
        for idx, row in tqdm(interactions_df.iterrows(), total=len(interactions_df), desc="Creating fingerprints"):
            drug1 = row['Drug 1']
            drug2 = row['Drug 2']
            description = row['Interaction Description']
            
            # Get SMILES for both drugs
            smiles1 = self.drug_to_smiles.get(drug1)
            smiles2 = self.drug_to_smiles.get(drug2)
            
            if smiles1 is None or smiles2 is None:
                skipped += 1
                continue
            
            # Convert to fingerprints
            fp1 = self.smiles_to_fingerprint(smiles1)
            fp2 = self.smiles_to_fingerprint(smiles2)
            
            # Concatenate fingerprints
            combined_fp = np.concatenate([fp1, fp2])
            
            # Classify severity
            severity = self.classify_interaction_severity(description)
            
            X.append(combined_fp)
            y.append(severity)
        
        print(f"\nSkipped {skipped} interactions due to missing SMILES")
        print(f"Total valid interactions: {len(X)}")
        
        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Print class distribution
        print("\nClass distribution:")
        unique, counts = np.unique(y, return_counts=True)
        for label, count in zip(unique, counts):
            print(f"  {label}: {count} ({count/len(y)*100:.2f}%)")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, 
            test_size=test_size, 
            random_state=random_state,
            stratify=y_encoded
        )
        
        print(f"\nTraining set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test, self.label_encoder
    
    def save_preprocessor(self, filepath):
        """Save preprocessor state"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'label_encoder': self.label_encoder,
                'drug_to_smiles': self.drug_to_smiles,
                'fingerprint_size': self.fingerprint_size,
                'radius': self.radius
            }, f)
        print(f"Preprocessor saved to {filepath}")
    
    def load_preprocessor(self, filepath):
        """Load preprocessor state"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.label_encoder = data['label_encoder']
            self.drug_to_smiles = data['drug_to_smiles']
            self.fingerprint_size = data['fingerprint_size']
            self.radius = data['radius']
        print(f"Preprocessor loaded from {filepath}")


def main():
    """Example usage"""
    # Paths - Updated to correct location
    interactions_file = "../../model_data/db_drug_interactions.csv"
    smiles_file = "../../model_data/drug_info_combined.csv"
    
    # Create preprocessor
    preprocessor = DrugDataPreprocessor(fingerprint_size=2048, radius=2)
    
    # Preprocess data
    X_train, X_test, y_train, y_test, label_encoder = preprocessor.preprocess_data(
        interactions_file, 
        smiles_file
    )
    
    # Save preprocessed data
    os.makedirs('../data', exist_ok=True)
    np.save('../data/X_train.npy', X_train)
    np.save('../data/X_test.npy', X_test)
    np.save('../data/y_train.npy', y_train)
    np.save('../data/y_test.npy', y_test)
    
    # Save preprocessor
    preprocessor.save_preprocessor('../data/preprocessor.pkl')
    
    print("\n✅ Preprocessing complete!")
    print(f"Data saved to ../data/")


if __name__ == "__main__":
    main()

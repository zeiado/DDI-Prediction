"""
Memory-Optimized Data Preprocessing Module for Drug-Drug Interaction Prediction
Processes data in batches to avoid memory crashes
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
import gc

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
        """Convert SMILES string to Morgan fingerprint"""
        if smiles in self.fingerprint_cache:
            return self.fingerprint_cache[smiles]
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return np.zeros(self.fingerprint_size, dtype=np.float32)
            
            # Generate Morgan fingerprint
            fp = AllChem.GetMorganFingerprintAsBitVect(
                mol, 
                self.radius, 
                nBits=self.fingerprint_size
            )
            
            # Convert to numpy array (use float32 to save memory)
            arr = np.zeros((self.fingerprint_size,), dtype=np.float32)
            Chem.DataStructs.ConvertToNumpyArray(fp, arr)
            
            # Cache the result
            self.fingerprint_cache[smiles] = arr
            return arr
        except Exception as e:
            return np.zeros(self.fingerprint_size, dtype=np.float32)
    
    def load_drug_smiles(self, smiles_file):
        """Load drug SMILES data from CSV"""
        print("Loading drug SMILES data...")
        df = pd.read_csv(smiles_file)
        
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing drugs"):
            drug_name = row['Name']
            drug_id = row['Drug name']
            smiles = row['Smiles']
            
            self.drug_to_smiles[drug_name] = smiles
            self.drug_to_smiles[drug_id] = smiles
        
        print(f"Loaded {len(self.drug_to_smiles)} drug entries")
    
    def classify_interaction_severity(self, description):
        """Classify interaction severity based on description keywords"""
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
        
        for keyword in severe_keywords:
            if keyword in description_lower:
                return 'Severe'
        
        for keyword in moderate_keywords:
            if keyword in description_lower:
                return 'Moderate'
        
        return 'None'
    
    def preprocess_data_in_batches(self, interactions_file, smiles_file, 
                                   batch_size=10000, max_samples=50000,
                                   test_size=0.2, random_state=42):
        """
        Memory-efficient preprocessing with batching and sampling
        
        Args:
            interactions_file: Path to drug interactions CSV
            smiles_file: Path to drug SMILES CSV
            batch_size: Number of interactions to process at once
            max_samples: Maximum number of samples to use (to prevent memory issues)
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility
        """
        # Load drug SMILES
        self.load_drug_smiles(smiles_file)
        
        # Load interactions in chunks
        print(f"\nLoading drug interactions (max {max_samples} samples)...")
        
        # First, count total interactions
        total_interactions = sum(1 for _ in open(interactions_file)) - 1  # -1 for header
        print(f"Total interactions in file: {total_interactions}")
        
        # Calculate sampling ratio if needed
        if total_interactions > max_samples:
            sample_ratio = max_samples / total_interactions
            print(f"Sampling {sample_ratio*100:.1f}% of data to prevent memory issues")
        else:
            sample_ratio = 1.0
            max_samples = total_interactions
        
        # Process in batches
        X_batches = []
        y_batches = []
        processed = 0
        skipped = 0
        
        print(f"\nProcessing up to {max_samples} interactions in batches...")
        
        for chunk in pd.read_csv(interactions_file, chunksize=batch_size):
            # Sample from chunk if needed
            if sample_ratio < 1.0:
                chunk = chunk.sample(frac=sample_ratio, random_state=random_state)
            
            X_batch = []
            y_batch = []
            
            for _, row in tqdm(chunk.iterrows(), total=len(chunk), 
                             desc=f"Batch {processed//batch_size + 1}", leave=False):
                drug1 = row['Drug 1']
                drug2 = row['Drug 2']
                description = row['Interaction Description']
                
                # Get SMILES
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
                
                X_batch.append(combined_fp)
                y_batch.append(severity)
                
                processed += 1
                
                # Stop if we've reached max_samples
                if processed >= max_samples:
                    break
            
            if X_batch:
                X_batches.append(np.array(X_batch, dtype=np.float32))
                y_batches.append(y_batch)
            
            # Clear cache periodically to save memory
            if len(self.fingerprint_cache) > 5000:
                print("  Clearing fingerprint cache to save memory...")
                self.fingerprint_cache.clear()
                gc.collect()
            
            if processed >= max_samples:
                break
        
        print(f"\nProcessed {processed} interactions")
        print(f"Skipped {skipped} interactions due to missing SMILES")
        
        # Combine all batches
        print("\nCombining batches...")
        X = np.vstack(X_batches)
        y = np.array([item for batch in y_batches for item in batch])
        
        # Clear memory
        del X_batches, y_batches
        gc.collect()
        
        # Encode labels
        print("Encoding labels...")
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Print class distribution
        print("\nClass distribution:")
        unique, counts = np.unique(y, return_counts=True)
        for label, count in zip(unique, counts):
            print(f"  {label}: {count} ({count/len(y)*100:.2f}%)")
        
        # Split data
        print("\nSplitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, 
            test_size=test_size, 
            random_state=random_state,
            stratify=y_encoded
        )
        
        print(f"Training set: {len(X_train)} samples")
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
    """Main preprocessing function with memory optimization"""
    # Paths
    interactions_file = "../../model_data/db_drug_interactions.csv"
    smiles_file = "../../model_data/drug_info_combined.csv"
    
    # Create preprocessor
    preprocessor = DrugDataPreprocessor(fingerprint_size=2048, radius=2)
    
    print("="*60)
    print("MEMORY-OPTIMIZED DATA PREPROCESSING")
    print("="*60)
    print("\nThis version processes data in batches to prevent crashes.")
    print("Using 50,000 samples (sufficient for good model performance)")
    print("="*60)
    
    # Preprocess data with memory optimization
    X_train, X_test, y_train, y_test, label_encoder = preprocessor.preprocess_data_in_batches(
        interactions_file, 
        smiles_file,
        batch_size=5000,      # Process 5000 at a time
        max_samples=50000     # Use 50k samples (prevents memory issues)
    )
    
    # Save preprocessed data
    print("\nSaving preprocessed data...")
    os.makedirs('../data', exist_ok=True)
    
    np.save('../data/X_train.npy', X_train)
    np.save('../data/X_test.npy', X_test)
    np.save('../data/y_train.npy', y_train)
    np.save('../data/y_test.npy', y_test)
    
    # Save preprocessor
    preprocessor.save_preprocessor('../data/preprocessor.pkl')
    
    print("\n" + "="*60)
    print("✅ PREPROCESSING COMPLETE!")
    print("="*60)
    print(f"Data saved to ../data/")
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Memory usage optimized for your system!")
    print("="*60)


if __name__ == "__main__":
    main()

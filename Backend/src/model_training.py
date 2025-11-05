"""
DeepDDI Model Training Module
Implements a deep neural network for drug-drug interaction prediction
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import seaborn as sns


class DrugInteractionDataset(Dataset):
    """PyTorch Dataset for drug interaction data"""
    
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class DeepDDI(nn.Module):
    """
    Deep Drug-Drug Interaction Neural Network
    Architecture: 4096 -> 512 -> 256 -> num_classes
    """
    
    def __init__(self, input_dim=4096, num_classes=3, dropout_rate=0.3):
        super(DeepDDI, self).__init__()
        
        self.network = nn.Sequential(
            # Layer 1
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            # Layer 2
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            # Layer 3
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            # Output layer
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        return self.network(x)


class DDIModelTrainer:
    """Trainer class for DeepDDI model"""
    
    def __init__(self, model, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
    
    def train_epoch(self, train_loader, criterion, optimizer):
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in tqdm(train_loader, desc="Training", leave=False):
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            
            # Zero gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self, val_loader, criterion):
        """Validate the model"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in tqdm(val_loader, desc="Validating", leave=False):
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        epoch_loss = running_loss / len(val_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(self, train_loader, val_loader, epochs=20, lr=0.001, patience=5):
        """
        Train the model
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of training epochs
            lr: Learning rate
            patience: Early stopping patience
        """
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=3
        )
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        print(f"\n{'='*60}")
        print(f"Starting training on {self.device}")
        print(f"{'='*60}\n")
        
        for epoch in range(epochs):
            print(f"Epoch {epoch+1}/{epochs}")
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader, criterion, optimizer)
            self.train_losses.append(train_loss)
            self.train_accuracies.append(train_acc)
            
            # Validate
            val_loss, val_acc = self.validate(val_loader, criterion)
            self.val_losses.append(val_loss)
            self.val_accuracies.append(val_acc)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
            print(f"  Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            print()
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), '../models/deepddi_best.pt')
                print("  ✅ Best model saved!")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"\n⚠️ Early stopping triggered after {epoch+1} epochs")
                    break
        
        print(f"\n{'='*60}")
        print("Training completed!")
        print(f"Best validation loss: {best_val_loss:.4f}")
        print(f"{'='*60}\n")
    
    def evaluate(self, test_loader, label_encoder):
        """Evaluate model on test set"""
        self.model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for inputs, labels in tqdm(test_loader, desc="Testing"):
                inputs = inputs.to(self.device)
                outputs = self.model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(all_labels, all_preds)
        
        print("\n" + "="*60)
        print("TEST SET EVALUATION")
        print("="*60)
        print(f"\nOverall Accuracy: {accuracy*100:.2f}%\n")
        
        # Classification report
        print("Classification Report:")
        print("-"*60)
        print(classification_report(
            all_labels, all_preds, 
            target_names=label_encoder.classes_,
            digits=4
        ))
        
        # Confusion matrix
        cm = confusion_matrix(all_labels, all_preds)
        self.plot_confusion_matrix(cm, label_encoder.classes_)
        
        return accuracy
    
    def plot_confusion_matrix(self, cm, classes):
        """Plot confusion matrix"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=classes, yticklabels=classes)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('../logs/confusion_matrix.png', dpi=300, bbox_inches='tight')
        print("\n✅ Confusion matrix saved to ../logs/confusion_matrix.png")
        plt.close()
    
    def plot_training_history(self):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Loss plot
        ax1.plot(self.train_losses, label='Train Loss', marker='o')
        ax1.plot(self.val_losses, label='Val Loss', marker='s')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Accuracy plot
        ax2.plot(self.train_accuracies, label='Train Accuracy', marker='o')
        ax2.plot(self.val_accuracies, label='Val Accuracy', marker='s')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.set_title('Training and Validation Accuracy')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../logs/training_history.png', dpi=300, bbox_inches='tight')
        print("✅ Training history saved to ../logs/training_history.png")
        plt.close()


def train_model():
    """Main training function"""
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load preprocessed data
    print("\nLoading preprocessed data...")
    X_train = np.load('../data/X_train.npy')
    X_test = np.load('../data/X_test.npy')
    y_train = np.load('../data/y_train.npy')
    y_test = np.load('../data/y_test.npy')
    
    # Load label encoder
    import pickle
    with open('../data/preprocessor.pkl', 'rb') as f:
        preprocessor_data = pickle.load(f)
        label_encoder = preprocessor_data['label_encoder']
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Number of classes: {len(label_encoder.classes_)}")
    print(f"Classes: {label_encoder.classes_}")
    
    # Create datasets and dataloaders
    train_dataset = DrugInteractionDataset(X_train, y_train)
    test_dataset = DrugInteractionDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False, num_workers=2)
    
    # Create model
    input_dim = X_train.shape[1]
    num_classes = len(label_encoder.classes_)
    
    model = DeepDDI(input_dim=input_dim, num_classes=num_classes, dropout_rate=0.3)
    
    print(f"\nModel Architecture:")
    print(model)
    print(f"\nTotal parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Create trainer
    trainer = DDIModelTrainer(model, device=device)
    
    # Train model
    trainer.train(
        train_loader=train_loader,
        val_loader=test_loader,
        epochs=30,
        lr=0.001,
        patience=7
    )
    
    # Plot training history
    trainer.plot_training_history()
    
    # Load best model and evaluate
    print("\nLoading best model for final evaluation...")
    model.load_state_dict(torch.load('../models/deepddi_best.pt'))
    trainer.model = model.to(device)
    
    # Evaluate
    accuracy = trainer.evaluate(test_loader, label_encoder)
    
    # Save final model
    torch.save(model.state_dict(), '../models/deepddi_model.pt')
    print("\n✅ Final model saved to ../models/deepddi_model.pt")
    
    # Save model info
    model_info = {
        'input_dim': input_dim,
        'num_classes': num_classes,
        'classes': label_encoder.classes_.tolist(),
        'accuracy': accuracy,
        'device': str(device)
    }
    
    import json
    with open('../models/model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"Model saved to: ../models/deepddi_model.pt")
    print(f"Best model saved to: ../models/deepddi_best.pt")
    print(f"Model info saved to: ../models/model_info.json")
    print(f"Final test accuracy: {accuracy*100:.2f}%")
    print("="*60)


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('../models', exist_ok=True)
    os.makedirs('../logs', exist_ok=True)
    
    # Train model
    train_model()

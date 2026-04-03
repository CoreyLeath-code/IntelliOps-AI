import torch
import torch.nn as nn
import torch.optim as optim
import mlflow
import mlflow.pytorch
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load dataset
data = load_iris()
X = data.data
y = (data.target == 0).astype(int)  # Binary classification

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Scale data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Convert to tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)

X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)

# Model
class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(4, 1)

    def forward(self, x):
        return torch.sigmoid(self.fc(x))

model = Model()

criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# MLflow tracking
mlflow.set_experiment("IntelliOps-Model")

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("epochs", 100)

    # Training loop
    for epoch in range(100):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

    # Evaluation
    with torch.no_grad():
        predictions = model(X_test)
        predicted = (predictions > 0.5).float()
        accuracy = (predicted == y_test).sum().item() / len(y_test)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("loss", loss.item())

    # Save model
    mlflow.pytorch.log_model(model, "model")

    print(f"Accuracy: {accuracy}")

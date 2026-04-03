import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(4, 1)

    def forward(self, x):
        return torch.sigmoid(self.fc(x))

model = SimpleModel()

def predict(input_data):
    with torch.no_grad():
        tensor = torch.tensor(input_data, dtype=torch.float32)
        output = model(tensor)
        return output.numpy().tolist()

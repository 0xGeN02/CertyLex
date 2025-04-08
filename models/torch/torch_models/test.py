import torch
import torch.nn as nn

def test_model(model: nn.Module, test_loader: torch.utils.data.DataLoader, device: torch.device):
    """
    Test a PyTorch model on a given test dataset.

    Parameters:
        model (nn.Module): The PyTorch model to test.
        test_loader (DataLoader): DataLoader for the test dataset.
        device (torch.device): The device to run the test on (CPU or GPU).

    Returns:
        float: The accuracy of the model on the test dataset.
    """
    model.eval()
    model.to(device)
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f"Test Accuracy: {accuracy:.2f}%")
    return accuracy

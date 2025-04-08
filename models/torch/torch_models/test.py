"""
    Module to test a PyTorch model and all dependencies.
    This module includes a function to test the model's accuracy on a given dataset.
"""

try:
    import torch
    from torch import nn
except ModuleNotFoundError as e:
    raise ModuleNotFoundError("The 'torch' library is not installed. Please install it using 'poetry add torch' or 'pip install torch'.") from e

from torchvision.models import resnet18  # Import a pre-trained model

def test_model(model: nn.Module, test_loader: torch.utils.data.DataLoader, device: torch.device, threshold: float = 90.0):
    """
    Test a PyTorch model on a given test dataset.

    Parameters:
        model (nn.Module): The PyTorch model to test.
        test_loader (DataLoader): DataLoader for the test dataset.
        device (torch.device): The device to run the test on (CPU or GPU).
        threshold (float): The accuracy threshold to determine success.

    Returns:
        float: The accuracy of the model on the test dataset.
        bool: Whether the test passed the accuracy threshold.
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

    model_accuracy = 100 * correct / total
    print(f"Test Accuracy: {model_accuracy:.2f}%")
    return model_accuracy, model_accuracy >= threshold

if __name__ == "__main__":
    # Example usage
    import sys
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms

    # Use a pre-trained ResNet18 model for better performance
    NUM_CLASSES = 2  # Example number of output classes
    resnet_model = resnet18(weights='DEFAULT')  # Load the pre-trained model
    resnet_model.fc = nn.Linear(resnet_model.fc.in_features, NUM_CLASSES)  # Adjust the final layer

    # Update data preprocessing with normalization
    test_dataset = datasets.FakeData(
        size=100,  # Example dataset size
        image_size=(3, 224, 224),  # Image dimensions
        num_classes=NUM_CLASSES,
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # Normalize images
        ])
    )
    global_test_loader = DataLoader(test_dataset, batch_size=32)  # Renamed to avoid shadowing
    model_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    accuracy, success = test_model(resnet_model, global_test_loader, model_device)
    if success:
        print("Test passed successfully!")
        sys.exit(0)
    else:
        print("Test failed.")
        sys.exit(1)

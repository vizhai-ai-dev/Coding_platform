import os
import requests
from tqdm import tqdm

def download_file(url: str, filename: str):
    """
    Download a file with a progress bar
    """
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

def main():
    # URL for the Llama 2 7B Chat model
    model_url = "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"
    model_path = "models/llama-2-7b-chat.gguf"
    
    print("Downloading Llama 2 7B Chat model...")
    print("This may take a while depending on your internet connection.")
    print("The model file is about 4GB.")
    
    try:
        download_file(model_url, model_path)
        print(f"\nModel downloaded successfully to {model_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Please download the model manually from:")
        print("https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF")
        print("And place it in the backend/models directory")

if __name__ == "__main__":
    main() 
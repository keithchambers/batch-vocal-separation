import argparse
import os
import yaml
import logging
import urllib.request
import torch

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_DIR = "models"

# Model URLs (MDX-Net and VR models based on the provided data)
MODEL_URLS = {
    "MDX23C-InstVoc HQ": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Inst_HQ_1.onnx",
    "UVR-MDX-NET Karaoke 2": "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR_MDXNET_KARA_2.onnx",
    # Add additional models as needed
}

class VocalExtractor:
    def __init__(self, model, gpu_conversion, segment_size, overlap):
        self.model = model
        self.gpu_conversion = gpu_conversion
        self.segment_size = segment_size
        self.overlap = overlap
        self.model_path = os.path.join(MODEL_DIR, f"{self.model}.onnx")

    def download_model_if_needed(self):
        if not os.path.exists(self.model_path):
            logging.info(f"Model {self.model} not found. Downloading...")
            if self.model in MODEL_URLS:
                os.makedirs(MODEL_DIR, exist_ok=True)
                urllib.request.urlretrieve(MODEL_URLS[self.model], self.model_path)
                logging.info(f"Model {self.model} downloaded successfully.")
            else:
                raise FileNotFoundError(f"Model {self.model} is not available for download. Please add the correct URL.")

    def extract(self, audio_file):
        logging.info(f"Extracting vocals from {audio_file} using model {self.model}")
        return f"processed_{audio_file}"  # Replace with actual audio extraction logic

class DeReverbModel:
    def __init__(self, model):
        self.model = model
        self.model_path = os.path.join(MODEL_DIR, f"{self.model}.onnx")

    def download_model_if_needed(self):
        if not os.path.exists(self.model_path):
            logging.info(f"Dereverb model {self.model} not found. Downloading...")
            if self.model in MODEL_URLS:
                os.makedirs(MODEL_DIR, exist_ok=True)
                urllib.request.urlretrieve(MODEL_URLS[self.model], self.model_path)
                logging.info(f"Dereverb model {self.model} downloaded successfully.")
            else:
                raise FileNotFoundError(f"Dereverb model {self.model} is not available for download. Please add the correct URL.")

    def apply(self, audio_data):
        logging.info(f"Applying dereverb using model {self.model}")
        return audio_data  # Replace with actual dereverb logic

class AudioProcessor:
    @staticmethod
    def list_audio_files(directory):
        return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.wav', '.mp3', '.flac'))]

    @staticmethod
    def save_audio(audio_data, output_file):
        logging.info(f"Saving processed audio to {output_file}")

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def process_audio_files(directory, config):
    gpu_conversion = config.get('gpu_conversion', True)
    segment_size = config.get('segment_size', 4000)
    overlap = config.get('overlap', 99)

    # Extract vocal section
    extract_config = config['extract-vocal']
    vocal_extractor = VocalExtractor(
        model=extract_config['model'], 
        gpu_conversion=gpu_conversion, 
        segment_size=segment_size, 
        overlap=overlap
    )
    vocal_extractor.download_model_if_needed()

    # Dereverb vocal section
    dereverb_config = config.get('dereverb-vocal', None)
    dereverb_model = None
    if dereverb_config:
        dereverb_model = DeReverbModel(model=dereverb_config['model'])
        dereverb_model.download_model_if_needed()

    # Process audio files
    audio_files = AudioProcessor.list_audio_files(directory)

    for idx, audio_file in enumerate(audio_files, 1):
        logging.info(f'Processing {idx}/{len(audio_files)}: {audio_file}')
        
        # Extract vocals
        extracted_vocals = vocal_extractor.extract(audio_file)
        
        # Apply dereverb if configured
        if dereverb_model:
            extracted_vocals = dereverb_model.apply(extracted_vocals)

        # Save the processed file
        output_file = os.path.join(directory, f'processed_{os.path.basename(audio_file)}')
        AudioProcessor.save_audio(extracted_vocals, output_file)

    logging.info('Batch processing complete.')

def main():
    parser = argparse.ArgumentParser(description='Batch process audio files with vocal extraction and dereverbing models.')
    parser.add_argument('-d', '--directory', required=True, help='Directory containing audio files')
    parser.add_argument('-c', '--config', required=True, help='Path to the configuration YAML file')

    args = parser.parse_args()

    # Load configuration from YAML
    config = load_config(args.config)

    # Process all audio files in the specified directory
    process_audio_files(args.directory, config)

if __name__ == '__main__':
    main()

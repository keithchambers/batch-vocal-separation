# Batch Vocal Separation

This tool processes audio files using MDX-Net models for vocal extraction and optional dereverbing with support for Apple Silicon (M1/M2).

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/batch-vocal-separation.git
   cd batch-vocal-separation

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

## Usage

Run the tool with the following command:
```bash
python3 bulk-separate.py -d /path/to/audio/files -c config.yml

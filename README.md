# clean-ableton-unlicensed-devices

This tool extracts and lists all Simpler/Sampler-related device blocks from an Ableton Live `.als` project file. It can be extended easily to other plugins or devices that cause Ableton to throw licensing errors.

Heavily inspired by:
Abletool -> https://ableton-utility.vercel.app/

And relies on:
dawtool -> https://github.com/offlinemark/dawtool


## What it does
- Parses an Ableton `.als` file
- Finds and prints all Simpler/Sampler/MultiSampler/InstrumentGroupDevice blocks
- Useful for identifying sample-based devices in a project

## Setup
1. Clone this repo and `cd` into it.
2. Create a virtual environment (recommended):
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install dawtool
   ```

## Usage
```sh
python als-parser.py /path/to/your/project.als
```
- Output: Number of Simpler/Sampler-related device blocks and a preview of each block.

## Requirements
- Python 3
- dawtool (install with `pip install dawtool`)
import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import subprocess
import tempfile
import dawtool
import gzip


def extract_als_file(input_als_path, dest_dir=None):
    """Extracts the contents of an Ableton Live Set (.als) file to a directory using dawtool."""
    if dest_dir is None:
        dest_dir = os.getcwd()
    os.makedirs(dest_dir, exist_ok=True)
    with open(input_als_path, 'rb') as f:
        proj = dawtool.load_project(input_als_path, f)
        proj.parse()
        xml_path = os.path.join(dest_dir, 'extracted.xml')
        # Decompress if needed
        raw = proj.raw_contents
        try:
            xml_data = gzip.decompress(raw).decode('utf-8')
        except Exception:
            xml_data = raw.decode('utf-8') if isinstance(raw, bytes) else raw
        with open(xml_path, 'w', encoding='utf-8') as out:
            out.write(xml_data)
    print(f"Extracted XML from '{input_als_path}' to '{xml_path}'")


def clean_als_file(input_als_path, dest_dir=None):
    if dest_dir is None:
        dest_dir = os.getcwd()
    # Extract and parse XML in-memory
    with open(input_als_path, 'rb') as f:
        proj = dawtool.load_project(input_als_path, f)
        proj.parse()
        raw = proj.raw_contents
        try:
            xml_data = gzip.decompress(raw).decode('utf-8')
        except Exception:
            xml_data = raw.decode('utf-8') if isinstance(raw, bytes) else raw
    # Clean XML in-memory
    root = ET.fromstring(xml_data)
    to_remove = []
    # Use correct case for MultiSampler
    for elem in root.findall('.//MultiSampler'):
        to_remove.append(elem)
    removed_blocks_info = []
    for elem in to_remove:
        parent = None
        for p in root.iter():
            if elem in list(p):
                parent = p
                break
        if parent is not None:
            elem_str = ET.tostring(elem, encoding='unicode')
            removed_blocks_info.append(elem_str)
            parent.remove(elem)
    cleaned_xml = ET.tostring(root, encoding='utf-8')
    # Write cleaned XML directly to a new .als file (gzip-compressed XML, not zip)
    base = os.path.splitext(os.path.basename(input_als_path))[0]
    output_als_filename = f"{base}-clean.als"
    output_als_path = os.path.join(dest_dir, output_als_filename)
    with gzip.open(output_als_path, 'wb') as gz_out:
        gz_out.write(cleaned_xml)
    print(f"Removed {len(removed_blocks_info)} <MultiSampler> blocks:")
    for i, block in enumerate(removed_blocks_info, 1):
        print(f"Block {i}:\n{block}\n")
    print(f"Cleaned file saved to: {output_als_path}")
    return output_als_path


def summarize_multisamplers(als_path):
    # Extract and parse XML in-memory
    with open(als_path, 'rb') as f:
        proj = dawtool.load_project(als_path, f)
        proj.parse()
        raw = proj.raw_contents
        try:
            xml_data = gzip.decompress(raw).decode('utf-8')
        except Exception:
            xml_data = raw.decode('utf-8') if isinstance(raw, bytes) else raw
    root = ET.fromstring(xml_data)
    results = []
    for track_idx, track in enumerate(root.findall('.//Tracks//MidiTrack')):
        name_elem = track.find('.//UserName')
        name = name_elem.text if name_elem is not None else '(no name)'
        for ms in track.findall('.//MultiSampler'):
            path = f"Song/Tracks/MidiTrack[{track_idx+1}]/.../MultiSampler"
            results.append({
                'track_number': track_idx + 1,
                'track_name': name,
                'path': path,
            })
    print(f"Found {len(results)} MultiSampler devices:")
    for r in results:
        print(
            f"Track {r['track_number']} ('{r['track_name']}') at {r['path']}\n")


def summarize_devices_per_track(als_path):
    # Extract and parse XML in-memory
    with open(als_path, 'rb') as f:
        proj = dawtool.load_project(als_path, f)
        proj.parse()
        raw = proj.raw_contents
        try:
            xml_data = gzip.decompress(raw).decode('utf-8')
        except Exception:
            xml_data = raw.decode('utf-8') if isinstance(raw, bytes) else raw
    root = ET.fromstring(xml_data)
    for track_idx, track in enumerate(root.findall('.//Tracks//MidiTrack')):
        name_elem = track.find('.//UserName')
        name = name_elem.text if name_elem is not None else '(no name)'
        print(f"Track {track_idx+1} ('{name}'):")
        # List all device names under this track
        device_names = []
        for device in track.findall('.//DeviceChain//Devices/*'):
            device_names.append(device.tag)
        if device_names:
            for d in device_names:
                print(f"  - {d}")
        else:
            print("  (No devices found)")
    print()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(
            "Usage: python script.py <mode: clean|extract|summary|devices> <inputfile.als> [destination_directory]")
        sys.exit(1)
    mode = sys.argv[1].lower()
    input_path = sys.argv[2]
    dest_dir = sys.argv[3] if len(sys.argv) > 3 else None
    if mode == 'clean':
        clean_als_file(input_path, dest_dir)
    elif mode == 'extract':
        extract_als_file(input_path, dest_dir)
    elif mode == 'summary':
        # Clean, then summarize the cleaned file
        output_path = clean_als_file(input_path, dest_dir)
        summarize_multisamplers(output_path)
    elif mode == 'devices':
        summarize_devices_per_track(input_path)
    else:
        print("Unknown mode. Use 'clean', 'extract', 'summary', or 'devices'.")
        sys.exit(1)

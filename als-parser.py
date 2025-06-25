import sys
import gzip
import dawtool
import xml.etree.ElementTree as ET


def extract_xml_from_als(als_path):
    with open(als_path, 'rb') as f:
        proj = dawtool.load_project(als_path, f)
        proj.parse()
        raw = proj.raw_contents
        try:
            xml_data = gzip.decompress(raw).decode('utf-8')
        except Exception:
            xml_data = raw.decode('utf-8') if isinstance(raw, bytes) else raw
    return xml_data


def find_multisamplers_with_device(xml_data, device_name=None):
    # Use iterparse for large files
    found = []
    for event, elem in ET.iterparse(sys.stdin if xml_data is None else sys.__stdin__, events=("end",)):
        if elem.tag.lower() == 'multisampler' or elem.tag.lower() == 'multisampler':
            block_str = ET.tostring(elem, encoding='unicode')
            if device_name is None or device_name in block_str:
                found.append(block_str)
        elem.clear()
    return found


def find_simpler_sampler_devices(xml_data):
    import tempfile
    found = []
    with tempfile.NamedTemporaryFile('w+', encoding='utf-8', delete=False) as tmp:
        tmp.write(xml_data)
        tmp.flush()
        tmp.seek(0)
        for event, elem in ET.iterparse(tmp.name, events=("end",)):
            tag = elem.tag.lower()
            # Check for MultiSampler, Simpler, Sampler, or InstrumentGroupDevice
            if (
                "simpler" in tag or
                "sampler" in tag or
                tag == "multisampler" or
                tag == "instrumentgroupdevice"
            ):
                block_str = ET.tostring(elem, encoding='unicode')
                # Only include if Simpler or Sampler in tag or in block
                if ("simpler" in tag or "sampler" in tag or
                        "Simpler" in block_str or "Sampler" in block_str):
                    found.append(block_str)
            elem.clear()
    return found


def main():
    if len(sys.argv) < 2:
        print("Usage: python als-parser.py <inputfile.als>")
        sys.exit(1)
    als_path = sys.argv[1]
    xml_data = extract_xml_from_als(als_path)
    found = find_simpler_sampler_devices(xml_data)
    print(f"Found {len(found)} Simpler/Sampler-related device blocks:")
    for block in found:
        print(block[:400] + ('\n... (truncated) ...' if len(block) > 400 else ''))


if __name__ == "__main__":
    main()

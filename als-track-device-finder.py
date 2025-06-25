import dawtool
import gzip
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


def extract_project(als_path):
    with open(als_path, 'rb') as f:
        proj = dawtool.load_project(als_path, f)
        proj.parse()
        raw = proj.raw_contents
        try:
            xml_data = gzip.decompress(raw).decode('utf-8')
        except Exception:
            xml_data = raw.decode('utf-8') if isinstance(raw, bytes) else raw
    return xml_data


def get_node_path(node):
    path = []
    while node is not None and node.tag != '':
        parent = node.getparent() if hasattr(node, 'getparent') else None
        idx = ''
        if parent is not None:
            siblings = [sib for sib in parent if sib.tag == node.tag]
            if len(siblings) > 1:
                idx = f"[{siblings.index(node)+1}]"
        path.append(f"{node.tag}{idx}")
        node = parent
    return '/'.join(reversed(path))


def pretty_print_xml(elem, maxlen=400):
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty = reparsed.toprettyxml(indent="  ")
    if len(pretty) > maxlen:
        return pretty[:maxlen] + '\n... (truncated) ...'
    return pretty


def find_tracks_and_multisamplers(xml_data):
    root = ET.fromstring(xml_data)
    results = []
    for track_idx, track in enumerate(root.findall('.//Tracks//MidiTrack')):
        name_elem = track.find('.//UserName')
        name = name_elem.text if name_elem is not None else '(no name)'
        for ms in track.findall('.//MultiSampler'):
            # Find the path to this node
            # ET doesn't support getparent, so just show the logical path
            path = f"Song/Tracks/MidiTrack[{track_idx+1}]/.../MultiSampler"
            results.append({
                'track_number': track_idx + 1,
                'track_name': name,
                'path': path,
                'pretty_xml': pretty_print_xml(ms)
            })
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python als-track-device-finder.py <inputfile.als>")
        sys.exit(1)
    als_path = sys.argv[1]
    xml_data = extract_project(als_path)
    # Write extended XML file
    import os
    base, _ = os.path.splitext(als_path)
    extended_xml_path = base + '-extended.xml'
    with open(extended_xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_data)
    print(f"Extracted XML written to: {extended_xml_path}")
    results = find_tracks_and_multisamplers(xml_data)
    print(f"Found {len(results)} MultiSampler devices:")
    for r in results:
        print(
            f"Track {r['track_number']} ('{r['track_name']}') at {r['path']}\n")


if __name__ == "__main__":
    main()

import json
import urllib.request
import urllib.parse
import uuid
import websocket # pip install websocket-client
import os
import argparse
import time

# G-FORGE: CLI wrapper for ComfyUI API
# Version 1.0.0

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{SERVER_ADDRESS}/history/{prompt_id}") as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break # Execution finished
        else:
            continue # binary data (previews)

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            images_output = []
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

def forge(prompt_text, output_path="forge_output.png", workflow_path=None):
    if not workflow_path:
        workflow_path = os.path.join(os.path.dirname(__file__), "workflows", "sdxl_basic.json")
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # Simple logic to find the text node and swap the prompt
    # In standard workflows, we often look for CLIPTextEncode nodes
    for node_id in workflow:
        node = workflow[node_id]
        if node["class_type"] == "CLIPTextEncode" or node["class_type"] == "FluxGuidance":
            if "text" in node["inputs"]:
                node["inputs"]["text"] = prompt_text
            elif "conditioning" in node["inputs"] and isinstance(node["inputs"]["conditioning"], str):
                 node["inputs"]["conditioning"] = prompt_text

    ws = websocket.WebSocket()
    ws.connect(f"ws://{SERVER_ADDRESS}/ws?clientId={CLIENT_ID}")
    
    print(f"[G-FORGE] Forging: {prompt_text}")
    images = get_images(ws, workflow)
    
    for node_id in images:
        for i, image_data in enumerate(images[node_id]):
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"[G-FORGE] Saved image to: {output_path}")
            return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="G-FORGE: Local Image Generation CLI")
    parser.add_argument("prompt", type=str, help="Text prompt for generation")
    parser.add_argument("--output", "-o", type=str, default="forge_output.png", help="Output filename")
    parser.add_argument("--workflow", "-w", type=str, help="Path to workflow JSON")
    
    args = parser.parse_args()
    
    try:
        forge(args.prompt, args.output, args.workflow)
    except Exception as e:
        print(f"[G-FORGE] Error: {e}")

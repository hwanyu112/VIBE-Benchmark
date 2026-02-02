import os
import json
import base64
from io import BytesIO
from PIL import Image
from tqdm import tqdm
import time
import openai
from openai import OpenAI


# ================= Configuration Section =================

# User-provided global configuration
BASE_DIR = "/path/to/your/VIBE-Benchmark-Dataset/"
MAX_DISPLAY_SIZE = 1500 
CUSTOM_RUN_SUFFIX = "_run_v1"

TASK_CONFIG = {
    "Addition": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Addition/Addition.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Addition/"),
        "image_root": BASE_DIR 
    },
    "Removal": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Removal/Removal.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Removal/"),
        "image_root": BASE_DIR
    },
    "Replacement": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Replacement/Replacement.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Replacement/"),
        "image_root": BASE_DIR
    },
    "Translation": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Translation/Translation.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-1-Deictic/Translation/"),
        "image_root": BASE_DIR
    },
    "Pose_Control": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Pose_Control/dataset.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Pose_Control/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Pose_Control/")
    },
    "Reorientation": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Reorientation/Reorientation.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Reorientation/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Reorientation/" )
    },
    "Draft_Instantiation": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Draft_Instantiation/draft_instantiation.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Draft_Instantiation/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Level-2-Morphological/Draft_Instantiation/" )
    },
    "Flow_Simulation": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Flow/flow.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Flow/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Flow/") 
    },
    "Light_Control": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Light_Control/light_control.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Light_Control/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Light_Control/")
    },
    "Billiards": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Billiards/Billiards.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Billiards/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Level-3-Causal/Billiards/")
    }
}

# ================= Utility Functions =================

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="PNG") # Recommended to use PNG to preserve quality and transparency
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def resize_image_if_needed(image, max_size=MAX_DISPLAY_SIZE):
    """Resize image if needed"""
    w, h = image.size
    if max(w, h) > max_size:
        scale = max_size / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return image

def pil_to_bytes_stream(image, name="image.png"):
    """Convert PIL Image to BytesIO stream and set name attribute"""
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG') 
    img_byte_arr.seek(0)
    img_byte_arr.name = name
    return img_byte_arr

def process_and_merge_images(source_path, layer_path=None, max_size=MAX_DISPLAY_SIZE):
    """
    Read source image and layer (optional), composite them, and resize.
    If layer_path is None or empty, only process source_path
    """
    try:
        # 1. Open Source image
        source_img = Image.open(source_path).convert("RGBA")
        
        # 2. Check if need to composite Layer
        if layer_path and os.path.exists(layer_path):
            layer_img = Image.open(layer_path).convert("RGBA")
            
            # Resize layer to match source
            if source_img.size != layer_img.size:
                layer_img = layer_img.resize(source_img.size, Image.Resampling.LANCZOS)
            
            # Composite
            final_img = Image.alpha_composite(source_img, layer_img)
        else:
            # If no layer, use source directly
            # (If layer_path exists but file not found, skip compositing and use original image,
            # If you want to raise error, add raise FileNotFoundError in else)
            final_img = source_img

        # 3. Convert to RGB (remove Alpha channel)
        final_img = final_img.convert("RGB")

        # 4. Size optimization (Resize)
        w, h = final_img.size
        if max(w, h) > max_size:
            scale = max_size / max(w, h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            final_img = final_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        return final_img

    except FileNotFoundError as e:
        print(f"Error loading images: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error processing images: {e}")
        return None


# ================= Main Logic Class =================

class BenchmarkEvaluator:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        # 这里记录模型名称，用于创建文件夹
        self.model_name = "gpt-image-1"
        self.run_suffix = CUSTOM_RUN_SUFFIX

    def run_task(self, task_name):
        """运行指定的Task，并将结果保存在原数据目录下的模型文件夹中"""
        if task_name not in TASK_CONFIG:
            print(f"Task '{task_name}' not found.")
            return

        config = TASK_CONFIG[task_name]
        json_path = config['json_path']
        image_root = config['image_root']
        
        # --- [Key Modification] Build save path ---
        base_task_dir = os.path.dirname(json_path)
        folder_name = f"{self.model_name}{self.run_suffix}" # e.g.: gpt-image-1_run_v1
        save_dir = os.path.join(base_task_dir, folder_name)
        img_save_dir = os.path.join(save_dir, "imgs")

        output_json_path = os.path.join(save_dir, f"{task_name}_results.json")
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Created output directory: {save_dir}")
        else:
            print(f"Output directory exists: {save_dir}")

        if not os.path.exists(img_save_dir):
            os.makedirs(img_save_dir)
            print(f"Created output directory: {img_save_dir}")
        else:
            print(f"Output directory exists: {img_save_dir}")

        print(f"Loading task data from: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        results = []
        processed_ids = set()

        if os.path.exists(output_json_path):
            print(f"Found existing results at {output_json_path}. Checking for completed items...")
            try:
                with open(output_json_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    # Record already successfully processed IDs
                    for item in results:
                        if item.get('status') == 'success':
                            processed_ids.add(item['id'])
                print(f"Skipping {len(processed_ids)} already processed items.")
            except json.JSONDecodeError:
                print("Existing JSON is corrupt. Starting fresh.")
        
        # Iterate through data
        for item in tqdm(data, desc=f"Processing {task_name}"):
            item_id = item['id']

            if item_id in processed_ids:
                continue
            
            # --- Path resolution (unchanged) ---
            source_rel_path = item['file_paths']['source']
            source_full_path = os.path.join(image_root, source_rel_path)
            
            instr_rel_path = item['file_paths'].get('visual_instruction', "")
            if instr_rel_path and instr_rel_path.strip() != "":
                instr_full_path = os.path.join(base_task_dir, instr_rel_path)
            else:
                instr_full_path = None # Mark as None, subsequent function will recognize
            prompt_text = item['text_prompt']['input_prompt']

            image_streams = []

            try:
                # *** Special handling for Pose_Control ***
                if task_name == "Pose_Control":
                    # 1. Source Image
                    if os.path.exists(source_full_path):
                        src_img = Image.open(source_full_path).convert("RGB")
                        src_img = resize_image_if_needed(src_img)
                        image_streams.append(pil_to_bytes_stream(src_img, name="source.png"))
                    else:
                        print(f"Source image missing for {item_id}")
                        continue
                    
                    # 2. Visual Instruction (if exists)
                    if instr_full_path and os.path.exists(instr_full_path):
                        inst_img = Image.open(instr_full_path).convert("RGB")
                        inst_img = resize_image_if_needed(inst_img)
                        image_streams.append(pil_to_bytes_stream(inst_img, name="instruction.png"))
                
                # *** Other tasks (default merge) ***
                else:
                    combined_img = process_and_merge_images(source_full_path, instr_full_path)
                    if combined_img is None:
                        continue
                    image_streams.append(pil_to_bytes_stream(combined_img, name="merged.png"))

            except Exception as e:
                print(f"Error preparing images for {item_id}: {e}")
                continue

            current_result = {}

            # --- API Call ---
            success = False
            try:
                response = self.client.images.edit(
                    model=self.model_name,
                    image=image_streams, # 将合成图作为列表传入
                    prompt=prompt_text,
                    n=1,
                    extra_query={
                    "api-version": "2025-04-01-preview", 
                },
                )
                
                # --- Parse and save image ---
                # Get Base64 data
                image_base64 = response.data[0].b64_json
                image_bytes = base64.b64decode(image_base64)
                
                # Define save filename (use ID)
                save_filename = f"{item_id}.png"
                save_file_path = os.path.join(img_save_dir, save_filename)
                
                with open(save_file_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                # --- Record results ---
                current_result = {
                    "id": item_id,
                    "input_prompt": prompt_text,
                    "saved_image_path": save_filename, # Absolute path of saved image
                    "status": "success"
                }
                
                success = True
            except openai.AuthenticationError as e:
                print(f"AuthenticationError occurred: {e}")
                if hasattr(e, "status_code") and e.status_code == 401:
                    time.sleep(5)
            except openai.RateLimitError as e:
                print(f"RateLimitError occurred: {e}")
                if hasattr(e, "status_code") and e.status_code == 429:
                    time.sleep(5)
            except openai.BadRequestError as e:
                print(f"BadRequestError occurred: {e}")
                if hasattr(e, "status_code") and e.status_code == 400:
                    time.sleep(5)
            except openai.InternalServerError as e:
                print(f"InternalServerError occurred: {e}")
                time.sleep(10)

            if success:
                results = [r for r in results if r['id'] != item_id]
                
                # Add current result
                results.append(current_result)
                
                # Write back to file immediately
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"Task finished. Results and images saved to: {save_dir}")

# ================= Entry Point =================

if __name__ == "__main__":
    evaluator = BenchmarkEvaluator()
    
    # Test Flow task
    target_task = "Reorientation"
    evaluator.run_task(target_task)
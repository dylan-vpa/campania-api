import runpod
import base64
import os
import tempfile
import subprocess
import json

print("Starting NVIDIA PersonaPlex Serverless Handler...")

def handler(job):
    job_input = job['input']
    text_prompt = job_input.get("text_prompt", "You are a helpful AI assistant.")
    input_audio_b64 = job_input.get("input_audio_b64", "")
    
    # 1. Escribir audio a temporales
    in_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    out_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    out_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name
    
    if input_audio_b64:
        with open(in_wav, "wb") as f:
            f.write(base64.b64decode(input_audio_b64))
    else:
        # Crear 1 segundo de silencio si no hay audio de entrada inicial (primer turno)
        os.system(f"sox -n -r 8000 -c 1 {in_wav} trim 0.0 1.0")

    print(f"Running Moshi inference on {in_wav}...")
    
    # 2. Ejecutar PersonaPlex Offline (Moshi)
    cmd = [
        "python", "-m", "moshi.offline",
        "--voice-prompt", "NATF1.pt",  # Voz Femenina Natural (o NATM1.pt para hombre)
        "--text-prompt", text_prompt,
        "--input-wav", in_wav,
        "--output-wav", out_wav,
        "--output-text", out_json
    ]
    
    try:
        env = os.environ.copy()
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd="/app/personaplex")
        
        if result.returncode != 0:
            print("Moshi Error:", result.stderr)
            return {"status": "error", "message": f"Moshibot Error: {result.stderr}"}
            
        # 3. Leer los resultados generados
        with open(out_wav, "rb") as f:
            out_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        with open(out_json, "r") as f:
            try:
                transcript_data = json.load(f)
            except:
                transcript_data = {"text": open(out_json, "r").read()} # Fallback
            
    except Exception as e:
        print("Exception:", str(e))
        return {"status": "error", "message": str(e)}
    finally:
        for f in [in_wav, out_wav, out_json]:
            if os.path.exists(f): os.remove(f)

    print("Inference successful. Returning audio & text.")
    return {
        "status": "success",
        "transcript": transcript_data,
        "response_audio_b64": out_b64
    }

if __name__ == '__main__':
    runpod.serverless.start({"handler": handler})

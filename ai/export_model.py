"""
Script para exportar el modelo mDeBERTa a formato ONNX.
Se ejecuta una sola vez para generar los archivos del modelo.

Uso:
    python ai/export_model.py

Requisitos (solo para exportacion):
    pip install transformers torch optimum[onnxruntime]
"""
import os
import sys
import ssl

# Solucionar problema de certificados SSL en Windows
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['HF_HUB_DISABLE_SSL_VERIFY'] = '1'

# Desactivar warnings de SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def export_model():
    model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_onnx")
    
    if os.path.exists(output_dir) and os.path.exists(os.path.join(output_dir, "model.onnx")):
        print(f"[OK] El modelo ONNX ya existe en: {output_dir}")
        return output_dir
    
    print(f"[1/3] Descargando modelo: {model_name}")
    print("      Esto puede tardar unos minutos la primera vez...")
    
    try:
        from optimum.onnxruntime import ORTModelForSequenceClassification
        from transformers import AutoTokenizer
    except ImportError:
        print("[Error] Necesitas instalar las dependencias de exportacion:")
        print("  pip install transformers torch optimum[onnxruntime]")
        sys.exit(1)
    
    # Parchear requests para ignorar SSL
    import requests
    old_merge = requests.adapters.HTTPAdapter.send
    def patched_send(self, request, *args, **kwargs):
        kwargs['verify'] = False
        return old_merge(self, request, *args, **kwargs)
    requests.adapters.HTTPAdapter.send = patched_send
    
    print(f"[2/3] Exportando a ONNX en: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Exportar modelo a ONNX
    model = ORTModelForSequenceClassification.from_pretrained(
        model_name,
        export=True
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Guardar modelo y tokenizer
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print(f"[3/3] Modelo exportado exitosamente!")
    print(f"       Ubicacion: {output_dir}")
    
    # Mostrar tamano
    total_size = 0
    for f in os.listdir(output_dir):
        fp = os.path.join(output_dir, f)
        if os.path.isfile(fp):
            total_size += os.path.getsize(fp)
    print(f"       Tamano total: {total_size / (1024*1024):.1f} MB")
    
    return output_dir


if __name__ == "__main__":
    export_model()

from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import threading
import requests
import io

app = Flask(__name__)

# URL do endpoint do Mendix
MENDIX_UPLOAD_URL = "http://192.168.31.62:8080/rest/upload"

# Inicializa e configura a câmera
picam2 = Picamera2()
try:
    config = picam2.create_preview_configuration(main={"size": (1280, 720)})
    picam2.configure(config)
    # AWB automático no modo diurno
    picam2.set_controls({"AwbEnable": True})
    picam2.start()
    time.sleep(1)
except Exception as e:
    print(f"Erro ao inicializar a câmera: {e}")

# Controles para alternar entre dia e noite
controles_dia = {"AwbEnable": True}
controles_noite = {"AwbEnable": False, "ColourGains": (0.8, 1.8)}

# Detector de pessoas HOG
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# White-balance em software (Grayworld) para cores realistas
default_wb = cv2.xphoto.createGrayworldWB()

# Variáveis de controle
ultima_detecao = 0
LIMIAR_ESCURO = 30  # brilho médio para alternar modos
modo_atual = "dia"

# Envio de imagem detectada em thread separada
def handle_detection(frame_bytes: bytes):
    try:
        response = requests.post(
            MENDIX_UPLOAD_URL,
            files={'PessoaDetectada': ('imagem.jpg', io.BytesIO(frame_bytes), 'image/jpeg')}
        )
        print(f"[INFO] Imagem enviada - Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"Erro no envio da imagem: {e}")

# Gera frames com efeito de visão noturna verde
def generate_frames():
    global ultima_detecao, modo_atual
    while True:
        try:
            # Captura e pré-processamento
            frame = picam2.capture_array()
            frame = cv2.flip(frame, -1)
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Reduz para cálculo de brilho
            small = cv2.resize(bgr, (320, 240))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            brilho_medio = gray.mean()

            # Alterna modo diurno/noturno
            try:
                if brilho_medio < LIMIAR_ESCURO and modo_atual != "noite":
                    picam2.set_controls(controles_noite)
                    modo_atual = "noite"
                    print("Modo noturno ativado")
                elif brilho_medio >= LIMIAR_ESCURO and modo_atual != "dia":
                    picam2.set_controls(controles_dia)
                    modo_atual = "dia"
                    print("Modo diurno ativado")
            except RuntimeError as e:
                print(f"Aviso controle não suportado: {e}")

            # Aplica white-balance em software
            try:
                bgr_corr = default_wb.balanceWhite(bgr)
            except Exception:
                bgr_corr = bgr

            # Se estiver no modo noturno, aplica efeito verde
            if modo_atual == "noite":
                gray_full = cv2.cvtColor(bgr_corr, cv2.COLOR_BGR2GRAY)
                night = np.zeros_like(bgr_corr)
                night[:, :, 1] = gray_full  # canal verde recebe luminância
                bgr_corr = night

            # Detecta pessoas
            boxes, _ = hog.detectMultiScale(small, winStride=(8, 8))
            now = time.time()
            if len(boxes) > 0 and (now - ultima_detecao) > 1:
                ultima_detecao = now
                _, buf = cv2.imencode('.jpg', frame)
                threading.Thread(
                    target=handle_detection,
                    args=(buf.tobytes(),),
                    daemon=True
                ).start()

            # Codifica e envia frame para streaming
            _, buffer = cv2.imencode('.jpg', bgr_corr)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        except Exception as e:
            print(f"Erro no processamento do frame: {e}")
            continue

@app.route('/')
def index():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        print(f"Erro no servidor Flask: {e}")

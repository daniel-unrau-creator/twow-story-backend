import os
import io
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import easyocr
from gtts import gTTS

# Flask App initialisieren
app = Flask(__name__)
CORS(app)  # Cross-Origin Requests erlauben

# EasyOCR Reader für Deutsch und Englisch
reader = easyocr.Reader(['de', 'en'])

# OCR Endpoint
@app.route("/ocr", methods=["POST"])
def ocr():
    try:
        data = request.get_json()
        image_data = data.get("image")
        if not image_data:
            return jsonify({"error": "Kein Bild empfangen"}), 400

        # Bilddaten dekodieren
        image_bytes = base64.b64decode(image_data.split(",")[1])
        result = reader.readtext(image_bytes, detail=0)
        text = "\n".join(result)
        print("Erkannter Text:", text)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# TTS Endpoint
@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json()
        text = data.get("text", "")
        lang = data.get("lang", "de")  # Standard: Deutsch

        if not text.strip():
            return jsonify({"error": "Kein Text übergeben"}), 400

        # Text zu Sprache
        tts = gTTS(text=text, lang=lang, slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        return send_file(
            mp3_fp,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="tts.mp3"
        )
    except Exception as e:
        return jsonify({"error": f"TTS-Fehler: {str(e)}"}), 500

# Root Endpoint zum Testen
@app.route("/")
def home():
    return "Hello, Render!"

# Main: Server starten
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

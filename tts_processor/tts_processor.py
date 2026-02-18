import edge_tts, re

class TTSProcessor:
    def __init__(self):
        pass

    def get_first_bold_text(self, text) -> str:
        match = re.search(r"<b>(.*?)</b>", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    def generate_audio_sync(self, text, output_path):
        text = self.get_first_bold_text(text)
        print(f'Generating audio in from text: {text}')
        communicate = edge_tts.Communicate(
            text,
            voice="ja-JP-NanamiNeural",
        )
        communicate.save_sync(output_path)
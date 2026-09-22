from PIL import Image
import os

src_path = r'C:\Users\Rasika\.gemini\antigravity-ide\brain\28267c92-d07d-4094-9c7e-2b454225d0af\assistiq_logo_icon_1790059812836.jpg'
img = Image.open(src_path).convert('RGBA')

# Target directories
os.makedirs(r'E:\AssistIQ\frontend\public', exist_ok=True)
os.makedirs(r'E:\AssistIQ\frontend\build', exist_ok=True)
os.makedirs(r'E:\AssistIQ\flutter_app\assets\images', exist_ok=True)

# 1. 512x512 PNG
img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
img_512.save(r'E:\AssistIQ\frontend\public\icon.png', 'PNG')
img_512.save(r'E:\AssistIQ\frontend\build\icon.png', 'PNG')
img_512.save(r'E:\AssistIQ\flutter_app\assets\images\app_logo.png', 'PNG')

# 2. Favicon PNG (64x64)
img_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
img_64.save(r'E:\AssistIQ\frontend\public\favicon.png', 'PNG')

# 3. ICO multi-size (256, 128, 64, 48, 32, 16)
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
img_512.save(r'E:\AssistIQ\frontend\build\icon.ico', format='ICO', sizes=sizes)
img_512.save(r'E:\AssistIQ\frontend\public\favicon.ico', format='ICO', sizes=sizes)

print('Icons generated successfully!')

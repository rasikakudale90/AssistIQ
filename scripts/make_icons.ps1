Add-Type -AssemblyName System.Drawing

$srcPath = "C:\Users\Rasika\.gemini\antigravity-ide\brain\28267c92-d07d-4094-9c7e-2b454225d0af\assistiq_logo_icon_1790059812836.jpg"
$img = [System.Drawing.Image]::FromFile($srcPath)

# Ensure directories
New-Item -ItemType Directory -Force -Path "E:\AssistIQ\frontend\public" | Out-Null
New-Item -ItemType Directory -Force -Path "E:\AssistIQ\frontend\build" | Out-Null
New-Item -ItemType Directory -Force -Path "E:\AssistIQ\flutter_app\assets\images" | Out-Null

# 1. 512x512 PNG
$bmp512 = New-Object System.Drawing.Bitmap 512, 512
$g = [System.Drawing.Graphics]::FromImage($bmp512)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($img, 0, 0, 512, 512)
$g.Dispose()

$bmp512.Save("E:\AssistIQ\frontend\public\icon.png", [System.Drawing.Imaging.ImageFormat]::Png)
$bmp512.Save("E:\AssistIQ\frontend\build\icon.png", [System.Drawing.Imaging.ImageFormat]::Png)
$bmp512.Save("E:\AssistIQ\flutter_app\assets\images\app_logo.png", [System.Drawing.Imaging.ImageFormat]::Png)

# 2. 64x64 Favicon PNG
$bmp64 = New-Object System.Drawing.Bitmap 64, 64
$g64 = [System.Drawing.Graphics]::FromImage($bmp64)
$g64.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g64.DrawImage($img, 0, 0, 64, 64)
$g64.Dispose()
$bmp64.Save("E:\AssistIQ\frontend\public\favicon.png", [System.Drawing.Imaging.ImageFormat]::Png)

# 3. 256x256 ICO
$bmp256 = New-Object System.Drawing.Bitmap $bmp512, 256, 256
$hIcon = $bmp256.GetHicon()
$icon = [System.Drawing.Icon]::FromHandle($hIcon)

$fs = New-Object System.IO.FileStream("E:\AssistIQ\frontend\build\icon.ico", [System.IO.FileMode]::Create)
$icon.Save($fs)
$fs.Close()

Copy-Item "E:\AssistIQ\frontend\build\icon.ico" "E:\AssistIQ\frontend\public\favicon.ico" -Force

$img.Dispose()
$bmp512.Dispose()
$bmp64.Dispose()
$bmp256.Dispose()

Write-Host "Icons generated successfully!"

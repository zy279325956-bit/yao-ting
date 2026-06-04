# 一键构建（部署前跑一次：python _build.py）
#  ① 为 images/ 下每张原图生成 preview/ 预览图（原图不动；已存在且较新则跳过）
#  ② 扫描 musics/ 下的音频，生成 musics/playlist.json，播放器会自动读取并列表循环
import os, sys, glob, json, urllib.parse
from PIL import Image, ImageOps

try:                                    # 让 Windows 控制台也能正常输出中文
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(ROOT, "images")
PREVIEW = os.path.join(ROOT, "preview")
MUSICS = os.path.join(ROOT, "musics")
MAXEDGE, QUALITY = 1920, 86
AUDIO_EXT = (".mp3", ".m4a", ".aac", ".ogg", ".oga", ".wav", ".flac")


def build_previews():
    os.makedirs(PREVIEW, exist_ok=True)
    files = sorted(glob.glob(os.path.join(IMAGES, "*.jpg")) +
                   glob.glob(os.path.join(IMAGES, "*.jpeg")) +
                   glob.glob(os.path.join(IMAGES, "*.png")))
    made = skipped = 0
    for fn in files:
        base = os.path.splitext(os.path.basename(fn))[0] + ".jpg"
        out = os.path.join(PREVIEW, base)
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(fn):
            skipped += 1
            continue
        try:
            im = ImageOps.exif_transpose(Image.open(fn))
            if im.mode != "RGB":
                im = im.convert("RGB")
            w, h = im.size
            s = MAXEDGE / float(max(w, h))
            if s < 1:
                im = im.resize((max(1, round(w * s)), max(1, round(h * s))),
                               Image.Resampling.LANCZOS)
            im.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
            made += 1
            print("preview:", base, "%dKB" % (os.path.getsize(out) // 1024), flush=True)
        except Exception as e:
            print("preview ERR", base, repr(e), flush=True)
    print("预览图：新增 %d，跳过 %d" % (made, skipped), flush=True)


def build_playlist():
    if not os.path.isdir(MUSICS):
        print("没有 musics/ 目录，跳过歌单", flush=True)
        return
    files = sorted(f for f in os.listdir(MUSICS) if f.lower().endswith(AUDIO_EXT))
    pl = [{"src": "musics/" + urllib.parse.quote(f),
           "title": os.path.splitext(f)[0]} for f in files]
    with open(os.path.join(MUSICS, "playlist.json"), "w", encoding="utf-8") as fp:
        json.dump(pl, fp, ensure_ascii=False, indent=2)
    print("歌单：musics/playlist.json 共 %d 首" % len(pl), flush=True)
    for it in pl:
        print("  -", it["title"], flush=True)


if __name__ == "__main__":
    build_previews()
    build_playlist()
    print("DONE", flush=True)

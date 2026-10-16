#!/usr/bin/env python3
"""Next Life RP.lt commercial: stitch existing Runway media without regenerating."""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageStat

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
OUT = ROOT / "output"
WORK.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
VIDEO = OUT / "NEXT_LIFE_RP_LT_REKLAMA_50s.mp4"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def run(args, *, capture=False):
    print("RUN:", " ".join(str(a) for a in args[:5]), flush=True)
    p = subprocess.run(args, text=True, capture_output=capture)
    if p.returncode != 0:
        if capture:
            print((p.stderr or "")[-6500:], flush=True)
        raise RuntimeError("Command failed with exit code " + str(p.returncode))
    return p.stdout if capture else None

def download(name, url):
    dest = WORK / name
    if dest.exists() and dest.stat().st_size > 10000:
        return dest
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=90) as rsp:
                if rsp.status != 200:
                    raise RuntimeError("HTTP " + str(rsp.status))
                with dest.open("wb") as f:
                    shutil.copyfileobj(rsp, f, length=1024*1024)
            if dest.stat().st_size < 1000:
                raise RuntimeError("Media download too small")
            print("DOWNLOADED", name, dest.stat().st_size, flush=True)
            return dest
        except Exception as exc:
            print("RETRY", name, i+1, type(exc).__name__, str(exc)[:170], flush=True)
            dest.unlink(missing_ok=True)
            if i == 3:
                raise
            time.sleep((i+1)*2)

def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture=True))

def make_card(img_file):
    im = Image.open(img_file).convert("RGB")
    im = ImageOps.fit(im, (1080,1920), method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(7))
    veil = Image.new("RGBA", im.size, (5, 10, 24, 135))
    im = Image.alpha_composite(im.convert("RGBA"), veil)
    dr = ImageDraw.Draw(im, "RGBA")
    dr.rounded_rectangle((65,655,1015,1330),radius=38,fill=(0,7,19,188))
    dr.line((270,800,810,800),fill=(210,181,122,220),width=3)
    head="NEXT LIFE RP.lt"
    font_size=102
    font=ImageFont.truetype(FONT_BOLD, font_size)
    while dr.textbbox((0,0),head,font=font)[2] > 920:
        font_size -= 2
        font=ImageFont.truetype(FONT_BOLD,font_size)
    def center(text,y,font,fill):
        b=dr.textbbox((0,0),text,font=font,stroke_width=0)
        x=(1080-(b[2]-b[0]))/2
        dr.text((x+2,y+4),text,font=font,fill=(0,0,0,185),anchor="lt")
        dr.text((x,y),text,font=font,fill=fill,anchor="lt")
    center(head,866,font,(255,255,255,255))
    center("Tavo istorija prasideda čia.",1030,ImageFont.truetype(FONT_REG,43),(230,230,235,255))
    dr.line((270,1200,810,1200),fill=(210,181,122,170),width=2)
    path=WORK/"endcard_verified.png"
    im.convert("RGB").save(path,quality=97)
    return path

def timestamp(t):
    h=int(t//3600);m=int(t//60%60);s=int(t%60);cs=int(round((t-int(t))*100))
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def write_ass():
    subtitles = [
        (0.65,3.2,"Po tokios dienos norėjau tik vieno…"),
        (3.2,5.6,"grįžt namo, užsidėt ausines"),
        (5.6,9.2,"ir pamiršt viską. Bet tą vakarą\nįsijungiau kitą gyvenimą."),
        (15.1,17.2,"O, naujokas! Labas!"),
        (17.2,19.0,"Darbo ieškai?"),
        (19.0,20.9,"Sėsk, parodysiu miestą!"),
        (21.7,24.7,"Vakar čia nepažinojau nė vieno."),
        (24.7,27.3,"Šiandien – pirmas darbas,\npirmi pinigai…"),
        (27.3,29.55,"ir žmonės, kurie prisimena mano vardą."),
        (30.25,32.2,"Ei, chebra! Vakare renkamės"),
        (32.2,34.9,"prie garažo! Lauksim ir tavęs!"),
        (35.8,38.6,"Prisėdau tiesiog atsipalaiduot."),
        (38.6,41.0,"O radau vietą, į kurią norisi sugrįžt."),
        (41.0,43.5,"Next Life RP taškas LT."),
        (43.5,45.0,"Tavo istorija tik prasideda.")
    ]
    header = """[Script Info]
Title: Next Life RP.lt
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,53,&H00FFFFFF,&H00FFFFFF,&HBC09090A,&H78000000,-1,0,0,0,100,100,0,0,1,3,1,2,90,90,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    p=WORK/"subtitles.ass"
    with p.open("w", encoding="utf8") as f:
        f.write(header)
        for start,end,line in subtitles:
            line=line.replace("\n",r"\N")
            f.write(f"Dialogue: 0,{timestamp(start)},{timestamp(end)},Default,,0,0,0,,{line}\n")
    return p

def render():
    raw=json.loads((ROOT/"asset_urls.json").read_text(encoding="utf8"))
    for name,url in raw.items():
        download(name,url)
    for name in ("part1.mp4","part2.mp4","part3.mp4"):
        p=probe(WORK/name)
        v=next(x for x in p["streams"] if x["codec_type"]=="video")
        duration=float(p["format"]["duration"])
        print("VALID_VIDEO",name,v["width"],v["height"],v["codec_name"],"duration",round(duration,3),flush=True)
        if duration < 14.5 or v["width"] < 700 or v["height"] < 1200:
            raise RuntimeError("Invalid animation segment " + name)
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss","7","-i",str(WORK/name),"-frames:v","1",str(WORK/(name+".jpg"))])
        pic=Image.open(WORK/(name+".jpg")).convert("L")
        if ImageStat.Stat(pic).mean[0] < 2.5:
            raise RuntimeError("One of the original video segments is already black: "+name)

    card=make_card(WORK/"endcard.png")
    sub=write_ass()
    inputs=[]
    for name in ("part1.mp4","part2.mp4","part3.mp4"):
        inputs+=["-i",str(WORK/name)]
    inputs+=["-loop","1","-framerate","30","-t","5","-i",str(card)]
    for name in ("voice1.mp3","friend1.mp3","voice2.mp3","friend2.mp3","voice3.mp3","music.mp3","endfx.mp3"):
        inputs+=["-i",str(WORK/name)]

    g=[]
    for k in range(3):
        g.append(f"[{k}:v]trim=duration=15,setpts=PTS-STARTPTS,fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{k}]")
    g.append("[3:v]trim=duration=5,setpts=PTS-STARTPTS,fps=30,scale=1080:1920,setsar=1,format=yuv420p[title]")
    g.append("[v0][v1][v2][title]concat=n=4:v=1:a=0[full]")
    g.append("[full]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='Next Life RP.lt':fontcolor=white@0.90:fontsize=49:shadowx=2:shadowy=3:shadowcolor=black@0.72:x=(w-text_w)/2:y=180:enable='between(t,11,14.5)',ass="+str(sub)+",format=yuv420p[outv]")
    for k in range(3):
        g.append(f"[{k}:a]atrim=duration=15,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[amb{k}]")
    g.append("[amb0][amb1][amb2]concat=n=3:v=0:a=1,volume=0.31,apad=pad_dur=5[amb]")
    voice_times=[650,15100,21700,30250,35800]
    for k,at in enumerate(voice_times):
        idx=4+k
        g.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.05,adelay={at}|{at}[sp{k}]")
    g.append("[sp0][sp1][sp2][sp3][sp4]amix=inputs=5:duration=longest:dropout_transition=0:normalize=0[voices]")
    g.append("[9:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration=50,asetpts=PTS-STARTPTS,volume=0.18,afade=t=in:st=0:d=0.7,afade=t=out:st=47.5:d=2.5[score]")
    g.append("[10:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.25,adelay=45000|45000[endfx]")
    g.append("[amb][voices][score][endfx]amix=inputs=4:duration=longest:dropout_transition=0:normalize=0,alimiter=limit=0.94,atrim=duration=50,aresample=48000[outa]")
    fc=";".join(g)
    cmd=["ffmpeg","-hide_banner","-loglevel","warning","-stats","-y",*inputs,
         "-filter_complex",fc,"-map","[outv]","-map","[outa]",
         "-c:v","libx264","-preset","veryfast","-crf","18",
         "-profile:v","high","-level","4.2","-pix_fmt","yuv420p",
         "-r","30","-c:a","aac","-b:a","192k",
         "-t","50","-movflags","+faststart",str(VIDEO)]
    run(cmd)
    return VIDEO

def validate(video):
    result=probe(video)
    streams=result["streams"]
    v=next(x for x in streams if x["codec_type"]=="video")
    a=next((x for x in streams if x["codec_type"]=="audio"),None)
    duration=float(result["format"]["duration"])
    print("EXPORTED",video,"BYTES",video.stat().st_size,"DURATION",duration,flush=True)
    if not (49.6 < duration < 50.5 and v["width"]==1080 and v["height"]==1920 and a and video.stat().st_size > 1500000):
        raise RuntimeError("MP4 validity check failed")

    print("Validating full decoded video and searching for blank spans...",flush=True)
    proc=subprocess.run(["ffmpeg","-hide_banner","-i",str(video),
                        "-vf","blackdetect=d=0.9:pix_th=0.04:pic_th=0.99",
                        "-an","-f","null","-"],text=True,capture_output=True)
    if proc.returncode!=0:
        print(proc.stderr[-2500:])
        raise RuntimeError("Full video decode failed")
    blackspots=re.findall(r"black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)\s+black_duration:\s*([\d.]+)",proc.stderr)
    if blackspots:
        print("BLACK_SPOTS:",blackspots)
        raise RuntimeError("Black video segment detected; do not publish")
    stamp=[2,8,17,24,33,42,48]
    frames=[]
    scores={}
    for t in stamp:
        f=WORK/f"proof_{t:02}.jpg"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(t),"-i",str(video),"-frames:v","1","-q:v","3",str(f)])
        im=Image.open(f).convert("RGB")
        brightness=ImageStat.Stat(im.convert("L")).mean[0]
        visible=sum(1 for p in im.convert("L").resize((90,160)).getdata() if p>16)/(90*160)
        scores[str(t)]={"mean_luma":round(brightness,2),"visible_pixel_share":round(visible,4)}
        print("FRAME",t,"LUMA",brightness,"VISIBLE",round(visible,3),flush=True)
        if visible<0.05 or brightness<4:
            raise RuntimeError("Frame "+str(t)+" is black / missing")
        im.thumbnail((270,480))
        frames.append((t,im.copy()))
    sheet=Image.new("RGB",(270*4,520*2),(15,21,30))
    dr=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(FONT_BOLD,21)
    for i,(t,img) in enumerate(frames):
        x=i%4*270;y=i//4*520
        sheet.paste(img,(x,y))
        dr.text((x+12,y+481),f"{t:02d}s - VAIZDAS",font=font,fill=(255,255,255))
    sheet.save(OUT/"KADRU_PATIKRA.jpg",quality=90)
    report={"filename":video.name,"duration_seconds":duration,"width":v["width"],"height":v["height"],
            "has_audio":True,"black_spans":[],"verified_frames":scores,"result":"PASS - complete animated imagery throughout"}
    (OUT/"PATIKRA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps(report,ensure_ascii=False),flush=True)
    return report

if __name__=="__main__":
    movie=render()
    validate(movie)
    print("RENDER_AND_QA_SUCCESS",str(movie),flush=True)

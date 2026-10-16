#!/usr/bin/env python3
"""Produce a playable single 52-second Next Life RP.lt ad from existing Runway shots.

Strict media validation, full-frame decode, black span detection, and frame proofs.
No new AI requests or paid model generations are made by this renderer.
"""
from pathlib import Path
import json
import math
import re
import shutil
import subprocess
import time
import urllib.request
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "media"
OUT = ROOT / "output"
SRC.mkdir(exist_ok=True, parents=True)
OUT.mkdir(exist_ok=True, parents=True)
OUTFILE = OUT / "NEXT_LIFE_RP_LT_VIENTISA_REKLAMA_52s.mp4"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SHOTS = [("shot01_home.mp4",8),("shot02_car_pickup.mp4",10),("shot03_car_conversation.mp4",10),
         ("shot04_mechanic.mp4",10),("shot05_friends.mp4",10)]
TITLE_SECONDS = 4

def run(command, capture=False):
    command = [str(arg) for arg in command]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None)
    if result.returncode:
        if capture:
            print((result.stderr or "")[-4000:], flush=True)
        raise RuntimeError("Nonzero exit code "+str(result.returncode)+": "+" ".join(command[:6]))
    return result.stdout if capture else None

def download(name, url):
    path = SRC/name
    if path.exists() and path.stat().st_size>10000:
        return path
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
            with urllib.request.urlopen(req,timeout=100) as source, open(path,"wb") as dest:
                if source.status!=200:
                    raise RuntimeError("HTTP "+str(source.status))
                shutil.copyfileobj(source,dest,length=1024*1024)
            if path.stat().st_size<10000:
                raise RuntimeError("File too short")
            print("DOWNLOADED",name,path.stat().st_size,flush=True)
            return path
        except Exception as exc:
            path.unlink(missing_ok=True)
            print("RETRY",name,attempt+1,str(exc)[:200],flush=True)
            if attempt==3: raise
            time.sleep(2+attempt*2)

def probe(path):
    return json.loads(run(["ffprobe","-hide_banner","-v","error","-show_streams",
                           "-show_format","-of","json",str(path)],capture=True))

def validate_sources():
    for fname,dur in SHOTS:
        p=SRC/fname
        details=probe(p)
        videos=[x for x in details["streams"] if x.get("codec_type")=="video"]
        audios=[x for x in details["streams"] if x.get("codec_type")=="audio"]
        size=(videos[0].get("width"),videos[0].get("height")) if videos else None
        length=float(details["format"]["duration"])
        print("SOURCE",fname,"DURATION",length,"SIZE",size,"AUDIO",len(audios)>0,flush=True)
        if not videos or not audios or length<dur-0.4 or size[0]<700 or size[1]<1200:
            raise RuntimeError("Bad source: "+fname)
        snap=SRC/(fname+".jpg")
        run(["ffmpeg","-hide_banner","-loglevel","error","-y",
             "-ss",str(dur/2),"-i",str(p),"-frames:v","1",str(snap)])
        avg=ImageStat.Stat(Image.open(snap).convert("L")).mean[0]
        if avg<3:
            raise RuntimeError("Source file appears black: "+fname)
    for fname in ["music.mp3","endfx.mp3"]:
        a=probe(SRC/fname)
        if not any(s.get("codec_type")=="audio" for s in a["streams"]):
            raise RuntimeError("Missing audio: "+fname)

def poster():
    """Generate exact readable typography over the ACTUAL last scene, not hallucinated lettering."""
    bg=SRC/"lastframe.jpg"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss","9.25",
         "-i",str(SRC/"shot05_friends.mp4"),"-frames:v","1",str(bg)])
    image=Image.open(bg).convert("RGB")
    image=ImageOps.fit(image,(1080,1920),method=Image.Resampling.LANCZOS)
    image=image.filter(ImageFilter.GaussianBlur(13))
    image=ImageEnhance.Brightness(image).enhance(.33).convert("RGBA")
    shading=Image.new("RGBA",(1080,1920),(5,11,26,95))
    image=Image.alpha_composite(image,shading)
    dr=ImageDraw.Draw(image,"RGBA")
    dr.rounded_rectangle((72,660,1008,1320),radius=31,fill=(1,6,18,144),outline=(204,172,105,155),width=2)
    dr.line((284,786,796,786),fill=(218,188,126,190),width=4)
    title="NEXT LIFE RP.lt"
    s=103
    f=ImageFont.truetype(FONT_BOLD,s)
    while dr.textbbox((0,0),title,font=f)[2]>890:
        s-=2
        f=ImageFont.truetype(FONT_BOLD,s)
    def draw_center(txt,at,font,color):
        bounds=dr.textbbox((0,0),txt,font=font)
        x=int((1080-(bounds[2]-bounds[0]))/2)
        dr.text((x+2,at+5),txt,font=font,fill=(0,0,0,150))
        dr.text((x,at),txt,font=font,fill=color)
    draw_center(title,873,f,(255,255,255,255))
    draw_center("Tavo istorija prasideda čia.",1047,
                ImageFont.truetype(FONT_REG,44),(236,237,240,255))
    dr.line((300,1191,780,1191),fill=(218,188,126,170),width=3)
    dst=SRC/"title_verified.png"
    image.convert("RGB").save(dst,compress_level=4)
    print("FINAL TITLE EXACT: NEXT LIFE RP.lt",flush=True)
    return dst

def render():
    urls=json.loads((ROOT/"asset_urls.json").read_text(encoding="utf-8"))
    needed=[name for name,dur in SHOTS]+["music.mp3","endfx.mp3"]
    for filename in needed:
        if not urls.get(filename):
            raise RuntimeError("Missing asset URL for "+filename)
        download(filename,urls[filename])
    validate_sources()
    card=poster()
    ins=[]
    for name,duration in SHOTS:
        ins.extend(["-i",str(SRC/name)])
    ins.extend(["-loop","1","-framerate","30","-t",str(TITLE_SECONDS),"-i",str(card)])
    ins.extend(["-i",str(SRC/"music.mp3"),"-i",str(SRC/"endfx.mp3")])
    filter_lines=[]
    for i,(name,dur) in enumerate(SHOTS):
        filter_lines.append(
            f"[{i}:v]trim=duration={dur},setpts=PTS-STARTPTS,fps=30,"+
            "scale=1080:1920:flags=lanczos:force_original_aspect_ratio=decrease,"+
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{i}]"
        )
        filter_lines.append(
            f"[{i}:a]atrim=duration={dur},asetpts=PTS-STARTPTS,aresample=48000,"+
            "aformat=channel_layouts=stereo,volume=1.04"+f"[a{i}]"
        )
    filter_lines.append("[5:v]trim=duration=4,setpts=PTS-STARTPTS,fps=30,scale=1080:1920,setsar=1,format=yuv420p[card]")
    filter_lines.append("".join(f"[v{i}]" for i in range(5))+"[card]concat=n=6:v=1:a=0[vc]")
    filter_lines.append(
      "[vc]drawtext=fontfile="+FONT_BOLD+":text='NEXT LIFE RP.lt':fontcolor=white@0.96:"+
      "fontsize=47:shadowcolor=black@0.85:shadowx=3:shadowy=3:"+
      "box=1:boxcolor=black@0.40:boxborderw=15:x=(w-text_w)/2:y=h-490:"+
      "enable='between(t,6.15,7.95)',format=yuv420p[vout]"
    )
    filter_lines.append("".join(f"[a{i}]" for i in range(5))+"concat=n=5:v=0:a=1[native]")
    filter_lines.append("[6:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration=52,"+
                        "asetpts=PTS-STARTPTS,volume=0.13,afade=t=in:st=0:d=1.4,"+
                        "afade=t=out:st=48:d=4[music]")
    filter_lines.append("[7:a]aresample=48000,aformat=channel_layouts=stereo,"+
                        "atrim=duration=4,asetpts=PTS-STARTPTS,volume=0.30,afade=t=out:st=2.9:d=1.1[end]")
    filter_lines.append("[native][end]concat=n=2:v=0:a=1[dialog]")
    filter_lines.append("[dialog][music]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0,"+
                        "alimiter=limit=0.93,atrim=duration=52,aresample=48000[aout]")

    run(["ffmpeg","-hide_banner","-loglevel","warning","-stats","-y",*ins,
         "-filter_complex",";".join(filter_lines),"-map","[vout]","-map","[aout]",
         "-c:v","libx264","-preset","veryfast","-crf","18","-profile:v","high",
         "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","192k",
         "-t","52","-movflags","+faststart",str(OUTFILE)])
    return OUTFILE

def inspect(path):
    check=probe(path)
    vids=[s for s in check["streams"] if s["codec_type"]=="video"]
    audio=[s for s in check["streams"] if s["codec_type"]=="audio"]
    dur=float(check["format"]["duration"])
    print("FINAL MP4",str(path),"BYTES",path.stat().st_size,"TIME",dur,"V",len(vids),"A",len(audio),flush=True)
    if not(51.5<=dur<=52.4 and vids and audio and vids[0]["width"]==1080 and vids[0]["height"]==1920 and path.stat().st_size>12000000):
        raise RuntimeError("FINAL LENGTH / VIDEO / AUDIO validation FAILED")
    result=subprocess.run(["ffmpeg","-hide_banner","-i",str(path),
                           "-vf","blackdetect=d=0.65:pix_th=0.035:pic_th=0.995",
                           "-f","null","-"],capture_output=True,text=True)
    if result.returncode:
        print(result.stderr[-4000:])
        raise RuntimeError("Whole MP4 decode failed")
    blackspots=re.findall(r"black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)\s+black_duration:\s*([\d.]+)",result.stderr)
    if blackspots:
        print("BLACK_SPOTS",blackspots,flush=True)
        raise RuntimeError("UNACCEPTABLE: black video spans detected")
    stamp=[1.5,5,9,13,17,21,26,31,36,40,45,49,51]
    proofs=[]
    brightness={}
    for t in stamp:
        file=SRC/("proof_"+str(t)+".jpg")
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(t),
             "-i",str(path),"-frames:v","1",str(file)])
        img=Image.open(file).convert("RGB")
        lumi=img.convert("L")
        avg=ImageStat.Stat(lumi).mean[0]
        visible=sum(1 for p in lumi.resize((90,160)).getdata() if p>14)/(90*160)
        brightness[str(t)]={"average_luma":round(avg,2),"visible_pixels":round(visible,3)}
        print("PROOF",t,round(avg,2),round(visible,3),flush=True)
        if avg<4 or visible<0.06:
            raise RuntimeError("Blank sample frame at "+str(t))
        img.thumbnail((216,384))
        proofs.append((t,img))
    sheet=Image.new("RGB",(216*5,420*3),(18,24,35))
    dr=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(FONT_BOLD,18)
    for k,(t,img) in enumerate(proofs):
        x=(k%5)*216;y=(k//5)*420
        sheet.paste(img,(x,y))
        dr.text((x+8,y+386),f"{t:04.1f} s",font=font,fill=(255,255,255))
    sheet.save(OUT/"FILMO_KADRU_PATIKRA.jpg",quality=92)
    report={"status":"PASS_VIDEO_DECODE_NO_BLACK_SPANS","video":path.name,
            "seconds":dur,"width":1080,"height":1920,"audio_present":bool(audio),
            "black_spans":[],"sample_frames":brightness,
            "note":"Technical full-video check only; verify dialogue-to-lips and scene-action alignment by viewing the film."}
    (OUT/"PATIKROS_REZULTATAS.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("VERIFIED FINAL VIDEO WITHOUT BLACK SPANS",flush=True)

if __name__=="__main__":
    movie=render()
    inspect(movie)
    print("RENDER_AND_FULL_DECODE_QA_PASS",str(movie),flush=True)

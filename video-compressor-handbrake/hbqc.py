#!/usr/bin/env python3
"""
    Handbrake (json) Queue Creator
    last updated: 2021/oct/9 iexa
    
    changelog:
    - 21/oct/9:  open hb.json file in utf8 encoding to be sure
    - 21/jul/15: added rotation check
    - 21/jun/23: added ffmpeg automatic resolution sniffing
"""
import argparse
import base64
import bz2
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from string import Template


class HandBrakeJSON:
    """ Holds json settings file that is used as a template. """

    template = b"LRx4!F+o`-Q&}7?B<lbH#9x3_P*i7sazF3?>Ob$_`cMU4Hv!$6h?<$3W>h5vLS(?2r?oIfO)_eFnldzK02(v^)M+MadVm=K01SZBKs3+;KnYC*Ax)&38YaqZ5w$%GMw){G28?LR9AwF+m`sd;ff$-FMi6Mz00IdV6u~L&42nFbsp+Yvjf!YAJwP;Rp`i5`1cVlGYu=a$gAki-3;kh{oEntc29rSeQ4%dI?I=2G5CT@DgbaF;LDs<p(9kyPf<R4)Iee>!VcJYex<b~7LIA8$OjRf-^q}n^$x9zi3JBdvfDQ~02;;f}%aJUF;d*cOaWd=coW!G@5tqy5CWY;s-W_b*yjhBfhc>^N>w7FczG0ByX``6>sz|kb{G4f%0^d0~CFL$e#G#=Q%$cA-B+QWE0-^~{ARRO*hYEKIWY8*iigHr|VYrzd9wIzi@-A3)zO0KsGsivR5q5ZtL#cB8aZ@!G9$KJ<5YU>PB@qceB+XVx3s?}DE4^9Rl2@jpxNVm#<6IpXV3aO|HPGmkJG(f9hew<+MnIk-5^!WZ$`9vZt?Buyyb>2~x)Wt<)@qy4TUr1Op#dap=<hx!yN2Fsw*bQJn@FUm*-DNU-=!Mor!2Y;c($5i52vBwG1NQmoqOAN5&KvU6;%6maK6ahm7Qx69V@#}H+boD@<-BLk_NiGHP#?fsg`)X$c~a&u(0iw&*;76)bQW)y>dBGMB(;%=Y<>E&f0pV0?`|)1E}g8ZtdKmGa+t%4mbU?LF$pPc6F;23pEgl0ZWaJ{T!@`o|;YQcK3E9Fp;YcMdmsr4QC{IM?3yV2Y`g4$$=@mz+(j5p<;2{=>(+Xw!WoR6pe0TR8h@Ewx&@M*=QYlgw~$8n03yrZVec{ytNT)oOH@lib+5$Q?o)PH-Qk6hBHk-ARJ->2;-ZI%={X&aVGNb*t8#{w`_=qf{MuukO_mbvdR{1H9J{nos5SIz+`qCIzfgU#+MK!l<}1s>KFH!wbN%|HD@tkM#)1RpmI#xl?E0Dj6^(|hNemAK~*mcTrPp6yg5zi2^#;nVf)QdAxW}65=5I+LmIW6D=1#5>9FCP=Z0WE#0M+Y&y?bvNiWj}=r#433G)Rx$plg&dN~UnAjGGZ*l{V+>kNGaw4ApQXt!JzRhi|T;$6#iQLmX`AWk(5-Ga8DA|X(SpeVCj9r3my=wgmyA)+5a9%}+oPHm}&>4>NO*nLy@X7`p25rXiM+hq{KSz`xcYJl12g60xMOTu>?4NNudY#4&x8TaW-5tIh64k;i~6$vpw9dK8dR7#wIppGp(5`!lB3}-z14sF>)F5TbJnuEl%2BF?WOBo7D`8f^Mvpxd|hT)_%k%+Qmp*k>60C0A1s4jUtdt+M5z)($S<R(Uim`da#JubU*J1!UqRT?*iIi}D!sEE6l83Zb)7DSLlVG^o`mSi^kSGozRTUPH7xb;M$YDpE5;OR1rGK?D*Mnq5<5W5LQ^WJZ}*NIqF3LwPC&w$1g(!&`ZnUXyyR@q$D7Z{A?_h=C@DP2fyr$(@*%x6kSv59?F8qkIgT5p5nvWHC;WEhnNQB?}2>$!R3QYoY|C`wk04Q24Kd+ZG;Uzg5@4&MeR1K6BYPYG<<{}*yaI8cxrE+p#"
    ffprobe = 'ffprobe -loglevel panic -select_streams v:0 -show_streams -print_format json'

    @classmethod
    def encode(cls, args):
        if args.dir.is_file():
            try:
                with open(args.dir, "r") as file:
                    data = file.read()
            except FileNotFoundError:
                sys.exit("file to be encoded not found - you can use stdin too")
        else:
            data = "".join([x for x in sys.stdin])
        return base64.b85encode(bz2.compress(bytes(data, "utf8")))

    @classmethod
    def decode(cls):
        return bz2.decompress(base64.b85decode(cls.template)).decode("utf8")

    @classmethod
    def parse(cls, context) -> str:
        """Template must have these markers:
        # ${in}, ${out}, ${fps}, TODO ${skip}, ${resx}, ${resy}
        """
        t = cls.decode()
        # check for every file... if automatic res.
        if context['res'].startswith('auto'):
            if not Path(context['in']).is_file():
                raise RuntimeError(f"ERROR {context['in']} is not accessible! Exit.")
            print(".", end="", flush=True)
            vid_info = subprocess.check_output([*cls.ffprobe.split(), context['in']], encoding='utf8')
            vid_info = json.loads(vid_info)
            if 'streams' not in vid_info or not vid_info['streams']:
                raise RuntimeError(f"ERROR {context['in']} has no valid video stream! Exit.")
            vid_info = vid_info['streams'][0]
            context['resx'], context['resy'] = vid_info['width'], vid_info['height'] # or coded_width/height
            # check of video is rotated by 90 degrees and modify width/height if so
            if vid_info.get('tags') != None and (rot := vid_info['tags'].get('rotate')) != None:
              try:
                if abs(int(rot)) == 90:
                  context['resx'], context['resy'] = context['resy'], context['resx']
              except ValueError:
                pass # I know it's bad habit but there is really nothing to do if value is invalid
            if context['res'] == 'auto-half':
                context['resx'], context['resy'] = context['resx'] // 2, context['resy'] // 2
        else:
            context["resx"], context["resy"] = context.get("res").split("x")
        # for windows it is definitely required for posix maybe not
        context["in"] = str(context["in"]).replace("\\", "\\\\")
        context["out"] = str(context["out"]).replace("\\", "\\\\")
        return Template(t).substitute(context)


class HandBrakeQueue:
    """
    Create a new JSON Handbrake config file for a folder tree of files
    using specific settings for high efficiency encoding.
    If DIR_OUT option is used and is different than DIR then all non-encoded files are
    first copied to the encoded files dir.
    -
    Resolutions can now be set to auto or auto-half - this requires ffprobe to be
    installed on your system - and will automatically set the resolutions based on the
    original video, or in case of auto-half to half the size of it (half width and height).
    Note that using this option will slow down the process as every video file will be checked.
    """

    def __init__(self):
        p = argparse.ArgumentParser(description=self.__doc__)
        p.add_argument(
            "dir",
            nargs="?",
            default=Path("."),
            type=Path,
            help="path to input files root, defaults to current dir",
        )
        p.add_argument(
            "dir_out",
            nargs="?",
            default=None,
            type=Path,
            help="path to out encoded files, defaults to DIR",
        )
        p.add_argument(
            "hbconf_file",
            nargs="?",
            type=Path,
            default=None,
            help="name of generated hb queue json file, defaults to DIR_OUT/hb.json",
        )
        p.add_argument(
            "-e",
            default="mp4 mov ts".split(" "),
            action="append",
            help="allowed video exts, defaults to (mp4 mov ts) can spec. multiple",
        )
        # p.add_argument(
        #     "--skip",
        #     default=0,
        #     type=int,
        #     help="TODO skip 1st SKIP seconds from all vids, defaults to 0",
        # )
        p.add_argument(
            "--fps",
            default=10,
            type=int,
            choices=(5, 10, 12, 15, 20, 25),
            help="out fps of videos, defaults to 10",
        )
        p.add_argument(
            "--res",
            default="1280x720",
            choices=["auto", "auto-half", "1280x720", "1440x810"],
            help="out res. of videos, defaults to 1280x720, can be set to auto or auto-half",
        )
        # advanced options to help encode / decode built-in json template
        group = p.add_argument_group(
            "advanced options", "to handle built-in hb json template"
        )
        group.add_argument("--template_enc", action="store_true")
        group.add_argument("--template_dec", action="store_true")
        self.args = p.parse_args()
        self.check_template_commands()
        self.check_for_ffprobe(self.args.res)

        dir_in = self.args.dir
        if not dir_in.is_absolute():
            dir_in = dir_in.resolve()  # DOES NOT WORK WITH RAMDISK on windows OSError 1!
        dir_out = self.args.dir_out if self.args.dir_out else dir_in
        if not dir_out.is_absolute():
            try:
                dir_out = dir_out.resolve(
                    strict=True
                )  # same as above, windows ramdisk bug
            except FileNotFoundError:
                sys.exit(f'Please create the DIR_OUT "{dir_out}" before using it!')
        files_all = self.gather_files(dir_in)
        files_req = self.gather_files(dir_in, self.args.e)
        files_diff = set(files_all) - set(files_req)
        if not files_req:
            sys.exit("No files found to be encoded. Use -h for help.")
        if dir_in != dir_out:
            self.copy_out_files_and_dirs(dir_in, dir_out, files_diff)
            self.copy_out_files_and_dirs(dir_in, dir_out, files_req, only_make_dirs=True)
        hbconf_file = dir_out / "hb.json"
        if self.args.hbconf_file:
            hbconf_file = self.args.hbconf_file
        self.create_hbconf_file(dir_in, dir_out, hbconf_file, files_req)
        print("Done.")
        sys.exit(0)

    def create_hbconf_file(self, dir_in, dir_out, hbconf, files):
        print(f"#{len(files)} found to be encoded")
        with open(hbconf, "w", encoding='utf8') as file:
            file.write("[\n")
            for f in files:
                ctx = {
                    "in": f,
                    "out": dir_out / f.relative_to(dir_in).with_suffix(".m4v"),
                    "res": self.args.res,
                    "fps": self.args.fps,
                    # "skip": self.args.skip,
                }
                file.write(HandBrakeJSON.parse(ctx))
            file.write("]")

    def copy_out_files_and_dirs(self, dir_in, dir_out, files, only_make_dirs=False):
        if dir_in == dir_out or not files:
            return
        if not only_make_dirs:
            print(f"#{len(files)} files are not to be encoded copying to {dir_out}")
        for f in files:
            out_file = dir_out / f.relative_to(dir_in)
            if not out_file.parent.exists():
                out_file.parent.mkdir(parents=True)
            if not only_make_dirs:
                shutil.copyfile(f, out_file)

    def gather_files(self, root, extensions=None):
        reg_p = None
        if extensions:  # case-insensitive exts
            reg_p = re.compile(rf".({'|'.join(extensions)})$", re.I)
        # all_files = [file for x in extensions for file in root.rglob(f"*.{x}")]
        files = [
            x for x in root.rglob("*") if reg_p is None or reg_p and reg_p.search(str(x))
        ]
        return [f for f in files if f.is_file()]

    def check_template_commands(self):
        if self.args.template_enc:
            print(HandBrakeJSON.encode(self.args))
            sys.exit(0)
        if self.args.template_dec:
            print(HandBrakeJSON.decode())
            sys.exit(0)

    def check_for_ffprobe(self, res_string):
        if res_string.startswith('auto') and not shutil.which('ffprobe'):
            sys.exit('To use auto resolutions ffprobe (ffmpeg) needs to be installed!')


if __name__ == "__main__":
    HandBrakeQueue()
    
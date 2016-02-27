WinFile - A powerful Symbian S60 filemanager written in PyS60 language

```
print "Welcome in the WinFile world!!"
return "Thanks!"
```

# Introduction #

This is a great filemanager (for me, well not surprising :=) ) not only for file management but to quick play audio files and see my pictures :) (I have to say that for hex editing and quick in-use-file copy I still use X-Plore and the great Fexplorer, the first and the most easy).
I think there's not a perfect software with everything you need, but why don't use various tools?
So, download WinFile and test it carefully!
The project started in the end of 2007. The idea came from a little script made by atrant: it was a little graphical file viewer, without any possible operation.
The first WinFile 0.1 was released 20th January 2008 and today we reached the version 1.05.3, the 13th release.
Feature by feature, it is now a little "Swiss Knife". But there is a lot of work to do.
The most important feature that's in development is the full compatibility with new Symbian editions.

Thank You,

> Lorenzo, aka MemoryN70

# Features #

Some of the main features are
  * Customizable skins
  * Big icons
  * Image viewer, Audio player, and text viewer
  * Plugin support (to enhance WinFile capabilities)
  * Lots of settings, customizable color font
  * Custom UI (no S60 UI like menus and lists)
  * Detailed description on various file types (mp3,zip,rar,sis,jar,jpg(exif))
  * System informations
  * Ram cleaner, bluetooth switch, and system restart
  * Simple file cryptation system
  * Java applications list for quick send over BT, possibility to create a report on every application installed on the phone (Sis and Java)
  * ...and much much more ;)!

# Downloads #

Go here to browse every version since 0.1! (2nd edition only)

[WinFile Museum](http://code.google.com/p/winfiles60/source/browse/#svn/trunk/releases)

# System requirements #

  * Python runtime installed (optionally with some module pack installed)
  * About 10 mb of ram free during runtime (minimum 5), depending on the machine
  * Some space free on the memory card or C: drive (at least 5 mb)
  * Symbian OS S60 2nd edition (6600([1](1.md)), 6630, 6680, N70, ...)
  * Symbian 3rd - 5th edition support is under developement
  * Some features of the programm need to have a little free space on D: drive. When the software won't start, simply restart the phone (it is very very rare, tough)

[1](1.md) It seems that WinFile works good in a 6600 only if it's installed the python runtime for the FP2 S60 version. With this version the only problem occurs with the camera module: simply extract it from the python for FP1 and copy it in system\libs!

# File browsing & management #

  * Normal file/folder operations like rename, delete, copy and cut
  * Simple cryptography: just to hide some files, without password
  * Received files from bluetooth, mms or irda
  * Tasks and processes management (kill and switch)
  * File search: jolly characters are supported (more to come like date/time/size search)
  * Attributes editor, possibility to apply attribs for every file and sub directory of a folder
  * Plugins support: there are now more than 9 plugins like the zip/jar explorer, sis explorer, vcf viewer, mbm/ota/gif viewer/extractor, arc bakup reader, skn editor, aif viewer/extractor

# Tools #

  * Bluetooth switching
  * Ram cleaner
  * System info
  * Java applications listing (quick send over bt)
  * Sis & Java application report writer
  * Debug log viewer
  * System (soft) restart

# Audio Player #

  * Supports every format which is supported by your phone or you've added with a plugin!
  * Supports .lrc (lyrics) files: they are shown synchronized with song time.
  * It is possible to hide the player and continue file browsing without stopping the song
  * Simple repeat / shuffle options

# Image viewer #

  * It's a fast image viewer!
  * Supports image zooming (different options)
  * Detailed information on image loaded
  * Brightness control
  * Possibility to open directly Editor Application

# Text viewer #

  * A simple text viewer (to be enhanced in the future releases)
  * Wrap to screen function
  * Search function
  * Goto line...
  * Fast scroll, page or line by line

# Informations about files, folders and system #

  * Complete information about a dozen of file types including: mp3, ogg, txt, jar, sis, jpg(exif), zip, rar, m3u, pyl(well not a famous ext...my old pyplayer), and others.
  * ID3v1 tag editor for mp3 files
  * Detailed infos for drives like mmc and mass storage.

Ascci logo ;)
```
BBMBBBBBMBBBBBBBMBBBBBBBBBBBMBBB8ENqGBMBBBBBBBBBMMBBBBBBBBBBMMOBMBBBMBMMN88OX
BBBOLrMBBBB0rJBBBBB1rSBk..0BBMZEMBB0MBBBMYL7riirOB7 iMBv  BBONE0OGMMBM00BMBMB
MBBB   MBBBi  iBBBB  :Bq  1BBMBBBBBBBBBBF       1Br  8BZ  SBBBBBBBBBBB0OBBMBM
XBBBB  .BBB.   YBBB  jBBS:NBBu:jF. .YBBBB  FBBBBBBBriMBB. iBBBBj.  :SBBPMMBMM
;BBBBO  iBB  :  0BG  GBBi  BBj    .   MBB: :ZMNqZBE  iBBr  BBM  .u7  :MBqZq00
.BBBBBF  GB  B2  BS .BBBF  PBZ  rBBB  iBBu       EBv  BBq  GB7  L5F:  :BMMBMB
 ZBBMBBY  7  BB. :: :BBBM  rBB: ,BBBr  BBO  UBBMNBBN  MBB  JBP   i.::iYOMBMBM
 JBBBBBB;   .BBB    LBBOB.  BBv  OBBZ  XBB. :BBBBZBB  rBB. .BB:  ZBBBN1EBMBMM
 :BBMBBBB:  :BBBN   XBBBBY  GB1  JBBB  YBBi  NBBMGBB:  BBU  ZBBL       ZBBMBM
BBBBBBBBBBBMBBBBBBBBBBBMBBMOBBME8BBBBBMBBBBOMBBBBZPEB8MBBBM8BBBBBMqFPPBBBMBMB
```
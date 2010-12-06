'''

The idea is to join graphics files loading and theme colors loading, in order to load everything at winfile start.
This is not only better to avoid bugs, but in order to define other usefull definitions like: some renamed files, different mask size, no mask support etc...

15/07/2010
'''

class SknInfo:
    def __init__(s, skn):
        s.skin_path=skn
        s.name=''
        s.author=''
        s.version=0.0
        s.description=''
        s.docpath=None
        s.winfile_version=1.054
        

class Theme_Handler(object):
    skn_begin="WF_SKIN_FILE_BEGIN"
    skn_end="WF_SKN_FILE_END"

    
    def load(s):
        fo = open( s.skin_path, 'rb' , 100)
        if fo.read(len(skn_begin))!=skn_begin:
            raise "Invalid skin file: invalid header"
        if fo.read(-len(skn_end), 2)!=skn_end:
            raise "Invalid skin file: truncated file"

class SVG:

    def __init__(s, path, size):
        

class _grafica:
    def boot(s):
        try:
            s.load()
        except:
            try:
                #Qui potrebbe essere solo un problema della directory "temporanea"
                s.load(1)
            except:
                #Il tema è di sicuro danneggiato, verifichiamo se ce ne sono altri, altrimenti l'applicazione avvisa e si chiude
                try:
                    os.remove(directory.theme_file)
                    #print "theme.dat eliminato"
                except:
                    pass
                try:
                    for path in os.listdir(directory.allskin_dir):
                        try:
                            l=os.listdir(directory.allskin_dir+"\\"+path)
                            l=map(lambda x: x.lower(),l)
                        except: continue
                        if ("ui.zip" in l) and ("icons.zip" in l) and ("theme_prop.ini" in l):
                            settings.skin=[path,path]
                            break
                    s.load(1)
                except:
                    appuifw.note(u"Nessun tema!\nNo themes!\nKeine Themen!")
                    appuifw.note(u"Installarne uno!\nInstall one!\nBitte eine installieren!")
                    #appuifw.note(u"Low Memory on D:? Try to restart!")
                    g=gestore_temi(no_load=1)
                    g.install()
                    try:
                        for path in os.listdir(directory.allskin_dir):
                            try:
                                l=os.listdir(directory.allskin_dir+"\\"+path)
                                l=map(lambda x: x.lower(),l)
                            except: continue
                            if ("ui.zip" in l) and ("icons.zip" in l) and ("theme_prop.ini" in l):
                                settings.skin=[path,path]
                                break
                        s.load(1)
                    except:# Exception,e:
                        #print str(e)
                        #print settings.skin
                        settings.path_color=0xff0000
                        user.note(u"Impossibile avviare il programma.\nNessun tema è installato o disponibile per l'utilizzo.\nOppure una o più memorie (utente, D: o ram) sono piene.\nProvare a riavviare il telefono.",u"Fatal Error",-1)
                        sys.exit()
                    del g
                    #appuifw.app.set_exit()
    def load(s,force=0):
        if (not os.path.exists(directory.skin_dir)) or force:
            #print "Lettura file zip"
            unzip().extract("%s\\%s\\ICONS.zip"%(directory.allskin_dir,settings.skin[1]),directory.skin_dir)
            #print "Icone estratte"
            #user.direct_note(u"Icone estratte",u"Caricamento...")
            unzip().extract("%s\\%s\\UI.zip"%(directory.allskin_dir,settings.skin[0]),directory.skin_dir)
            #user.direct_note(u"UI estratto",u"Caricamento...")
            #print "UI estratto"
            #d=progress_dialog(u"Caricamento tema...",u"Avviamento WinFile",max=48)
            #d.draw()
        # for i in s.theme_files:
            # exec("""%s=Image.open("%s")"""%(var,path))
        # return
        # for var,path in [("s.spuntoimg","spunto.png"),
                        # ("s.appimg","Application.png"),
                        # ("s.file_img","File.png"),
                        # ("s.bg_img_normal","Sfondo.jpg"),
                        # ("s.bg_img_landscape","Sfondo_LS.jpg"),
                        # ("s.csel_img_normal","selezione.jpg"),
                        # ("s.csel_img_landscape","selezione_LS.jpg"),
                        # ("s.csel_img_mask_normal","selezione_mask.bmp"),
                        # ("s.csel_img_mask_landscape","selezione_mask_LS.bmp"),
                        # ("s.cartella_img","Cartella.png"),
                        # ("s.dll_img","dll.png"),
                        # ("s.ingranaggio_img","ingranaggio.png"),
                        # ("s.internet_img","internet.png"),
                        # ("s.mmc_img","mmcmemory.png"),
                        # ("s.tel_img","telmemory.png"),
                        # ("s.musica_img","musica.png"),
                        # ("s.mail_img","Mail.png"),
                        # ("s.ram_img","rammemory.png"),
                        # ("s.rom_img","rommemory.png"),
                        # ("s.video_img","video.png"),
                        # ("s.immagine_img","immagine.png"),
                        # ("s.settings_img","settings.png"),
                        # ("s.archive_img","Archivio.png"),
                        # ("s.vcf_img","Vcf.png"),
                        # ("s.sis_img","Sis_installer.png"),
                        # ("s.text_img","testo.png"),
                        # ("s.pycon_img","Python.png")]:
            # try:
                # exec("""%s=Image.open("D:\\winfile_theme\\%s")"""%(var,path))
                # e32.ao_yield()
            # except Exception,e: print str(e),path
        # sys.exit()
        
        #user.direct_note(u"Caricamento grafica in memoria...",u"Caricamento...")
        s.spuntoimg=Image.open(directory.skin_dir+"\\spunto.png")
        #d.forward();d.draw()
        s.appimg=Image.open(directory.skin_dir+"\\Application.png")
        #d.forward();d.draw()
        s.file_img=Image.open(directory.skin_dir+"\\File.png")
        #d.forward();d.draw()
        s.bg_img_normal=Image.open(directory.skin_dir+"\\Sfondo.jpg")
        #d.forward();d.draw()
        s.bg_img_landscape=Image.open(directory.skin_dir+"\\Sfondo_LS.jpg")
        #d.forward();d.draw()
        s.csel_img_normal=Image.open(directory.skin_dir+"\\selezione.jpg")
        #d.forward();d.draw()
        s.csel_img_landscape=Image.open(directory.skin_dir+"\\selezione_LS.jpg")
        #d.forward();d.draw()
        s.csel_img_mask_normal=Image.open(directory.skin_dir+"\\selezione_mask.bmp")
        #d.forward();d.draw()
        s.csel_img_mask_landscape=Image.open(directory.skin_dir+"\\selezione_LS_mask.bmp")
         #d.forward();d.draw()
        s.cartella_img=Image.open(directory.skin_dir+"\\Cartella.png")
         #d.forward();d.draw()
        # s.cartellaimg_img=Image.open(directory.skin_dir+"\\Cartella_immagini.png")
        # s.cartellaaudio_img=Image.open(directory.skin_dir+"\\Cartella_musica.png")
        # s.cartellavideo_img=Image.open(directory.skin_dir+"\\Cartella_video.png")
        # s.cartellainstall_img=Image.open(directory.skin_dir+"\\Cartella_install.png")
        s.dll_img=Image.open(directory.skin_dir+"\\dll.png")
         #d.forward();d.draw()
        #s.cartellafont_img=Image.open(directory.skin_dir+"\\font.png")
        s.ingranaggio_img=Image.open(directory.skin_dir+"\\ingranaggio.png") #;d.forward();d.draw()
        s.internet_img=Image.open(directory.skin_dir+"\\internet.png") #;d.forward();d.draw()
        s.mmc_img=Image.open(directory.skin_dir+"\\mmcmemory.png") #;d.forward();d.draw()
        s.tel_img=Image.open(directory.skin_dir+"\\telmemory.png") #;d.forward();d.draw()
        s.musica_img=Image.open(directory.skin_dir+"\\musica.png") #;d.forward();d.draw()
        s.mail_img=Image.open(directory.skin_dir+"\\Mail.png") #;d.forward();d.draw()
        s.ram_img=Image.open(directory.skin_dir+"\\rammemory.png") #;d.forward();d.draw()
        s.rom_img=Image.open(directory.skin_dir+"\\rommemory.png") #;d.forward();d.draw()
        s.video_img=Image.open(directory.skin_dir+"\\video.png") #;d.forward();d.draw()
        s.immagine_img=Image.open(directory.skin_dir+"\\immagine.png") #;d.forward();d.draw()
        s.settings_img=Image.open(directory.skin_dir+"\\settings.png") #;d.forward();d.draw()
        s.archive_img=Image.open(directory.skin_dir+"\\Archivio.png") #;d.forward();d.draw()
        s.vcf_img=Image.open(directory.skin_dir+"\\Vcf.png") #;d.forward();d.draw()
        s.sis_img=Image.open(directory.skin_dir+"\\Sis_installer.png") #;d.forward();d.draw()
        s.text_img=Image.open(directory.skin_dir+"\\testo.png") #;d.forward();d.draw()
        s.pycon_img=Image.open(directory.skin_dir+"\\Python.png") #;d.forward();d.draw()

        #Maschere init
        
        s.appimg_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.file_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.cartella_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        # s.cartellaimg_mask = Image.new((32,32), 'L');d.forward()
        # s.cartellaaudio_mask = Image.new((32,32), 'L')
        # s.cartellavideo_mask = Image.new((32,32), 'L')
        # s.cartellainstall_mask = Image.new((32,32), 'L')
        s.dll_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        #s.cartellafont_img_mask = Image.new((32,32), 'L')
        s.ingranaggio_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.internet_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.mmc_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.tel_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.musica_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.mail_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.ram_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.rom_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.video_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.immagine_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.settings_img_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.archive_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.vcf_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.sis_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.text_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        s.spunto_mask = Image.new((14,14), 'L') #;d.forward();d.draw()
        s.pycon_mask = Image.new((32,32), 'L') #;d.forward();d.draw()
        #Caricamento maschera;d.forward()
        #s.csel_img_mask.load(directory.skin_dir+"\\selezione_mask.bmp")
        s.appimg_mask.load(directory.skin_dir+"\\Application_mask.bmp") #;d.forward();d.draw()
        s.file_img_mask.load(directory.skin_dir+"\\File_mask.bmp") #;d.forward();d.draw()
        s.cartella_mask.load(directory.skin_dir+"\\Cartella_mask.bmp") #;d.forward();d.draw()
        # s.cartellaimg_mask.load(directory.skin_dir+"\\Cartella_immagini_mask.bmp;d.forward()")
        # s.cartellaaudio_mask.load(directory.skin_dir+"\\Cartella_musica_mask.bmp")
        # s.cartellavideo_mask.load(directory.skin_dir+"\\Cartella_video_mask.bmp")
        # s.cartellainstall_mask.load(directory.skin_dir+"\\Cartella_install_mask.bmp")
        s.dll_img_mask.load(directory.skin_dir+"\\dll_mask.bmp") #;d.forward();d.draw()
        #s.cartellafont_img_mask.load(directory.skin_dir+"\\font_mask.bmp")
        s.ingranaggio_img_mask.load(directory.skin_dir+"\\ingranaggio_mask.bmp") #;d.forward();d.draw()
        s.internet_img_mask.load(directory.skin_dir+"\\internet_mask.bmp") #;d.forward();d.draw()
        s.mmc_img_mask.load(directory.skin_dir+"\\mmcmemory_mask.bmp") #;d.forward();d.draw()
        s.tel_img_mask.load(directory.skin_dir+"\\telmemory_mask.bmp") #;d.forward();d.draw()
        s.musica_img_mask.load(directory.skin_dir+"\\musica_mask.bmp") #;d.forward();d.draw()
        s.mail_mask.load(directory.skin_dir+"\\mail_mask.bmp") #;d.forward();d.draw()
        s.ram_img_mask.load(directory.skin_dir+"\\rammemory_mask.bmp") #;d.forward();d.draw()
        s.rom_img_mask.load(directory.skin_dir+"\\rommemory_mask.bmp") #;d.forward();d.draw()
        s.video_img_mask.load(directory.skin_dir+"\\video_mask.bmp") #;d.forward();d.draw();d.draw()
        s.immagine_img_mask.load(directory.skin_dir+"\\immagine_mask.bmp") #;d.forward();d.draw()
        s.settings_img_mask.load(directory.skin_dir+"\\settings_mask.bmp") #;d.forward();d.draw()
        s.archive_mask.load(directory.skin_dir+"\\archivio_mask.bmp") #;d.forward();d.draw()
        s.vcf_mask.load(directory.skin_dir+"\\vcf_mask.bmp") #;d.forward();d.draw()
        s.sis_mask.load(directory.skin_dir+"\\Sis_installer_mask.bmp") #;d.forward();d.draw()
        s.text_mask.load(directory.skin_dir+"\\testo_mask.bmp") #;d.forward();d.draw()
        s.spunto_mask.load(directory.skin_dir+"\\spunto_mask.bmp") #;d.forward();d.draw()
        s.pycon_mask.load(directory.skin_dir+"\\Python_mask.bmp") #;d.forward();d.draw()
        #menu

        s.bg_img=s.bg_img_normal
        s.csel_img=s.csel_img_normal#.resize((176,16))
        s.csel_img_mask = Image.new(s.csel_img.size,'L')
        s.csel_img_mask.blit(s.csel_img_mask_normal)
        
        s.mn_i=s.csel_img.resize((168,16))
        s.mn_i_mask=s.csel_img_mask.resize((168,16))
        s.mn_il=s.csel_img.resize((100,16))
        s.mn_i_maskl=s.csel_img_mask.resize((100,16))
        
       # d.close()
    def screen_change(s):
        if ui.landscape:# and old!=2:
            s.bg_img=s.bg_img_landscape
            s.csel_img=s.csel_img_landscape
            s.csel_img_mask=Image.new(s.csel_img_mask_landscape.size,'L')
            s.csel_img_mask.blit(s.csel_img_mask_landscape)
            s.mn_i=s.csel_img.resize((200,16))
            s.mn_i_mask=s.csel_img_mask.resize((200,16))
            # s.mn_il=s.csel_img.resize((132,16))
            # s.mn_i_maskl=s.csel_img_mask.resize((132,16))
        else:
            s.bg_img=s.bg_img_normal
            s.csel_img=s.csel_img_normal
            s.csel_img_mask=Image.new(s.csel_img_mask_normal.size,'L')
            s.csel_img_mask.blit(s.csel_img_mask_normal)
            s.mn_i=s.csel_img.resize((168,16))
            s.mn_i_mask=s.csel_img_mask.resize((168,16))
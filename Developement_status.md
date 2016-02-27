## NOTE ##

The developement is still going on but the sources here aren't updated since I had to fix a lot of things. Don't use the old source because a lot of code (mainly graphics, but not only) is changed.


# Changelog of latest source (NOT uploaded) #


IDEE:

```
- some general code cleaned
- added: quick (sub)menu selection by number keys
- some menu graphics improved; complete new code; new (sub)menu skinUI definitions
- new menu background effect: negative brightness
- added exit confirmation (optional), turned on by default
- language file should now support utf8 characters also in extension (little glitch with u"")
- silent settings, session and theme dat files loading error message (debug log)
- little warning message correction and traceback improved in Translator
- did_u_know_tha draft added
- hints_Italiano.txt added
- color_mixed added (todo: split these color functions in proper module)
- softkeys label font and position corrected
- began to improve drive inconing: each drive icon is assigned according to drive type (no more hardcoded)
- Now playing: now showing artist 'n title if any
- removed Mail class: now integrated in Explorer (3rd ed??)
- explorer.content_of_dir struct improved: added modification time
- added setting: show_hidden_tasks
- removed ProcETask class: now integrated in Explorer
- some modifications in user.note
- feature added: possibility to reset settings directly from WinFile
- file / dirs sorting completed: now fully working with highly optimized instructions (this feature shouldn't hurt on performance, maybe only 1-2 ms delay for long lists so nothing to worry about)
- ui.display_size rewritten
- "No such file or directory Italiano" warning removed (for default language there's no language file)
- Reintroduced landscape compatibility with S60v2 (well rewritten display_size routine)
- library loading rewritten: every failure it's now reported on debug log
- added audio player confirm: "Stop song or continue playing?" if another song file is opened from filemanager during background playing
- Text_Object class created: still to test
- New popup windows logic: to be tested
- New auto time zone detection: it's a beta. It may not work in some situations!
- New popup windows code! Now it's adaptable and capable to view text with scrollbar if it's too long. Some glitches to fix. TODO: add queue!
- Audio lenght info: precision fixed
- Info cleaned and fixed. TODO: fix os.listdir in scan_dir_info (not always is possible to listdir)
- Some other "old" key definitions (not scancodes but keycodes) fixed to scancodes
- Every library that fails on import, takes the value None -> Extended and fixed modulability
- progress_dialog class rewritten. Now with scalable support, scrollable text...as popups!
- Parts of StatusBar rewritten. Optimized and changed s.position behaviour
- Parts of ScrollBar rewritten. Optimized and changed s.position behaviour
- added exec cmd menu function to test on the fly something :)
- Some notes popup fixed to be used with menu, in class start
- Submenu completely screen adapted
- Started to create image preview and other on the fly...
- Some lines_render bugs fixed
- Introduced begin_redraw/end_redraw to solve lots of non-sense bugs in 3rd edition
- Started to complete touch implementation
```

Known Defects:

- warning about skin loading: no problem...It is normal till I write a new skin loader
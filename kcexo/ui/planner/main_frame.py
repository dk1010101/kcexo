# -*- coding: UTF-8 -*-
# cSpell:ignore hmsdms OBJCTRA OBJCTDEC xlim ylim yrange kcexo otype exoclock
# pylint:disable=unused-argument
import logging
import warnings
import importlib.resources as res
from pathlib import Path
import yaml

from pubsub import pub

import wx
import wx.lib.agw.aui as aui

from kcexo.observatory import Observatories, Observatory
from kcexo.data.exoclock_data import ExoClockData

from kcexo.ui.planner.about import show_about_box
from kcexo.ui.planner.panel_obs import ObsPanel
from kcexo.ui.planner.panel_mt import MultipleTargetsPanel
from kcexo.ui.planner.panel_st import SingleTargetPanel
from kcexo.ui.planner.panel_sd import SingleDayPanel
from kcexo.ui.widgets.license_dialog import LicenseViewerDialog


class MainFrame(wx.Frame):
    """Main frame of the star comparison application"""
    def __init__(self, *args, **kwds):
        self.log = logging.getLogger("KCEXO")
        self.observatories: Observatories = None
        self.observatory: Observatory = None
        self.exoclock_db: ExoClockData = None
        self.ax = None
        self.allow_tab_change: bool = True
             
        # things that can be mass-enabled or mass-disabled
        self.ed_controls = []
        
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1500, 850))
        self.SetMinSize((1200, 850))
        
        self.SetTitle("Exoplanet Transit Planner")
        
        ############################################
        # Menu Bar
        self.create_menu_bar()
        
        ###########################################
        # Status Bar
        self.sb = self.CreateStatusBar(1)
        # self.sb.SetStatusWidths([-1, 200])
        self.clear_status_bar()
        
        ############################################
        # Main Panel
        self.panel_main = wx.Panel(self, wx.ID_ANY)
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        ############################################
        # Tab
        #self.tab_main = wx.Notebook(self.panel_main, wx.ID_ANY, style=wx.NB_BOTTOM)
        self.tab_main = aui.AuiNotebook(self.panel_main, wx.ID_ANY, agwStyle=aui.AUI_NB_BOTTOM|aui.AUI_NB_SMART_TABS)
        sizer_main.Add(self.tab_main, 1, wx.EXPAND, 0)
        
        ###################
        # tab 0 - obs
        self.tab_main_pane_obs = ObsPanel(self.tab_main, wx.ID_ANY, 
                                          self.observatories, 
                                          style=wx.BORDER_NONE | wx.FULL_REPAINT_ON_RESIZE | wx.TAB_TRAVERSAL)
        self.tab_main.AddPage(self.tab_main_pane_obs, "Observatory", select=True, tooltip="Observatory details")

        ###################
        # tab 1 - obs
        self.tab_main_pane_mt = MultipleTargetsPanel(self.tab_main, wx.ID_ANY, 
                                                     observatory=self.tab_main_pane_obs.observatory,
                                                     exoclock_db=self.exoclock_db,
                                                     style=wx.BORDER_NONE | wx.FULL_REPAINT_ON_RESIZE | wx.TAB_TRAVERSAL)
        self.tab_main.AddPage(self.tab_main_pane_mt, "All Targets", select=False, tooltip="Transits for multiple targets\nover multiple dates")


        ###################
        # tab 2 - obs
        self.tab_main_pane_st = SingleTargetPanel(self.tab_main, wx.ID_ANY, 
                                                  observatory=self.tab_main_pane_obs.observatory,
                                                  exoclock_db=self.exoclock_db,
                                                  style=wx.BORDER_NONE | wx.FULL_REPAINT_ON_RESIZE | wx.TAB_TRAVERSAL)
        self.tab_main.AddPage(self.tab_main_pane_st, "Single Target", select=False, tooltip="Transits for a single targets\nover multiple dates")


        ###################
        # tab 3 - obs
        self.tab_main_pane_sd = SingleDayPanel(self.tab_main, wx.ID_ANY, 
                                               observatory=self.tab_main_pane_obs.observatory,
                                               exoclock_db=self.exoclock_db,
                                               style=wx.BORDER_NONE | wx.FULL_REPAINT_ON_RESIZE | wx.TAB_TRAVERSAL)
        self.tab_main.AddPage(self.tab_main_pane_sd, "Single Night", select=False, tooltip="Single evening transit planner")

        ###################
        self.panel_main.SetSizer(sizer_main)
        self.Layout()
        
        ######################################
        # EVENTS
 
        ###################
        # vanilla events
        #self.tab_main.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_main_page_changed)
        self.tab_main.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.on_tab_main_page_changing)
        self.tab_main.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_tab_main_page_changed)
        
        pub.subscribe(self.on_pubsub_status_set, "status.set")
        pub.subscribe(self.on_pubsub_status_clear, "status.clear")
        pub.subscribe(self.on_pubsub_tabs_preventchange, "tabs.preventchange")
        pub.subscribe(self.on_pubsub_tabs_allowchange, "tabs.allowchange")
        
    ##############################
    # UI CREATION
    
    def create_menu_bar(self):
        """Create the simple menu bar."""
        frame_menubar = wx.MenuBar()
        menu_file = wx.Menu()
        item = menu_file.Append(wx.ID_ANY, "Load Observatories File", "")
        self.Bind(wx.EVT_MENU, self.on_menu_load_obs, item)
        item = menu_file.Append(wx.ID_ANY, "Refresh databases", "")
        self.Bind(wx.EVT_MENU, self.on_menu_refresh, item)
        menu_file.AppendSeparator()
        item = menu_file.Append(wx.ID_ANY, "Exit", "")
        self.Bind(wx.EVT_MENU, self.on_menu_exit, item)
        frame_menubar.Append(menu_file, "File")
        #
        menu_help = wx.Menu()
        item = menu_help.Append(wx.ID_ANY, "License", "")
        self.Bind(wx.EVT_MENU, self.on_menu_help_license, item)
        menu_help.AppendSeparator()
        item = menu_help.Append(wx.ID_ANY, "About", "")
        self.Bind(wx.EVT_MENU, self.on_menu_help_about, item)
        frame_menubar.Append(menu_help, "Help")
        #
        self.SetMenuBar(frame_menubar)
    
    ##############################
    # EVENTS - PUBSUB
    
    def on_pubsub_tabs_preventchange(self):
        """Disallow tab change if so requested"""
        self.log.debug("MF - on_pubsub_tabs_preventchange")
        self.allow_tab_change = False
    
    def on_pubsub_tabs_allowchange(self):
        """Allow tab change if so requested"""
        self.log.debug("MF - on_pubsub_tabs_allowchange")
        self.allow_tab_change = True
    
    def on_pubsub_status_set(self, data):
        """Update the status bar from pubsub event"""
        self.update_status_bar(data)
    
    def on_pubsub_status_clear(self):
        """Clear the status bar from pubsub event"""
        self.clear_status_bar()
    
    ##############################
    # EVENTS - UI
    
    def on_menu_help_license(self, event: wx.Event):
        """Show the license file from the menu"""
        text = res.read_text("kcexo.assets.comp_stars", "license.txt")
        dialog = LicenseViewerDialog(self, "License", text)
        dialog.ShowModal()
        
    def on_menu_help_about(self, event: wx.Event):
        """Show the about box from the menu"""
        show_about_box(self)

    def on_menu_exit(self, event: wx.Event):
        """Exit the app from the menu"""
        wx.CallAfter(self.Destroy)
        self.Close()
    
    def on_menu_refresh(self, event: wx.Event):
        """Reload database."""
        with wx.BusyCursor():
            self.update_status_bar("Loading exoclock planet and star data...")
            self.exoclock_db: ExoClockData = ExoClockData(self.observatories.root_dir)
            self.tab_main_pane_mt.set_db(self.exoclock_db)
            self.tab_main_pane_st.set_db(self.exoclock_db)
            self.tab_main_pane_sd.set_db(self.exoclock_db)
        self.clear_status_bar()
        
    def on_menu_load_obs(self, event: wx.Event):
        with wx.FileDialog(self, 
                           "Open observatories file", 
                           wildcard="YAML file (*.yaml)|*.yaml",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = file_dialog.GetPath()
            self.update_status_bar("Loading observatories...")
            try:
                with wx.BusyCursor():
                    self.tab_main.SetSelection(0)
                    with open(pathname, "r", encoding="utf-8") as f:
                        obss_y = yaml.safe_load(f)
                        root = Path(pathname).parent
                        self.observatories = Observatories(obss_y, root)
                        
                    self.update_status_bar("Loading exoclock planet and star data...")
                    self.exoclock_db: ExoClockData = ExoClockData(self.observatories.root_dir)
                    self.tab_main_pane_mt.set_db(self.exoclock_db)
                    self.tab_main_pane_st.set_db(self.exoclock_db)
                    self.tab_main_pane_sd.set_db(self.exoclock_db)
                    self.tab_main_pane_obs.set_observatories(self.observatories)
                    self.clear_status_bar()
                    
            except IOError as err:
                print(err)
                wx.LogError(f"Cannot open file '{pathname}'.")
            self.clear_status_bar()
        event.Skip()
    
    def on_tab_main_page_changed(self, event: wx.BookCtrlEvent):
        """Once tab changes check if we moved away from observatories and apply any changes"""
        previous = event.GetOldSelection()
        new = event.GetSelection()
        if previous == new:
            return
        if previous == 0:
            print("We switched from Observatory!")

    def on_tab_main_page_changing(self, event: wx.BookCtrlEvent):
        if self.allow_tab_change:
            event.Skip()

    ##############################
    # HELPERS
        
    def update_status_bar(self, message: str) -> None:
        """Update the status bar..."""
        self.sb.SetStatusText(message)

    def clear_status_bar(self) -> None:
        """clear the status bar"""
        self.update_status_bar("Ready")

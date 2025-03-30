# -*- coding: UTF-8 -*-
# cSpell:ignore hmsdms OBJCTRA OBJCTDEC xlim ylim yrange kcexo
# pylint:disable=unused-argument
import os
import copy
import importlib.resources as res

import numpy as np
import matplotlib.pyplot as plt

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.table import Table
from astropy.io import ascii as as_ascii
from astropy.visualization import ImageNormalize, SqrtStretch, LogStretch, AsinhStretch, ZScaleInterval, SquaredStretch, MinMaxInterval, SinhStretch, LinearStretch

import wx
import wx.grid

from kcexo.fov import FOV
from kcexo.data.fov_stars import FOVStars, MinMaxValue
from kcexo.data.fits import get_image_and_header

from kcexo.ui.comp_stars.about import show_about_box
from kcexo.ui.comp_stars.top_pane import TopPanel
from kcexo.ui.comp_stars.grid_pane import GridPanel
from kcexo.ui.widgets.license_dialog import LicenseViewerDialog


class MainFrame(wx.Frame):
    """Main frame of the star comparison application"""
    def __init__(self, *args, **kwds):
        bg_col = wx.WHITE
        bg_col2 = wx.LIGHT_GREY
        self.fname: str
        self.wcs: WCS
        self.fov: FOV
        self.fov_stars: FOVStars
        self.filtered_data: Table
        self.target_name: str = ""
        
        # image stuff
        self.image_data = None
        self.ax = None
        self._last_pick_mouseevent = ""        
        self.stretch_prev_vmin=65535  # some bigish number
        self.stretch_prev_vmax=0
        self.stretch_max = 0
        
        # canvas zoom and move
        self.canvas_cur_xlim = None
        self.canvas_cur_ylim = None
        self.canvas_press = None
        self.canvas_xpress = None
        self.canvas_ypress = None
        
        # things that can be mass-enabled or mass-disabled
        self.ed_controls = []
        
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1200, 850))
        self.SetMinSize((1200, 850))
        
        self.SetTitle("Comp Star Finder")
        
        ############################################
        # Menu Bar
        self.create_menu_bar()
        
        ############################################
        # Main Panel
        self.main_panel = wx.Panel(self, wx.ID_ANY)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        #################
        # splitter window
        self.wnd_split = wx.SplitterWindow(self.main_panel, wx.ID_ANY, style=wx.SP_LIVE_UPDATE)
        self.wnd_split.SetMinimumPaneSize(600)
        self.wnd_split.SetSashGravity(0.7)
        self.wnd_split.SetBackgroundColour(bg_col2)
        sizer_1.Add(self.wnd_split, 0, wx.EXPAND, 0)
        
        #################
        # create splitter
        self.wnd_split_pane_top = wx.Panel(self.wnd_split, wx.ID_ANY)
        self.wnd_split_pane_top.SetBackgroundColour(bg_col)
        
        self.wnd_split_pane_bottom = wx.Panel(self.wnd_split, wx.ID_ANY)
        self.wnd_split_pane_bottom.SetBackgroundColour(bg_col)
        
        self.wnd_split.SplitHorizontally(self.wnd_split_pane_top, self.wnd_split_pane_bottom)
        
        #################
        # top pane
        self.wnd_split_pane_top.SetBackgroundColour(bg_col2)
        tsz = wx.FlexGridSizer(1, 1, 0, 0)
        self.top_panel = TopPanel(self.wnd_split_pane_top, wx.ID_ANY, background_colour=bg_col)
        tsz.Add(self.top_panel, 0, wx.EXPAND, 1)
        tsz.AddGrowableRow(0)
        tsz.AddGrowableCol(0)
        self.wnd_split_pane_top.SetSizer(tsz)
        self.ed_controls.append(self.top_panel)
        
        #################
        # bottom pane
        self.wnd_split_pane_bottom.SetBackgroundColour(bg_col)
        bsz = wx.FlexGridSizer(1, 1, 0, 0)
        self.grid = GridPanel(self.wnd_split_pane_bottom, wx.ID_ADD, background_colour=bg_col)
        bsz.Add(self.grid, 1, wx.EXPAND, 0)
        bsz.AddGrowableRow(0)
        bsz.AddGrowableCol(0)
        self.wnd_split_pane_bottom.SetSizer(bsz)
        self.ed_controls.append(self.grid)
        
        #################
        self.disable_all_controls()
        self.main_panel.SetSizerAndFit(sizer_1)
        
        ###########################################
        
        self.Layout()
        self.Refresh()

        ###########################################
        # events
        self.wnd_split.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.on_splitter_change)
        self.Bind(wx.EVT_SIZE, self.on_size_change)
        
        ## top
        self.top_panel.slider_image_stretch.Bind(wx.EVT_LEFT_UP, self.on_slider_image_stretch)
        self.top_panel.bt_image_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch)
        self.top_panel.bt_image_stretch_reset.Bind(wx.EVT_BUTTON, self.on_bt_image_reset)
        self.top_panel.bt_image_stretch_apply.Bind(wx.EVT_BUTTON, self.on_bt_image_stretch)
        self.top_panel.cb_flip_x.Bind(wx.EVT_CHECKBOX, self.on_cb_flip)
        self.top_panel.cb_flip_y.Bind(wx.EVT_CHECKBOX, self.on_cb_flip)
        self.top_panel.flt_dist.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.top_panel.flt_bv.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.top_panel.flt_b.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.top_panel.flt_v.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.top_panel.flt_r.Bind(wx.EVT_CHECKBOX, self.on_cb_filter_change)
        self.top_panel.canvas.mpl_connect('pick_event', self.on_canvas_pick)
        self.top_panel.canvas.mpl_connect('scroll_event', self.on_canvas_scroll)
        self.top_panel.canvas.mpl_connect('button_press_event', self.on_canvas_press)
        self.top_panel.canvas.mpl_connect('button_release_event', self.on_canvas_release)
        self.top_panel.canvas.mpl_connect('motion_notify_event', self.on_canvas_motion)
                
    def create_menu_bar(self):
        """Create the simple menu bar."""
        frame_menubar = wx.MenuBar()
        menu_file = wx.Menu()
        item = menu_file.Append(wx.ID_ANY, "Open", "")
        self.Bind(wx.EVT_MENU, self.on_menu_open, item)
        self.menu_export = menu_file.Append(wx.ID_ANY, "Export...", "")
        self.Bind(wx.EVT_MENU, self.on_menu_export, self.menu_export)
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
        
        #####
        # add to enable/disable list
        self.ed_controls.append(self.menu_export)

    ##############################################################################
    # event handlers
    
    def on_size_change(self, event):
        """Handle app size change."""
        self.Refresh()
        event.Skip()
        
    def on_splitter_change(self, event):
        """When the splitter has been moved, redraw all."""
        self.Refresh()

    def on_cb_filter_change(self, event):
        """When a filter UI component changes, filter the data."""
        self.filter_data()

    def on_cb_nan_bv_change(self, event):
        """When a filter UI component changes, filter the data."""
        if self.cb_bv.GetValue():
            self.on_cb_filter_change(None)
    
    def on_cb_nan_b_change(self, event):
        """When a filter UI component changes, filter the data."""
        if self.cb_b.GetValue():
            self.on_cb_filter_change(None)
    
    def on_cb_nan_v_change(self, event):
        """When a filter UI component changes, filter the data."""
        if self.cb_v.GetValue():
            self.on_cb_filter_change(None)
    
    def on_cb_nan_r_change(self, event):
        """When a filter UI component changes, filter the data."""
        if self.cb_r.GetValue():
            self.on_cb_filter_change(None)

    def on_cb_flip(self, event):
        """Flip the image in X or Y direction."""
        self.plot_data()

    def on_bt_image_stretch(self, event):
        """Apply the stretch parameters."""
        self.plot_data()
        
    def on_bt_image_reset(self, event):
        """Reset the image back to starting values."""
        self.set_initial_stretch()
        self.plot_data()
        
    def on_slider_image_stretch(self, event):
        """Handle the change in the image stretch slider."""
        vmin, vmax = self.top_panel.slider_image_stretch.GetValues()
        self.top_panel.lbl_image_stretch_min.SetLabel(str(int(vmin)))
        self.top_panel.lbl_image_stretch_max.SetLabel(str(int(vmax)))
        self.reset_stretch_slider_minmax()
        if event:
            event.Skip() 
    
    def on_menu_open(self, event):
        """Load the FITS file and show all the results."""
        with wx.FileDialog(self, 
                           "Open reduced FITS image file", 
                           wildcard="FITS file (*.fits;*.fts)|*.fits;*.fts|Compressed FITS (*.fz;*.fits.fz)|*.fz;*.fits.fz)",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = file_dialog.GetPath()
            try:
                with wx.BusyCursor():
                    hdr, self.image_data = get_image_and_header(pathname)
                    if hdr is None or self.image_data is None:
                        wx.MessageBox("The FITS file did not have an image section that this program recognises.", "Doh!", wx.ICON_ERROR | wx.OK)
                        return
                    
                    self.target_name = hdr.get('OBJECT', '')
                    target_c = ''
                    if self.target_name:
                        if "_" in self.target_name:
                            # some observatories add user name after the object name. this is evil.
                            a, _ = self.target_name.split("_", 1)
                            self.target_name = a
                        target_c = SkyCoord.from_name(self.target_name)
                    if target_c is None or not target_c:
                        target_c = ''
                        if 'OBJCTRA' in hdr and 'OBJCTDEC' in hdr:
                            target_c = SkyCoord(f"{hdr['OBJCTRA']} {hdr['OBJCTDEC']}", unit=(u.hourangle, u.deg))
                        elif 'RA' in hdr and 'DEC' in hdr:
                            # since HOPS compressed file is evil
                            target_c = SkyCoord(f"{hdr['RA']} {hdr['DEC']}", unit=(u.deg, u.deg))
                        else:
                            wx.MessageBox("Cannot process FITS files without OBJECT or OBJCTRA/DEC tags.", "Really?", wx.ICON_ERROR | wx.OK)
                    
                    self.fov = FOV.from_image(pathname)
                    self.fov_stars = FOVStars(self.fov, self.target_name, target_c)
                    self.filtered_data = copy.deepcopy(self.fov_stars.table)
                    self.fname = pathname
                    
                    v = {
                        'dist': self.fov_stars.table[0]['dist'],
                        'B-V': self.fov_stars.table[0]['B-V'],
                        'B': self.fov_stars.table[0]['B'],
                        'V': self.fov_stars.table[0]['V'],
                        'R': self.fov_stars.table[0]['R']
                    }
                    self.top_panel.set_filter_target_values(v)
                                        
                    self.grid.update_grid(self.filtered_data)
                    self.set_initial_stretch()
                    self.plot_data()
                    
                    min_d = np.min(self.fov_stars.table['dist'])
                    max_d = np.max(self.fov_stars.table['dist'])
                    min_bv = np.min(self.fov_stars.table['B-V'])
                    max_bv = np.max(self.fov_stars.table['B-V'])
                    min_b = np.min(self.fov_stars.table['B'])
                    max_b = np.max(self.fov_stars.table['B'])
                    min_v = np.min(self.fov_stars.table['V'])
                    max_v = np.max(self.fov_stars.table['V'])
                    min_r = np.min(self.fov_stars.table['R'])
                    max_r = np.max(self.fov_stars.table['R'])

                    v = {
                        'dist': (min_d, max_d),
                        'B-V': (min_bv, max_bv),
                        'B': (min_b, max_b),
                        'V': (min_v, max_v),
                        'R': (min_r, max_r)
                    }
                    self.top_panel.set_filter_minmax(v)
                    
                    self.enable_all_controls()
                    self.Refresh()
            
            except IOError:
                wx.LogError(f"Cannot open file '{pathname}'.")

    def on_menu_export(self, event):
        """Export the data to file"""
        dlg = wx.FileDialog(self, "Export to CSV:", ".", "", "CSV (*.csv)|*.csv", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            fname = os.path.join(dirname, filename)
            as_ascii.write(self.filtered_data, fname, format='csv', fast_writer=False, overwrite=True)
        dlg.Destroy()
        wx.MessageDialog("Export completed", "Export ok")
    
    def on_menu_help_license(self, event):
        """Show the license file from the menu"""
        text = res.read_text("kcexo.assets.comp_stars", "license.txt")
        dialog = LicenseViewerDialog(self, "License", text)
        dialog.ShowModal()
        
    def on_menu_help_about(self,event):
        """Show the about box from the menu"""
        show_about_box(self)

    def on_menu_exit(self, event):
        """Exit the app from the menu"""
        wx.CallAfter(self.Destroy)
        self.Close()

    def on_canvas_pick(self, event):
        """Show what target was selected on the canvas"""
        artist = event.artist
        label = artist.get_label()
        if self._last_pick_mouseevent == label:
            return
        self._last_pick_mouseevent = label
        pos = int(label)
        self.grid.select_row(pos)

    def on_canvas_scroll(self, event):
        """Handle image zoom using mouse scroll wheel"""
        base_scale = .5
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        # cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        # cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print("foo")
        # set new limits
        self.ax.set_xlim([xdata - (xdata-cur_xlim[0]) / scale_factor, xdata + (cur_xlim[1]-xdata) / scale_factor])
        self.ax.set_ylim([ydata - (ydata-cur_ylim[0]) / scale_factor, ydata + (cur_ylim[1]-ydata) / scale_factor])
        self.top_panel.canvas.draw() # force re-draw

    def on_canvas_press(self, event):
        """Handle image click-and-drag initial mouse click event"""
        if event.inaxes != self.ax: 
            return
        self.canvas_cur_xlim = self.ax.get_xlim()
        self.canvas_cur_ylim = self.ax.get_ylim()
        self.canvas_press =event.xdata, event.ydata
        self.canvas_xpress, self.canvas_ypress = self.canvas_press

    def on_canvas_release(self, event):
        """Handle image click-and-drag mouse release event"""
        self.canvas_press = None
        self.ax.figure.canvas.draw()

    def on_canvas_motion(self, event):
        """Handle image click-and-drag event"""
        if self.canvas_press is None: 
            return
        if event.inaxes != self.ax: 
            return
        dx = event.xdata - self.canvas_xpress
        dy = event.ydata - self.canvas_ypress
        self.canvas_cur_xlim -= dx
        self.canvas_cur_ylim -= dy
        self.ax.set_xlim(self.canvas_cur_xlim)
        self.ax.set_ylim(self.canvas_cur_ylim)

        self.top_panel.canvas.draw()
        
    ##############################################################################
    # state-changers
    
    def enable_all_controls(self) -> None:
        """Make all controlled controls enabled"""
        for e in self.ed_controls:
            e.Enable(True)
        
    def disable_all_controls(self) -> None:
        """Make all controlled controls disabled"""
        for e in self.ed_controls:
            e.Enable(False)
    
    # ##############################################################################
    # helpers
    
    def set_initial_stretch(self) -> None:
        """Work-out the initial image stretch values and set the ui sliders appropriately."""
        interval = MinMaxInterval()
        _, vmax = interval.get_limits(self.image_data)
        self.stretch_max = vmax
        
        interval = ZScaleInterval()
        vmin, vmax = interval.get_limits(self.image_data)

        self.top_panel.slider_image_stretch.SetValues(vmin, vmax)
        self.reset_stretch_slider_minmax()
        self.on_slider_image_stretch(None)

    def reset_stretch_slider_minmax(self) -> None:
        """Iffy non-liner stretching slider range. This is needed as stretching is a non-linear process."""
        vmin, vmax = self.top_panel.slider_image_stretch.GetValues()
        d = vmax - vmin
        if vmin != self.stretch_prev_vmin:
            n_min = vmin - 2*d
        else:
            n_min = vmin
        if vmax != self.stretch_prev_vmax:
            n_max = vmax + 2*d
        else:
            n_max = vmax
        if n_min < 0:
            n_min = 0
        if n_max > self.stretch_max:
            n_max = self.stretch_max
        self.stretch_prev_vmin = n_min
        self.stretch_prev_vmax = n_max
        self.top_panel.slider_image_stretch.ResetLimits(n_min, n_max)
        self.top_panel.slider_image_stretch.SetValues(vmin, vmax)
        
    def plot_data(self) -> None:
        """Plot the starfiled along with the stars."""
        self.top_panel.figure.clear()
        self.ax = self.top_panel.figure.add_subplot(1, 1, 1, projection=self.fov.wcs)
        self.ax.set(xlabel="RA", ylabel="Dec")

        vmin, vmax = self.top_panel.slider_image_stretch.GetValues()

        stretch_method = self.top_panel.cb_image_stretch.GetCurrentSelection()
        if stretch_method == 0: # 'linear'
            stretch = LinearStretch()
        elif stretch_method == 1: # 'log'
            stretch = LogStretch()
        elif stretch_method == 2: # 'sinh'
            stretch = SinhStretch()
        elif stretch_method == 3: # 'asinh'
            stretch = AsinhStretch()
        elif stretch_method == 4: # 'square'
            stretch = SquaredStretch()
        elif stretch_method == 5: # 'sqrt'
            stretch = SqrtStretch()
        else:
            raise ValueError(f"Unknown stretch: {stretch_method}")
        norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=stretch)
        self.ax.imshow(self.image_data, origin='lower', norm=norm)
        if self.top_panel.cb_flip_x.GetValue():
            self.ax.invert_xaxis()
        if self.top_panel.cb_flip_y.GetValue():
            self.ax.invert_yaxis()
        
        target = self.filtered_data[0]['Object']
            
        for i, row in enumerate(self.filtered_data.iterrows()):
            c = SkyCoord(ra = row[2] * u.deg, dec = row[3] * u.deg)
            xy = self.fov.wcs.world_to_pixel(c)
            # print(i, row[0], c.to_string("hmsdms"), xy)
            if row[4] != "*":
                cl = 'yellow'
            else:
                cl = 'white'
            c = plt.Circle(xy, 22, color=cl, fill=False, lw=1, label=str(i), picker=True)
            self.ax.add_patch(c)
            if i == 0:
                self.ax.text(xy[0]+25, xy[1]+25, f"{row[0]}", color=cl, fontsize=8, label=str(i), picker=True)
            else:
                if target in row[0]:
                    continue
                self.ax.text(xy[0]+25, xy[1]+25, f"{i+1}", color=cl, fontsize=6, label=str(i), picker=True)
        # title
        obj_name = self.fov_stars.table[0]['Object']
        if obj_name != self.target_name:
            title = f"{self.target_name} ({obj_name})"
        else:
            title = self.target_name
        self.ax.set_title(title)
        self.ax.grid(True) 
        self.top_panel.figure.tight_layout()
        self.top_panel.canvas.draw()
        self.Refresh()

    def filter_data(self) -> None:
        """Based on filter ui components, filter the data and show it."""
        filters = []
        if self.top_panel.flt_dist.GetValue():
            v = self.top_panel.flt_dist.GetValues()
            filters.append(MinMaxValue('dist', v[0], v[1], v[2]))
        if self.top_panel.flt_bv.GetValue():
            v = self.top_panel.flt_bv.GetValues()
            filters.append(MinMaxValue('B-V', v[0], v[1], v[2]))
        if self.top_panel.flt_b.GetValue():
            v = self.top_panel.flt_b.GetValues()
            filters.append(MinMaxValue('B', v[0], v[1], v[2]))
        if self.top_panel.flt_v.GetValue():
            v = self.top_panel.flt_v.GetValues()
            filters.append(MinMaxValue('V', v[0], v[1], v[2]))
        if self.top_panel.flt_r.GetValue():
            v = self.top_panel.flt_r.GetValues()
            filters.append(MinMaxValue('R', v[0], v[1], v[2]))
        
        self.filtered_data = self.fov_stars.filter_stars(filters)
    
        self.grid.update_grid(self.filtered_data)
        self.plot_data()

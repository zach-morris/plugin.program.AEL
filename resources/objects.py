# -*- coding: utf-8 -*-
#
# Advanced Emulator Launcher miscellaneous set of objects
#

# 1. Always use new style classes in Python 2 to ease the transition to Python 3.
#    All classes in Python 2 must have object as base class.
#    See https://stackoverflow.com/questions/4015417/python-class-inherits-object

# Copyright (c) 2016-2018 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division
import abc
import collections
import shlex
import subprocess
import webbrowser

# --- AEL packages ---
from utils import *
from disk_IO import *
from net_IO import *
from platforms import *

# #################################################################################################
# #################################################################################################
# Assets/Artwork
# #################################################################################################
# #################################################################################################

ASSET_SETTING_KEYS = {
    ASSET_ICON_ID : '',
    ASSET_FANART_ID : 'scraper_fanart',
    ASSET_BANNER_ID : 'scraper_banner',
    ASSET_POSTER_ID : '',
    ASSET_CLEARLOGO_ID : 'scraper_clearlogo',
    ASSET_CONTROLLER_ID : '',
    ASSET_TRAILER_ID : '',
    ASSET_TITLE_ID : 'scraper_title',
    ASSET_SNAP_ID : 'scraper_snap',
    ASSET_BOXFRONT_ID : 'scraper_boxfront',
    ASSET_BOXBACK_ID : 'scraper_boxback',
    ASSET_CARTRIDGE_ID : 'scraper_cart',
    ASSET_FLYER_ID : '',
    ASSET_MAP_ID : '',
    ASSET_MANUAL_ID : ''
}

MAME_ASSET_SETTING_KEYS = {
    ASSET_ICON_ID : '',
    ASSET_FANART_ID : 'scraper_fanart_MAME',
    ASSET_BANNER_ID : 'scraper_marquee_MAME',
    ASSET_POSTER_ID : '',
    ASSET_CLEARLOGO_ID : 'scraper_clearlogo_MAME',
    ASSET_CONTROLLER_ID : '',
    ASSET_TRAILER_ID : '',
    ASSET_TITLE_ID : 'scraper_title_MAME',
    ASSET_SNAP_ID : 'scraper_snap_MAME',
    ASSET_BOXFRONT_ID : 'scraper_cabinet_MAME',
    ASSET_BOXBACK_ID : 'scraper_cpanel_MAME',
    ASSET_CARTRIDGE_ID : 'scraper_pcb_MAME',
    ASSET_FLYER_ID : 'scraper_flyer_MAME',
    ASSET_MAP_ID : '',
    ASSET_MANUAL_ID : ''
}

#
# Get extensions to search for files
# Input : ['png', 'jpg']
# Output: ['png', 'jpg', 'PNG', 'JPG']
#
def asset_get_filesearch_extension_list(exts):
    ext_list = list(exts)
    for ext in exts:
        ext_list.append(ext.upper())

    return ext_list

#
# Gets extensions to be used in Kodi file dialog.
# Input : ['png', 'jpg']
# Output: '.png|.jpg'
#
def asset_get_dialog_extension_list(exts):
    ext_string = ''
    for ext in exts:
        ext_string += '.' + ext + '|'
    # >> Remove trailing '|' character
    ext_string = ext_string[:-1]

    return ext_string

#
# Gets extensions to be used in regular expressions.
# Input : ['png', 'jpg']
# Output: '(png|jpg)'
#
def asset_get_regexp_extension_list(exts):
    ext_string = ''
    for ext in exts:
        ext_string += ext + '|'
    # >> Remove trailing '|' character
    ext_string = ext_string[:-1]

    return '(' + ext_string + ')'

# -------------------------------------------------------------------------------------------------
# Asset functions
# -------------------------------------------------------------------------------------------------

#
# Get artwork user configured to be used as icon/fanart/... for Categories/Launchers
#
def asset_get_default_asset_Category(object_dic, object_key, default_asset = ''):
    conf_asset_key = object_dic[object_key]
    asset_path     = object_dic[conf_asset_key] if conf_asset_key in object_dic and object_dic[conf_asset_key] else default_asset

    return asset_path

#
# Same for ROMs
#
def asset_get_default_asset_Launcher_ROM(rom, launcher, object_key, default_asset = ''):

    if object_key not in launcher:
        return default_asset

    conf_asset_key = launcher[object_key]
    asset_path     = rom[conf_asset_key] if rom[conf_asset_key] else default_asset

    return asset_path

#
# Gets a human readable name string for the asset field name.
#
def assets_get_asset_name_str(default_asset):
    asset_name_str = ''

    # >> ROMs
    if   default_asset == 's_title':     asset_name_str = 'Title'
    elif default_asset == 's_snap':      asset_name_str = 'Snap'
    elif default_asset == 's_boxfront':  asset_name_str = 'Boxfront'
    elif default_asset == 's_boxback':   asset_name_str = 'Boxback'
    elif default_asset == 's_cartridge': asset_name_str = 'Cartridge'
    elif default_asset == 's_fanart':    asset_name_str = 'Fanart'
    elif default_asset == 's_banner':    asset_name_str = 'Banner'
    elif default_asset == 's_clearlogo': asset_name_str = 'Clearlogo'
    elif default_asset == 's_flyer':     asset_name_str = 'Flyer'
    elif default_asset == 's_map':       asset_name_str = 'Map'
    elif default_asset == 's_manual':    asset_name_str = 'Manual'
    elif default_asset == 's_trailer':   asset_name_str = 'Trailer'
    # >> Categories/Launchers
    elif default_asset == 's_icon':       asset_name_str = 'Icon'
    elif default_asset == 's_poster':     asset_name_str = 'Poster'
    elif default_asset == 's_controller': asset_name_str = 'Controller'
    else:
        kodi_notify_warn('Wrong asset key {0}'.format(default_asset))
        log_error('assets_get_asset_name_str() Wrong default_thumb {0}'.format(default_asset))
    
    return asset_name_str

#
# This must match the order of the list Category_asset_ListItem_list in _command_edit_category()
#
def assets_choose_Category_mapped_artwork(dict_object, key, index):
    if   index == 0: dict_object[key] = 's_icon'
    elif index == 1: dict_object[key] = 's_fanart'
    elif index == 2: dict_object[key] = 's_banner'
    elif index == 3: dict_object[key] = 's_poster'
    elif index == 4: dict_object[key] = 's_clearlogo'

#
# This must match the order of the list Category_asset_ListItem_list in _command_edit_category()
#
def assets_get_Category_mapped_asset_idx(dict_object, key):
    if   dict_object[key] == 's_icon':       index = 0
    elif dict_object[key] == 's_fanart':     index = 1
    elif dict_object[key] == 's_banner':     index = 2
    elif dict_object[key] == 's_poster':     index = 3
    elif dict_object[key] == 's_clearlogo':  index = 4
    else:                                    index = 0

    return index

#
# This must match the order of the list Launcher_asset_ListItem_list in _command_edit_launcher()
#
def assets_choose_Launcher_mapped_artwork(dict_object, key, index):
    if   index == 0: dict_object[key] = 's_icon'
    elif index == 1: dict_object[key] = 's_fanart'
    elif index == 2: dict_object[key] = 's_banner'
    elif index == 3: dict_object[key] = 's_poster'
    elif index == 4: dict_object[key] = 's_clearlogo'
    elif index == 5: dict_object[key] = 's_controller'

#
# This must match the order of the list Launcher_asset_ListItem_list in _command_edit_launcher()
#
def assets_get_Launcher_mapped_asset_idx(dict_object, key):
    if   dict_object[key] == 's_icon':       index = 0
    elif dict_object[key] == 's_fanart':     index = 1
    elif dict_object[key] == 's_banner':     index = 2
    elif dict_object[key] == 's_poster':     index = 3
    elif dict_object[key] == 's_clearlogo':  index = 4
    elif dict_object[key] == 's_controller': index = 5
    else:                                    index = 0

    return index

#
# This must match the order of the list ROM_asset_str_list in _command_edit_launcher()
#
def assets_choose_ROM_mapped_artwork(dict_object, key, index):
    if   index == 0: dict_object[key] = 's_title'
    elif index == 1: dict_object[key] = 's_snap'
    elif index == 2: dict_object[key] = 's_boxfront'
    elif index == 3: dict_object[key] = 's_boxback'
    elif index == 4: dict_object[key] = 's_cartridge'
    elif index == 5: dict_object[key] = 's_fanart'
    elif index == 6: dict_object[key] = 's_banner'
    elif index == 7: dict_object[key] = 's_clearlogo'
    elif index == 8: dict_object[key] = 's_flyer'
    elif index == 9: dict_object[key] = 's_map'

#
# This must match the order of the list ROM_asset_str_list in _command_edit_launcher()
#
def assets_get_ROM_mapped_asset_idx(dict_object, key):
    if   dict_object[key] == 's_title':     index = 0
    elif dict_object[key] == 's_snap':      index = 1
    elif dict_object[key] == 's_boxfront':  index = 2
    elif dict_object[key] == 's_boxback':   index = 3
    elif dict_object[key] == 's_cartridge': index = 4
    elif dict_object[key] == 's_fanart':    index = 5
    elif dict_object[key] == 's_banner':    index = 6
    elif dict_object[key] == 's_clearlogo': index = 7
    elif dict_object[key] == 's_flyer':     index = 8
    elif dict_object[key] == 's_map':       index = 9
    else:                                   index = 0

    return index

# -------------------------------------------------------------------------------------------------
# Gets all required information about an asset: path, name, etc.
# Returns an object with all the information
# -------------------------------------------------------------------------------------------------
class AssetInfo:
    id              = 0
    key             = ''
    default_key     = ''
    rom_default_key = ''
    name            = ''
    description     = name
    plural          = ''
    fname_infix     = '' # Used only when searching assets when importing XML
    kind_str        = ''
    exts            = []
    exts_dialog     = []
    path_key        = ''

    def get_description(self):
        if self.description == '': return self.name

        return self.description

    def __eq__(self, other):
        return isinstance(other, AssetInfo) and self.id == other.id

    def __hash__(self):
        return self.id.__hash__()

# --- Static list of asset information objects ----------------------------------------------------
# >> These are used very frequently so I think it is better to have a cached statis list.
a_icon = AssetInfo()
a_icon.id               = ASSET_ICON_ID
a_icon.key              = 's_icon'
a_icon.default_key      = 'default_icon'
a_icon.rom_default_key  = 'roms_default_icon'
a_icon.name             = 'Icon'
a_icon.name_plural      = 'Icons'
a_icon.fname_infix      = 'icon'
a_icon.kind_str         = 'image'
a_icon.exts             = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_icon.exts_dialog      = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_icon.path_key         = 'path_icon'

a_fanart = AssetInfo()
a_fanart.id              = ASSET_FANART_ID
a_fanart.key             = 's_fanart'
a_fanart.default_key     = 'default_fanart'
a_fanart.rom_default_key = 'roms_default_fanart'
a_fanart.name            = 'Fanart'
a_fanart.plural          = 'Fanarts'
a_fanart.fname_infix     = 'fanart'
a_fanart.kind_str        = 'image'
a_fanart.exts            = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_fanart.exts_dialog     = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_fanart.path_key        = 'path_fanart'

a_banner = AssetInfo()
a_banner.id                = ASSET_BANNER_ID
a_banner.key               = 's_banner'
a_banner.default_key       = 'default_banner'
a_banner.rom_default_key   = 'roms_default_banner'
a_banner.name              = 'Banner'
a_banner.description       = 'Banner / Marquee'
a_banner.plural            = 'Banners'
a_banner.fname_infix       = 'banner'
a_banner.kind_str          = 'image'
a_banner.exts              = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_banner.exts_dialog       = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_banner.path_key          = 'path_banner'

a_poster = AssetInfo()        
a_poster.id                = ASSET_POSTER_ID
a_poster.key               = 's_poster'
a_poster.default_key       = 'default_poster'
a_poster.rom_default_key   = 'roms_default_poster'
a_poster.name              = 'Poster'
a_poster.plural            = 'Posters'
a_poster.fname_infix       = 'poster'
a_poster.kind_str          = 'image'
a_poster.exts              = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_poster.exts_dialog       = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_poster.path_key          = 'path_poster'

a_clearlogo = AssetInfo()
a_clearlogo.id              = ASSET_CLEARLOGO_ID
a_clearlogo.key             = 's_clearlogo'
a_clearlogo.default_key     = 'default_clearlogo'
a_clearlogo.rom_default_key = 'roms_default_clearlogo'
a_clearlogo.name            = 'Clearlogo'
a_clearlogo.plural          = 'Clearlogos'
a_clearlogo.fname_infix     = 'clearlogo'
a_clearlogo.kind_str        = 'image'
a_clearlogo.exts            = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_clearlogo.exts_dialog     = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_clearlogo.path_key        = 'path_clearlogo'

a_controller = AssetInfo()
a_controller.id             = ASSET_CONTROLLER_ID
a_controller.key            = 's_controller'
a_controller.name           = 'Controller'
a_controller.plural         = 'Controllers'
a_controller.fname_infix    = 'controller'
a_controller.kind_str       = 'image'
a_controller.exts           = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_controller.exts_dialog    = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_controller.path_key       = 'path_controller'

a_trailer = AssetInfo()
a_trailer.id                = ASSET_TRAILER_ID
a_trailer.key               = 's_trailer'
a_trailer.name              = 'Trailer'
a_trailer.plural            = 'Trailers'
a_trailer.fname_infix       = 'trailer'
a_trailer.kind_str          = 'video'
a_trailer.exts              = asset_get_filesearch_extension_list(TRAILER_EXTENSION_LIST)
a_trailer.exts_dialog       = asset_get_dialog_extension_list(TRAILER_EXTENSION_LIST)
a_trailer.path_key          = 'path_trailer'

a_title = AssetInfo()
a_title.id                  = ASSET_TITLE_ID
a_title.key                 = 's_title'
a_title.name                = 'Title'
a_title.plural              = 'Titles'
a_title.fname_infix         = 'title'
a_title.kind_str            = 'image'
a_title.exts                = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_title.exts_dialog         = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_title.path_key            = 'path_title'

a_snap = AssetInfo()
a_snap.id                   = ASSET_SNAP_ID
a_snap.key                  = 's_snap'
a_snap.name                 = 'Snap'
a_snap.plural               = 'Snaps'
a_snap.fname_infix          = 'snap'
a_snap.kind_str             = 'image'
a_snap.exts                 = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_snap.exts_dialog          = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_snap.path_key             = 'path_snap'

a_boxfront = AssetInfo()
a_boxfront.id               = ASSET_BOXFRONT_ID
a_boxfront.key              = 's_boxfront'
a_boxfront.name             = 'Boxfront'
a_boxfront.description      = 'Boxfront / Cabinet'
a_boxfront.plural           = 'Boxfronts'
a_boxfront.fname_infix      = 'boxfront'
a_boxfront.kind_str         = 'image'
a_boxfront.exts             = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_boxfront.exts_dialog      = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_boxfront.path_key         = 'path_boxfront'

a_boxback = AssetInfo()
a_boxback.id                = ASSET_BOXBACK_ID
a_boxback.key               = 's_boxback'
a_boxback.name              = 'Boxback'
a_boxback.description       = 'Boxback / CPanel'
a_boxback.plural            = 'Boxbacks'
a_boxback.fname_infix       = 'boxback'
a_boxback.kind_str          = 'image'
a_boxback.exts              = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_boxback.exts_dialog       = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_boxback.path_key          = 'path_boxback'

a_cartridge = AssetInfo()
a_cartridge.id              = ASSET_CARTRIDGE_ID
a_cartridge.key             = 's_cartridge'
a_cartridge.name            = 'Cartridge'
a_cartridge.description     = 'Cartridge / PCB'
a_cartridge.plural          = 'Cartridges'
a_cartridge.fname_infix     = 'cartridge'
a_cartridge.kind_str        = 'image'
a_cartridge.exts            = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_cartridge.exts_dialog     = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_cartridge.path_key        = 'path_cartridge'

a_flyer = AssetInfo()
a_flyer.id                  = ASSET_FLYER_ID
a_flyer.key                 = 's_flyer'
a_flyer.name                = 'Flyer'
a_flyer.plural              = 'Flyers'
a_flyer.fname_infix         = 'flyer'
a_flyer.kind_str            = 'image'
a_flyer.fname_infix         = 'poster'
a_flyer.exts                = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_flyer.exts_dialog         = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_flyer.path_key            = 'path_flyer'

a_map = AssetInfo()
a_map.id                    = ASSET_MAP_ID
a_map.key                   = 's_map'
a_map.name                  = 'Map'
a_map.plural                = 'Maps'
a_map.fname_infix           = 'map'
a_map.kind_str              = 'image'
a_map.exts                  = asset_get_filesearch_extension_list(IMAGE_EXTENSION_LIST)
a_map.exts_dialog           = asset_get_dialog_extension_list(IMAGE_EXTENSION_LIST)
a_map.path_key              = 'path_map'

a_manual = AssetInfo()
a_manual.id                 = ASSET_MANUAL_ID
a_manual.key                = 's_manual'
a_manual.name               = 'Manual'
a_manual.plural             = 'Manuals'
a_manual.fname_infix        = 'manual'
a_manual.kind_str           = 'manual'
a_manual.exts               = asset_get_filesearch_extension_list(MANUAL_EXTENSION_LIST)
a_manual.exts_dialog        = asset_get_dialog_extension_list(MANUAL_EXTENSION_LIST)
a_manual.path_key           = 'path_manual'

#
# Get AssetInfo object by asset ID.
#
ASSET_INFO_DICT = {
    ASSET_ICON_ID       : a_icon,
    ASSET_FANART_ID     : a_fanart,
    ASSET_BANNER_ID     : a_banner,
    ASSET_POSTER_ID     : a_poster,
    ASSET_CLEARLOGO_ID  : a_clearlogo,
    ASSET_CONTROLLER_ID : a_controller,
    ASSET_TRAILER_ID    : a_trailer,
    ASSET_TITLE_ID      : a_title,
    ASSET_SNAP_ID       : a_snap,
    ASSET_BOXFRONT_ID   : a_boxfront,
    ASSET_BOXBACK_ID    : a_boxback,
    ASSET_CARTRIDGE_ID  : a_cartridge,
    ASSET_FLYER_ID      : a_flyer,
    ASSET_MAP_ID        : a_map,
    ASSET_MANUAL_ID     : a_manual,
}

#
# Get AssetInfo object by database key.
#
ASSET_INFO_KEY_DICT = {
    's_icon'       : a_icon,
    's_fanart'     : a_fanart,
    's_banner'     : a_banner,
    's_poster'     : a_poster,
    's_clearlogo'  : a_clearlogo,
    's_controller' : a_controller,
    's_trailer'    : a_trailer,
    's_title'      : a_title,
    's_snap'       : a_snap,
    's_boxfront'   : a_boxfront,
    's_boxback'    : a_boxback,
    's_cartridge'  : a_cartridge,
    's_flyer'      : a_flyer,
    's_map'        : a_map,
    's_manual'     : a_manual,
}

#
# Class to interact with the asset engine.
# This class uses the asset_infos, dictionary of AssetInfo indexed by asset_ID
#
class AssetInfoFactory(object):
        
    def get_all(self):
        return list(ASSET_INFO_DICT.values())

    def get_asset_kinds_for_roms(self):
        rom_asset_kinds = []
        for rom_asset_kind in ROM_ASSET_LIST:
            rom_asset_kinds.append(ASSET_INFO_DICT[rom_asset_kind])

        return rom_asset_kinds

    # IDs is a list (or an iterable that returns an asset ID
    # Returns a list of AssetInfo objects.
    def get_asset_list_by_IDs(self, IDs):
        asset_info_list = []
        for asset_ID in IDs: asset_info_list.append(ASSET_INFO_DICT[asset_ID])

        return asset_info_list

    def get_asset_info(self, asset_kind):
        asset_info = ASSET_INFO_DICT.get(asset_kind, None)

        if asset_info is None:
            log_error('get_asset_info() Wrong asset_kind = {0}'.format(asset_kind))
            return AssetInfo()

        return asset_info

    # todo: use 1 type of identifier not number constants and name strings ('s_icon')
    def get_asset_info_by_namekey(self, name_key):
        if name_key == '': return None
        kind = ASSET_KEYS_TO_CONSTANTS[name_key]

        return self.get_asset_info(kind)

# --- Global object to get asset info ---
g_assetFactory = AssetInfoFactory()

#
# Scheme DIR uses different directories for artwork and no sufixes.
#
# Assets    -> Assets info object
# AssetPath -> FileName object
# ROM       -> ROM name FileName object
#
# Returns a FileName object
#
def assets_get_path_noext_DIR(Asset, AssetPath, ROM):
    return AssetPath + ROM.getBaseNoExt()

#
# Scheme SUFIX uses suffixes for artwork. All artwork assets are stored in the same directory.
# Name example: "Sonic The Hedgehog (Europe)_a3e_title"
# First 3 characters of the objectID are added to avoid overwriting of images. For example, in the
# Favourites special category there could be ROMs with the same name for different systems.
#
# asset_ID         -> Assets ID defined in constants.py
# AssetPath        -> FileName object
# asset_base_noext -> Unicode string
# objectID         -> Object MD5 ID fingerprint (Unicode string)
#
# Returns a FileName object
#
def assets_get_path_noext_SUFIX(asset_ID, AssetPath, asset_base_noext, objectID = '000'):
    objectID_str = '_' + objectID[0:3]

    if   asset_ID == ASSET_ICON_ID:       asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_icon')
    elif asset_ID == ASSET_FANART_ID:     asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_fanart')
    elif asset_ID == ASSET_BANNER_ID:     asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_banner')
    elif asset_ID == ASSET_POSTER_ID:     asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_poster')
    elif asset_ID == ASSET_CLEARLOGO_ID:  asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_clearlogo')
    elif asset_ID == ASSET_CONTROLLER_ID: asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_controller')
    elif asset_ID == ASSET_TRAILER_ID:    asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_trailer')
    elif asset_ID == ASSET_TITLE_ID:      asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_title')
    elif asset_ID == ASSET_SNAP_ID:       asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_snap')
    elif asset_ID == ASSET_BOXFRONT_ID:   asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_boxfront')
    elif asset_ID == ASSET_BOXBACK_ID:    asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_boxback')
    elif asset_ID == ASSET_CARTRIDGE_ID:  asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_cartridge')
    elif asset_ID == ASSET_FLYER_ID:      asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_flyer')
    elif asset_ID == ASSET_MAP_ID:        asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_map')
    elif asset_ID == ASSET_MANUAL_ID:     asset_path_noext_FN = AssetPath.pjoin(asset_base_noext + objectID_str + '_manual')
    else:
        asset_path_noext_FN = FileName('')
        log_error('assets_get_path_noext_SUFIX() Wrong asset_ID = {0}'.format(asset_ID))

    return asset_path_noext_FN

#
# Get a list of enabled assets.
#
# Returns tuple:
# configured_bool_list    List of boolean values. It has all assets defined in ROM_ASSET_LIST
# unconfigured_name_list  List of disabled asset names
#
def asset_get_configured_dir_list(launcher):
    configured_bool_list   = [False] * len(ROM_ASSET_LIST)
    unconfigured_name_list = []

    # >> Check if asset paths are configured or not
    for i, asset in enumerate(ROM_ASSET_LIST):
        A = assets_get_info_scheme(asset)
        configured_bool_list[i] = True if launcher[A.path_key] else False
        if not configured_bool_list[i]: 
            unconfigured_name_list.append(A.name)
            log_verb('asset_get_enabled_asset_list() {0:<9} path unconfigured'.format(A.name))
        else:
            log_debug('asset_get_enabled_asset_list() {0:<9} path configured'.format(A.name))

    return (configured_bool_list, unconfigured_name_list)

#
# Get a list of assets with duplicated paths. Refuse to do anything if duplicated paths found.
#
def asset_get_duplicated_dir_list(launcher):
    duplicated_bool_list   = [False] * len(ROM_ASSET_LIST)
    duplicated_name_list   = []

    # >> Check for duplicated asset paths
    for i, asset_i in enumerate(ROM_ASSET_LIST[:-1]):
        A_i = assets_get_info_scheme(asset_i)
        for j, asset_j in enumerate(ROM_ASSET_LIST[i+1:]):
            A_j = assets_get_info_scheme(asset_j)
            # >> Exclude unconfigured assets (empty strings).
            if not launcher[A_i.path_key] or not launcher[A_j.path_key]: continue
            # log_debug('asset_get_duplicated_asset_list() Checking {0:<9} vs {1:<9}'.format(A_i.name, A_j.name))
            if launcher[A_i.path_key] == launcher[A_j.path_key]:
                duplicated_bool_list[i] = True
                duplicated_name_list.append('{0} and {1}'.format(A_i.name, A_j.name))
                log_info('asset_get_duplicated_asset_list() DUPLICATED {0} and {1}'.format(A_i.name, A_j.name))

    return duplicated_name_list

#
# Search for local assets and place found files into a list.
# Returned list all has assets as defined in ROM_ASSET_LIST.
# This function is used in the ROM Scanner.
#
# launcher               -> launcher dictionary
# ROMFile                -> FileName object
# enabled_ROM_asset_list -> list of booleans
#
# todo: !!!! Orphaned method?
def assets_search_local_cached_assets(launcher, ROMFile, enabled_ROM_asset_list):
    log_verb('assets_search_local_cached_assets() Searching for ROM local assets...')
    local_asset_list = [''] * len(ROM_ASSET_LIST)
    rom_basename_noext = ROMFile.getBase_noext()
    for i, asset_kind in enumerate(ROM_ASSET_LIST):
        AInfo = assets_get_info_scheme(asset_kind)
        if not enabled_ROM_asset_list[i]:
            log_verb('assets_search_local_cached_assets() Disabled {0:<9}'.format(AInfo.name))
            continue
        local_asset = misc_search_file_cache(launcher[AInfo.path_key], rom_basename_noext, AInfo.exts)

        if local_asset:
            local_asset_list[i] = local_asset.getPath()
            log_verb('assets_search_local_cached_assets() Found    {0:<9} "{1}"'.format(AInfo.name, local_asset_list[i]))
        else:
            local_asset_list[i] = ''
            log_verb('assets_search_local_cached_assets() Missing  {0:<9}'.format(AInfo.name))

    return local_asset_list

#
# Search for local assets and put found files into a list.
# This function is used in _roms_add_new_rom() where there is no need for a file cache.
#
def assets_search_local_assets(launcher, ROMFile, enabled_ROM_asset_list):
    log_verb('assets_search_local_assets() Searching for ROM local assets...')
    local_asset_list = [''] * len(ROM_ASSET_LIST)
    for i, asset_kind in enumerate(ROM_ASSET_LIST):
        AInfo = assets_get_info_scheme(asset_kind)
        if not enabled_ROM_asset_list[i]:
            log_verb('assets_search_local_assets() Disabled {0:<9}'.format(AInfo.name))
            continue
        asset_path = FileName(launcher[AInfo.path_key])
        local_asset = misc_look_for_file(asset_path, ROMFile.getBase_noext(), AInfo.exts)

        if local_asset:
            local_asset_list[i] = local_asset.getPath()
            log_verb('assets_search_local_assets() Found    {0:<9} "{1}"'.format(AInfo.name, local_asset_list[i]))
        else:
            local_asset_list[i] = ''
            log_verb('assets_search_local_assets() Missing  {0:<9}'.format(AInfo.name))

    return local_asset_list

#
# A) This function checks if all path_* share a common root directory. If so
#    this function returns that common directory as an Unicode string.
# B) If path_* do not share a common root directory this function returns ''.
#
def assets_get_ROM_asset_path(launcher):
    ROM_asset_path = ''
    duplicated_bool_list = [False] * len(ROM_ASSET_LIST)
    AInfo_first = assets_get_info_scheme(ROM_ASSET_LIST[0])
    path_first_asset_FN = FileName(launcher[AInfo_first.path_key])
    log_debug('assets_get_ROM_asset_path() path_first_asset "{0}"'.format(path_first_asset_FN.getPath()))
    for i, asset_kind in enumerate(ROM_ASSET_LIST):
        AInfo = assets_get_info_scheme(asset_kind)
        current_path_FN = FileName(launcher[AInfo.path_key])
        if current_path_FN.getDir() == path_first_asset_FN.getDir():
            duplicated_bool_list[i] = True

    return path_first_asset_FN.getDir() if all(duplicated_bool_list) else ''

# #################################################################################################
# #################################################################################################
# Data storage objects.
# #################################################################################################
# #################################################################################################
#
# * Repository class for creating and retrieveing Categories/Launchers/ROM Collection objects.
#
# * This object only retrieves database dictionaries. Actual objects are created by the
#   class AELObjectFactory().
#
# * ROM objects can be created exclusively by Launcher objects using the ROMSetRepository class.
#
class ObjectRepository(object):
    def __init__(self, g_PATHS, g_settings):
        self.PATHS = g_PATHS
        self.settings = g_settings

        # Categories/Launchers are needed for virtually every AEL operation so load it
        # right now.
        # When AEL is used for the first time and categories.xml does not exists, just create
        # empty structures.
        # ROM Collection index is loaded lazily if needed.
        self.header_dic  = {}
        self.categories  = {}
        self.launchers   = {}
        self.collections = None
        if not self.PATHS.CATEGORIES_FILE_PATH.exists():
            log_debug('ObjectRepository::init() categories.xml does not exist. Creating empty data.')
        else:
            fs_load_catfile(self.PATHS.CATEGORIES_FILE_PATH,
                            self.header_dic, self.categories, self.launchers)

    def num_categories(self): return len(self.categories)

    def num_launchers(self): return len(self.launchers)

    def num_launchers_in_cat(self, category_id):
        # This implementation is slow, must be optimised.
        num_launchers = 0
        for launcher_id in self.launchers:
            if self.launchers[launcher_id]['categoryID'] != category_id: continue
            num_launchers += 1

        return num_launchers

    #
    # Finds an actual Category by ID in the database.
    # Returns a Category database dictionary or None if not found.
    #
    def find_category(self, category_id):
        if category_id in self.categories:
            category_dic = self.categories[category_id]
        else:
            category_dic = None

        return category_dic

    def find_category_all(self):
        category_dic_list = []
        for category_key in sorted(self.categories, key = lambda c : self.categories[c]['m_name']):
            category_dic_list.append(self.categories[category_key])

        return category_dic_list

    # Returns an OrderedDict, key is category_id and value is the Category name.
    # Categories are ordered alphabetically by m_name.
    # This function is useful for select dialogs.
    def get_categories_odict(self):
        categories_odict = collections.OrderedDict()
        # sorted(category_list, key = lambda c : c.get_name())
        for category_id in sorted(self.categories, key = lambda c : self.categories[c]['m_name']):
            categories_odict[category_id] = self.categories[category_id]['m_name']

        return categories_odict

    #
    # Finds an actual Launcher by ID in the database.
    # Returns a Launcher database dictionary or None if not found.
    #
    def find_launcher(self, launcher_id):
        if launcher_id in self.launchers:
            launcher_dic = self.launchers[launcher_id]
        else:
            launcher_dic = None

        return launcher_dic

    #
    # Returns a list of launchers belonging to category_id
    # Launchers are sorted alphabetically by m_name.
    #
    def find_launchers_by_category_id(self, category_id):
        launchers_dic_list = []
        for launcher_id in self.launchers:
            if self.launchers[launcher_id]['categoryID'] != category_id: continue
            launchers_dic_list.append(self.launchers[launcher_id])

        sorted_launcher_dic_list = []
        for launcher_dic in sorted(launchers_dic_list, key = lambda c : c['m_name']):
            sorted_launcher_dic_list.append(launcher_dic)

        return sorted_launcher_dic_list

    # Removes a category from the database.
    # Launchers belonging to this Category must be deleted first, otherwise will become orphaned.
    def delete_category(self, category):
        category_id = category.get_id()
        del self.categories[category_id]
        self.commit_database()

    #
    # Removes a Launcher from the database.
    # If Launcher supports ROMs it also removes all files associated with the Launcher.
    #
    def delete_launcher(self, launcher):
        if launcher.supports_launching_roms(): launcher.delete_ROM_databases()
        del self.launchers[launcher.get_id()]
        self.save_main_database()

    def save_category(self, category_dic):
        self.categories[category_dic['id']] = category_dic
        self.save_main_database()

    #
    # Use this function instead of save_object() when the launcher timestamp must be controlled.
    #
    def save_launcher(self, launcher_dic, update_launcher_timestamp = True):
        if update_launcher_timestamp:
            launcher_dic['timestamp_launcher'] = time.time()
        self.launchers[launcher_dic['id']] = launcher_dic
        self.save_main_database()

    # Saves the Categories and Launchers in the categories.xml database.
    # Updates the database timestamp.
    def save_main_database(self):
        # >> time.time() returns a float. Usually precision is much better than a second,
        # >> but not always.
        # >> See https://docs.python.org/2/library/time.html#time.time
        # NOTE When updating reports timestamp of categories/launchers this must not be modified.
        self.header_dic['database_version'] = '0.10.0'
        self.header_dic['update_timestamp'] = time.time()
        fs_write_catfile(self.PATHS.CATEGORIES_FILE_PATH,
                         self.header_dic, self.categories, self.launchers)

# -------------------------------------------------------------------------------------------------
# Repository class for Collection objects.
# Arranges retrieving and storing of the Collection launchers from and into the xml data file.
# -------------------------------------------------------------------------------------------------
class CollectionRepository(object):
    def __init__(self, PATHS, settings, obj_factory):
        # log_debug('CollectionRepository::__init__()')
        self.obj_factory = obj_factory

    def _parse_xml_to_dictionary(self, collection_element):
        __debug_xml_parser = False
        collection = { 'type': LAUNCHER_COLLECTION }
        # Parse child tags of category
        for collection_child in collection_element:
            # By default read strings
            xml_text = collection_child.text if collection_child.text is not None else ''
            xml_text = text_unescape_XML(xml_text)
            xml_tag  = collection_child.tag
            if __debug_xml_parser: log_debug('{0} --> {1}'.format(xml_tag, xml_text.encode('utf-8')))

            # Internal data is always stored as Unicode. ElementTree already outputs Unicode.
            collection[xml_tag] = xml_text

        return collection

    def find(self, collection_id):
        collection_element = self.data_context.get_node('Collection', collection_id)
        if collection_element is None:
            log_debug('Cannot find collection with id {}'.format(collection_id))
            return None
        collection_dic = self._parse_xml_to_dictionary(collection_element)
        collection = self.launcher_factory.create(collection_dic)

        return collection

    def find_all(self):
        collections = []
        collection_elements = self.data_context.get_nodes('Collection')
        log_debug('Found {0} collections'.format(len(collection_element)))
        for collection_element in collection_elements:
            collection_dic = self._parse_xml_to_dictionary(collection_element)
            collection = self.launcher_factory.create(collection_dic)
            collections.append(collection)

        return collections

    def save(self, collection, update_launcher_timestamp = True):
        if update_launcher_timestamp:
            collection.update_timestamp()
        collection_id   = collection.get_id()
        collection_dic = collection.get_data_dic()
        self.data_context.save_node('Collection', collection_id, collection_dic)
        self.data_context.commit()

    def save_multiple(self, collections, update_launcher_timestamp = True):
        for collection in collections:
            if update_launcher_timestamp:
                collection.update_timestamp()
            collection_id   = collection.get_id()
            collection_dic = collection.get_data_dic()
            self.data_context.save_node('Collection', collection_id, collection_dic)
        self.data_context.commit()

    def delete(self, collection):
        collection_id = collection.get_id()
        self.data_context.remove_node('Collection', collection_id)
        self.data_context.commit()

# -------------------------------------------------------------------------------------------------
# Rom sets constants
# -------------------------------------------------------------------------------------------------
ROMSET_CPARENT  = '_index_CParent'
ROMSET_PCLONE   = '_index_PClone'
ROMSET_PARENTS  = '_parents'
ROMSET_DAT      = '_DAT'

# -------------------------------------------------------------------------------------------------
# --- Repository class for ROM set objects of Standard ROM Launchers ---
# Arranges retrieving and storing of roms belonging to a particular standard ROM launcher.
#
# NOTE ROMs in a collection are stored as a list and ROMs in Favourites are stored as
#      a dictionary. Convert the Collection list into an ordered dictionary and then
#      converted back the ordered dictionary into a list before saving the collection.
# -------------------------------------------------------------------------------------------------
class ROMSetRepository(object):
    def __init__(self, PATHS, settings, store_as_dictionary = True):
        self.PATHS = PATHS
        self.settings = settings
        self.store_as_dictionary = store_as_dictionary
        self.ROMs_dir = self.PATHS.ROMS_DIR

    #
    # Loads ROM databases from disk
    #
    def load_ROMs(self, launcher, view_mode = None):
        log_debug('ROMSetRepository::load_ROMs() Starting ...')
        roms_base_noext = launcher.get_roms_base()
        if view_mode is None: view_mode = launcher.get_display_mode()

        if roms_base_noext is None:
            repository_file = self.ROMs_dir
        elif view_mode == LAUNCHER_DMODE_FLAT:
            repository_file = self.ROMs_dir.pjoin('{}.json'.format(roms_base_noext))
        else:
            repository_file = self.ROMs_dir.pjoin('{}_parents.json'.format(roms_base_noext))
        if not repository_file.exists():
            log_warning('Launcher JSON not found "{0}"'.format(repository_file.getPath()))
            return None
        log_info('Loading ROMs in Launcher ({0}:{1}) ...'.format(
            launcher.get_launcher_type_name(), launcher.get_name()))
        log_info('View mode {0}...'.format(view_mode))

        roms_data = {}
        # --- Parse using json module ---
        # >> On Github issue #8 a user had an empty JSON file for ROMs. This raises
        #    exception exceptions.ValueError and launcher cannot be deleted. Deal
        #    with this exception so at least launcher can be rescanned.
        log_verb('RomSetRepository.find_by_launcher(): Loading roms from file {0}'.format(repository_file.getPath()))
        try:
            roms_data = repository_file.readJson()
        except ValueError:
            statinfo = repository_file.stat()
            log_error('RomSetRepository.find_by_launcher(): ValueError exception in json.load() function')
            log_error('RomSetRepository.find_by_launcher(): Dir  {0}'.format(repository_file.getPath()))
            log_error('RomSetRepository.find_by_launcher(): Size {0}'.format(statinfo.st_size))
            return None

        # --- Extract roms from JSON data structure and ensure version is correct ---
        if roms_data and isinstance(roms_data, list) and 'control' in roms_data[0]:
            control_str = roms_data[0]['control']
            version_int = roms_data[0]['version']
            roms_data   = roms_data[1]

        roms = {}
        if isinstance(roms_data, list):
            for rom_data in roms_data:
                r = Rom(rom_data)
                key = r.get_id()
                roms[key] = r
        else:
            for key in roms_data:
                r = Rom(roms_data[key])
                roms[key] = r

        return roms

    def find_index_file_by_launcher(self, launcher, type):
        roms_base_noext = launcher.get_roms_base()
        repository_file = self.roms_dir.pjoin('{0}{1}.json'.format(roms_base_noext, type))

        if not repository_file.exists():
            log_warning('RomSetRepository.find_index_file_by_launcher(): File not found {0}'.format(repository_file.getPath()))
            return None

        log_verb('RomSetRepository.find_index_file_by_launcher(): Loading rom index from file {0}'.format(repository_file.getPath()))
        try:
            index_data = repository_file.readJson()
        except ValueError:
            statinfo = repository_file.stat()
            log_error('RomSetRepository.find_index_file_by_launcher(): ValueError exception in json.load() function')
            log_error('RomSetRepository.find_index_file_by_launcher(): Dir  {0}'.format(repository_file.getPath()))
            log_error('RomSetRepository.find_index_file_by_launcher(): Size {0}'.format(statinfo.st_size))
            return None

        return index_data

    def save_rom_set(self, launcher, roms, view_mode = None):
        romdata = None
        if self.store_as_dictionary:
            romdata = {key: roms[key].get_data() for (key) in roms}
        else:
            romdata = [roms[key].get_data() for (key) in roms]

        # --- Create JSON data structure, including version number ---
        control_dic = {
            'control' : 'Advanced Emulator {} ROMs'.format(launcher.get_launcher_type_name()),
            'version' : AEL_STORAGE_FORMAT
        }
        raw_data = []
        raw_data.append(control_dic)
        raw_data.append(romdata)

        # >> Get file names
        roms_base_noext = launcher.get_roms_base()

        if view_mode is None:
            view_mode = launcher.get_display_mode()

        if roms_base_noext is None:
            repository_file = self.roms_dir
        elif view_mode == LAUNCHER_DMODE_FLAT:
            repository_file = self.roms_dir.pjoin('{}.json'.format(roms_base_noext))
        else:
            repository_file = self.roms_dir.pjoin('{}_parents.json'.format(roms_base_noext))

        log_verb('RomSetRepository.save_rom_set() Dir  {0}'.format(self.roms_dir.getPath()))
        log_verb('RomSetRepository.save_rom_set() JSON {0}'.format(repository_file.getPath()))

        # >> Write ROMs JSON dictionary.
        # >> Do note that there is a bug in the json module where the ensure_ascii=False flag can produce
        # >> a mix of unicode and str objects.
        # >> See http://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence
        try:
            repository_file.writeJson(raw_data)
        except OSError:
            kodi_notify_warn('(OSError) Cannot write {0} file'.format(repository_file.getPath()))
            log_error('RomSetRepository.save_rom_set() (OSError) Cannot write {0} file'.format(repository_file.getPath()))
        except IOError:
            kodi_notify_warn('(IOError) Cannot write {0} file'.format(repository_file.getPath()))
            log_error('RomSetRepository.save_rom_set() (IOError) Cannot write {0} file'.format(repository_file.getPath()))

    # -------------------------------------------------------------------------------------------------
    # Standard ROM databases
    # -------------------------------------------------------------------------------------------------
    #
    # <roms_base_noext>.json
    # <roms_base_noext>.xml
    # <roms_base_noext>_index_CParent.json
    # <roms_base_noext>_index_PClone.json
    # <roms_base_noext>_parents.json
    # <roms_base_noext>_DAT.json
    #
    def delete_all_by_launcher(self, launcher):
        roms_base_noext = launcher.get_roms_base()

        # >> Delete ROMs JSON file
        roms_json_FN = self.roms_dir.pjoin(roms_base_noext + '.json')
        if roms_json_FN.exists():
            log_info('Deleting ROMs JSON    "{0}"'.format(roms_json_FN.getPath()))
            roms_json_FN.unlink()

        # >> Delete ROMs info XML file
        roms_xml_FN = self.roms_dir.pjoin(roms_base_noext + '.xml')
        if roms_xml_FN.exists():
            log_info('Deleting ROMs XML     "{0}"'.format(roms_xml_FN.getPath()))
            roms_xml_FN.unlink()

        # >> Delete No-Intro/Redump stuff if exist
        roms_index_CParent_FN = self.roms_dir.pjoin(roms_base_noext + '_index_CParent.json')
        if roms_index_CParent_FN.exists():
            log_info('Deleting CParent JSON "{0}"'.format(roms_index_CParent_FN.getPath()))
            roms_index_CParent_FN.unlink()

        roms_index_PClone_FN = self.roms_dir.pjoin(roms_base_noext + '_index_PClone.json')
        if roms_index_PClone_FN.exists():
            log_info('Deleting PClone JSON  "{0}"'.format(roms_index_PClone_FN.getPath()))
            roms_index_PClone_FN.unlink()

        roms_parents_FN = self.roms_dir.pjoin(roms_base_noext + '_parents.json')
        if roms_parents_FN.exists():
            log_info('Deleting parents JSON "{0}"'.format(roms_parents_FN.getPath()))
            roms_parents_FN.unlink()

        roms_DAT_FN = self.roms_dir.pjoin(roms_base_noext + '_DAT.json')
        if roms_DAT_FN.exists():
            log_info('Deleting DAT JSON     "{0}"'.format(roms_DAT_FN.getPath()))
            roms_DAT_FN.unlink()

        return

    def delete_by_launcher(self, launcher, kind):
        roms_base_noext     = launcher.get_roms_base()
        rom_set_file_name   = roms_base_noext + kind
        rom_set_path        = self.roms_dir.pjoin(rom_set_file_name + '.json')

        if rom_set_path.exists():
            log_info('delete_by_launcher() Deleting {0}'.format(rom_set_path.getPath()))
            rom_set_path.unlink()

        return

# -------------------------------------------------------------------------------------------------
# Strategy class for updating the ROM play statistics.
# Updates the amount of times a ROM is played and which rom recently has been played.
# Uses functions in disk_IO.py for maximum speed.
# ROMStatisticsStrategy() is exclusively called at ROM execution time.
# -------------------------------------------------------------------------------------------------
class ROMStatisticsStrategy(object):
    def __init__(self, PATHS, settings):
        self.PATHS = PATHS
        self.settings = settings
        self.MAX_RECENT_PLAYED_ROMS = 100
        # self.recent_played_launcher = recent_played_launcher
        # self.most_played_launcher = most_played_launcher

    def update_launched_rom_stats(self, recent_rom):
        # --- Compute ROM recently played list ---
        recently_played_roms = self.recent_played_launcher.get_roms()
        recently_played_roms = [rom for rom in recently_played_roms if rom.get_id() != recent_rom.get_id()]
        recently_played_roms.insert(0, recent_rom)

        if len(recently_played_roms) > self.MAX_RECENT_PLAYED_ROMS:
            log_debug('RomStatisticsStrategy() len(recently_played_roms) = {0}'.format(len(recently_played_roms)))
            log_debug('RomStatisticsStrategy() Trimming list to {0} ROMs'.format(self.MAX_RECENT_PLAYED_ROMS))

            temp_list            = recently_played_roms[:self.MAX_RECENT_PLAYED_ROMS]
            recently_played_roms = temp_list

        self.recent_played_launcher.update_rom_set(recently_played_roms)

        recent_rom.increase_launch_count()

        # --- Compute most played ROM statistics ---
        most_played_roms = self.most_played_launcher.get_roms()
        if most_played_roms is None:
            most_played_roms = []
        else:
            most_played_roms = [rom for rom in most_played_roms if rom.get_id() != recent_rom.get_id()]
        most_played_roms.append(recent_rom)
        self.most_played_launcher.update_rom_set(most_played_roms)

# -------------------------------------------------------------------------------------------------
# Abstract base class for business objects which support the generic
# metadata fields and assets.
#
# --- Class hierarchy ---
#
# MetaDataItemABC(object) (abstract class)
# |
# |----- Category
# |      |
# |      |----- VirtualCategory
# |
# |----- ROM
# |
# |----- LauncherABC (abstract class)
#        |
#        |----- StandaloneLauncher (Standalone launcher)
#        |
#        |----- ROMLauncherABC (abstract class)
#               |
#               |----- CollectionLauncher (ROM Collection launcher)
#               |
#               |----- VirtualLauncher (Browse by ... launcher)
#               |
#               |----- StandardRomLauncher (Standard launcher)
#               |
#               |----- LnkLauncher
#               |
#               |----- RetroplayerLauncher
#               |
#               |----- RetroarchLauncher
#               |
#               |----- SteamLauncher
#               |
#               |----- NvidiaGameStreamLauncher
#
# -------------------------------------------------------------------------------------------------
class MetaDataItemABC(object):
    __metaclass__ = abc.ABCMeta

    #
    # Addon PATHS is required to store/retrieve assets.
    # Addon settings is required because the way the metadata is displayed may depend on
    # some addon settings.
    #
    def __init__(self, PATHS, addon_settings, entity_data, objectRepository):
        self.PATHS = PATHS
        self.settings = addon_settings
        self.entity_data = entity_data
        self.objectRepository = objectRepository

    # --------------------------------------------------------------------------------------------
    # Core functions
    # --------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def get_object_name(self): pass

    @abc.abstractmethod
    def get_assets_kind(self): pass

    @abc.abstractmethod
    def save_to_disk(self): pass

    @abc.abstractmethod
    def delete_from_disk(self): pass

    # --- Database ID and utilities ---------------------------------------------------------------
    def set_id(self, id):
        self.entity_data['id'] = id

    def get_id(self):
        return self.entity_data['id']

    def get_data_dic(self):
        return self.entity_data

    def copy_of_data_dic(self):
        return self.entity_data.copy()

    def set_custom_attribute(self, key, value):
        self.entity_data[key] = value

    def get_custom_attribute(self, key, default_value = None):
        return self.entity_data[key] if key in self.entity_data else default_value

    def import_data_dic(self, data):
        for key in data:
            self.entity_data[key] = data[key]

    def dump_data_dic_to_log(self):
        log_debug('Dumping object {0}'.format(self.__class__))
        for key in self.entity_data:
            log_debug('[{0}] = {1}'.format(key, unicode(self.entity_data[key])))

    # NOTE Rename to get_filename_from_field()
    def _get_value_as_filename(self, field):
        if not field in self.entity_data: return None
        path = self.entity_data[field]
        if path == '': return None

        return FileName(path)

    # --- Metadata --------------------------------------------------------------------------------
    def get_name(self):
        return self.entity_data['m_name'] if 'm_name' in self.entity_data else 'Unknown'

    def set_name(self, name):
        self.entity_data['m_name'] = name

    def get_releaseyear(self):
        return self.entity_data['m_year'] if 'm_year' in self.entity_data else ''

    def set_releaseyear(self, releaseyear):
        self.entity_data['m_year'] = releaseyear

    def get_genre(self):
        return self.entity_data['m_genre'] if 'm_genre' in self.entity_data else ''

    def set_genre(self, genre):
        self.entity_data['m_genre'] = genre

    def get_developer(self):
        return self.entity_data['m_developer'] if 'm_developer' in self.entity_data else ''

    def set_developer(self, developer):
        self.entity_data['m_developer'] = developer

    # In AEL 0.9.7 m_rating is stored as a string.
    def get_rating(self):
        return int(self.entity_data['m_rating']) if self.entity_data['m_rating'] else ''

    def set_rating(self, rating):
        try:
            self.entity_data['m_rating'] = int(rating)
        except:
            self.entity_data['m_rating'] = ''

    def get_plot(self):
        return self.entity_data['m_plot'] if 'm_plot' in self.entity_data else ''

    def set_plot(self, plot):
        self.entity_data['m_plot'] = plot

    #
    # Used when rendering Categories/Launchers/ROMs
    #
    def get_trailer(self):
        return self.entity_data['s_trailer'] if 's_trailer' in self.entity_data else ''

    def set_trailer(self, trailer_str):
        self.entity_data['s_trailer'] = trailer_str

    # --- Finished status stuff -------------------------------------------------------------------
    def is_finished(self):
        return 'finished' in self.entity_data and self.entity_data['finished']

    def get_finished_str(self):
        finished = self.entity_data['finished']
        finished_display = 'Finished' if finished == True else 'Unfinished'

        return finished_display

    def change_finished_status(self):
        finished = self.entity_data['finished']
        finished = False if finished else True
        self.entity_data['finished'] = finished

    # --- Assets/artwork --------------------------------------------------------------------------
    def has_asset(self, asset_info):
        if not asset_info.key in self.entity_data: return False

        return self.entity_data[asset_info.key] != None and self.entity_data[asset_info.key] != ''

    def get_asset_str(self, asset_info):
        return self.entity_data[asset_info.key] if asset_info.key in self.entity_data else ''

    def get_asset_FN(self, asset_info):
        return FileName(self.get_asset_str(asset_info))

    def set_asset(self, asset_info, path_FN):
        self.entity_data[asset_info.key] = path_FN.getPath()

    def clear_asset(self, asset_info):
        self.entity_data[asset_info.key] = ''

    #
    # Get a list of the assets that can be mapped.
    # Returns a list of AssetInfo objects.
    #
    def get_default_asset_list(self):
        return g_assetFactory.get_asset_list_by_IDs(DEFAULTABLE_ASSET_ID_LIST)

# -------------------------------------------------------------------------------------------------
# Class representing an AEL Cateogry.
# Contains code to generate the context menus passed to Dialog.select()
# -------------------------------------------------------------------------------------------------
class Category(MetaDataItemABC):
    def __init__(self, PATHS, settings, category_dic, objectRepository):
        # Concrete classes are responsible of creating a default entity_data dictionary
        # with sensible defaults.
        if category_dic is None:
            category_dic = fs_new_category()
            category_dic['id'] = misc_generate_random_SID()
        super(Category, self).__init__(PATHS, settings, category_dic, objectRepository)

    def get_object_name(self): return 'Category'

    def get_assets_kind(self): return KIND_ASSET_CATEGORY

    def is_virtual(self): return False

    def save_to_disk(self): self.objectRepository.save_category(self.entity_data)

    def delete_from_disk(self):
        # Object becomes invalid after deletion.
        self.objectRepository.delete_category(self.entity_data)
        self.entity_data = None
        self.objectRepository = None

    def num_launchers(self):
        return self.objectRepository.num_launchers_in_cat(self.entity_data['id'])

    def get_main_edit_options(self):
        options = collections.OrderedDict()
        options['EDIT_METADATA']       = 'Edit Metadata ...'
        options['EDIT_ASSETS']         = 'Edit Assets/Artwork ...'
        options['EDIT_DEFAULT_ASSETS'] = 'Choose default Assets/Artwork ...'
        options['CATEGORY_STATUS']     = 'Category status: {0}'.format(self.get_finished_str())
        options['EXPORT_CATEGORY_XML'] = 'Export Category XML configuration ...'
        options['DELETE_CATEGORY']     = 'Delete Category'

        return options

    def get_metadata_edit_options(self):
        # NOTE The Category NFO file logic must be moved to this class. Settings not need to
        #      be used as a parameter here.
        NFO_FileName = fs_get_category_NFO_name(self.settings, self.entity_data)
        NFO_found_str = 'NFO found' if NFO_FileName.exists() else 'NFO not found'
        plot_str = text_limit_string(self.get_plot(), PLOT_STR_MAXSIZE)

        options = collections.OrderedDict()
        options['EDIT_METADATA_TITLE']       = "Edit Title: '{0}'".format(self.get_name())
        options['EDIT_METADATA_RELEASEYEAR'] = "Edit Release Year: '{0}'".format(self.get_releaseyear())
        options['EDIT_METADATA_GENRE']       = "Edit Genre: '{0}'".format(self.get_genre())
        options['EDIT_METADATA_DEVELOPER']   = "Edit Developer: '{0}'".format(self.get_developer())
        options['EDIT_METADATA_RATING']      = "Edit Rating: '{0}'".format(self.get_rating())
        options['EDIT_METADATA_PLOT']        = "Edit Plot: '{0}'".format(plot_str)
        options['IMPORT_NFO_FILE']           = 'Import NFO file (default, {0})'.format(NFO_found_str)
        options['IMPORT_NFO_FILE_BROWSE']    = 'Import NFO file (browse NFO file) ...'
        options['SAVE_NFO_FILE']             = 'Save NFO file (default location)'

        return options

    #
    # Returns an ordered dictionary with all the object assets, ready to be edited.
    # Keys are AssetInfo objects.
    # Values are the current file for the asset as Unicode string or '' if the asset is not set.
    #
    def get_assets_odict(self):
        asset_info_list = g_assetFactory.get_asset_list_by_IDs(CATEGORY_ASSET_ID_LIST)
        asset_odict = collections.OrderedDict()
        for asset_info in asset_info_list:
            asset_fname_str = self.entity_data[asset_info.key] if self.entity_data[asset_info.key] else ''
            asset_odict[asset_info] = asset_fname_str

        return asset_odict

    #
    # Get a list of the assets that can be mapped to a defaultable asset.
    # They must be images, no videos, no documents.
    #
    def get_mappable_asset_list(self):
        return g_assetFactory.get_asset_list_by_IDs(MAPPABLE_CATEGORY_ASSET_ID_LIST)

    #
    # Gets the database filename mapped for asset_info.
    # Note that the mapped asset uses diferent fields wheter it is a Category/Launcher/ROM
    #
    def get_mapped_asset_key(self, asset_info):
        return self.entity_data[asset_info.default_key]

    def set_mapped_asset_key(self, asset_info, mapped_to_info):
        self.entity_data[asset_info.default_key] = mapped_to_info.key

# -------------------------------------------------------------------------------------------------
# Class representing the virtual categories in AEL.
# All ROM Collections is a Virtual Category.
# ...
# -------------------------------------------------------------------------------------------------
class VirtualCategory(MetaDataItemABC):
    #
    # obj_dic is mandatory in Virtual Categories an must have the following fields:
    #  1) id
    #  2) type
    #  3) m_name
    #
    def __init__(self, PATHS, settings, obj_dic, objectRepository):
        # Concrete classes are responsible of creating a default entity_data dictionary
        # with sensible defaults.
        # This object is special, obj_dic must be not None and have certain fields.
        entity_data = fs_new_category()
        entity_data['id'] = obj_dic['id']
        entity_data['type'] = obj_dic['type']
        entity_data['m_name'] = obj_dic['m_name']
        super(VirtualCategory, self).__init__(PATHS, settings, entity_data, objectRepository)

    def get_object_name(self): return 'Virtual Category'

    def get_assets_kind(self): return KIND_ASSET_CATEGORY

    def is_virtual(self): return True

    def save_to_disk(self): pass

    def delete_from_disk(self): pass

# -------------------------------------------------------------------------------------------------
# Class representing a ROM file you can play through AEL.
# -------------------------------------------------------------------------------------------------
class ROM(MetaDataItemABC):
    def __init__(self, rom_data = None):
        super(ROM, self).__init__(None, None, rom_data) #todo
        if self.entity_data is None:
            self.entity_data = {
             'id' : misc_generate_random_SID(),
             'm_name' : '',
             'm_year' : '',
             'm_genre' : '',
             'm_developer' : '',
             'm_nplayers' : '',
             'm_esrb' : ESRB_PENDING,
             'm_rating' : '',
             'm_plot' : '',
             'filename' : '',
             'disks' : [],
             'altapp' : '',
             'altarg' : '',
             'finished' : False,
             'nointro_status' : NOINTRO_STATUS_NONE,
             'pclone_status' : PCLONE_STATUS_NONE,
             'cloneof' : '',
             's_title' : '',
             's_snap' : '',
             's_boxfront' : '',
             's_boxback' : '',
             's_cartridge' : '',
             's_fanart' : '',
             's_banner' : '',
             's_clearlogo' : '',
             's_flyer' : '',
             's_map' : '',
             's_manual' : '',
             's_trailer' : ''
             }

    # is this virtual only? Should we make a VirtualRom(Rom)?
    def get_launcher_id(self):
        return self.entity_data['launcherID']

    def is_virtual_rom(self):
        return 'launcherID' in self.entity_data

    def get_nointro_status(self):
        return self.entity_data['nointro_status']

    def get_pclone_status(self):
        return self.entity_data['pclone_status']

    def get_clone(self):
        return self.entity_data['cloneof']
    
    def has_alternative_application(self):
        return 'altapp' in self.entity_data and self.entity_data['altapp']

    def get_alternative_application(self):
        return self.entity_data['altapp']

    def has_alternative_arguments(self):
        return 'altarg' in self.entity_data and self.entity_data['altarg']

    def get_alternative_arguments(self):
        return self.entity_data['altarg']

    def get_filename(self):
        return self.entity_data['filename']

    def get_file(self):
        return self._get_value_as_filename('filename')

    def has_multiple_disks(self):
        return 'disks' in self.entity_data and self.entity_data['disks']

    def get_disks(self):
        if not self.has_multiple_disks():
            return []

        return self.entity_data['disks']

    def get_nfo_file(self):
        ROMFileName = self.get_file()
        nfo_file_path = ROMFileName.switchExtension('.nfo')
        return nfo_file_path

    def get_number_of_players(self):
        return self.entity_data['m_nplayers']

    def get_esrb_rating(self):
        return self.entity_data['m_esrb']

    def get_favourite_status(self):
        return self.entity_data['fav_status']

    def get_launch_count(self):
        return self.entity_data['launch_count']

    def set_file(self, file):
        self.entity_data['filename'] = file.getPath()

    def add_disk(self, disk):
        self.entity_data['disks'].append(disk)

    def set_number_of_players(self, amount):
        self.entity_data['m_nplayers'] = amount

    def set_esrb_rating(self, esrb):
        self.entity_data['m_esrb'] = esrb

    def set_nointro_status(self, status):
        self.entity_data['nointro_status'] = status

    def set_pclone_status(self, status):
        self.entity_data['pclone_status'] = status

    def set_clone(self, clone):
        self.entity_data['cloneof'] = clone

    # todo: definitly something for a inherited FavouriteRom class
    # >> Favourite ROM unique fields
    # >> Favourite ROMs in "Most played ROMs" DB also have 'launch_count' field.
    def set_favourite_status(self, state):
        self.entity_data['fav_status'] = state

    def increase_launch_count(self):
        launch_count = self.entity_data['launch_count'] if 'launch_count' in self.entity_data else 0
        launch_count += 1
        self.entity_data['launch_count'] = launch_count

    def set_alternative_application(self, application):
        self.entity_data['altapp'] = application

    def set_alternative_arguments(self, arg):
        self.entity_data['altarg'] = arg

    def copy(self):
        data = self.copy_of_data()
        return Rom(data)

    def get_edit_options(self, category_id):
        delete_rom_txt = 'Delete ROM'
        if category_id == VCATEGORY_FAVOURITES_ID:
            delete_rom_txt = 'Delete Favourite ROM'
        if category_id == VCATEGORY_COLLECTIONS_ID:
            delete_rom_txt = 'Delete Collection ROM'

        options = collections.OrderedDict()
        options['EDIT_METADATA']    = 'Edit Metadata ...'
        options['EDIT_ASSETS']      = 'Edit Assets/Artwork ...'
        options['ROM_STATUS']       = 'Status: {0}'.format(self.get_state()).encode('utf-8')

        options['ADVANCED_MODS']    = 'Advanced Modifications ...'
        options['DELETE_ROM']       = delete_rom_txt

        if category_id == VCATEGORY_FAVOURITES_ID:
            options['MANAGE_FAV_ROM']   = 'Manage Favourite ROM object ...'
            
        elif category_id == VCATEGORY_COLLECTIONS_ID:
            options['MANAGE_COL_ROM']       = 'Manage Collection ROM object ...'
            options['MANAGE_COL_ROM_POS']   = 'Manage Collection ROM position ...'

        return options

    # >> Metadata edit dialog
    def get_metadata_edit_options(self):
        NFO_FileName = fs_get_ROM_NFO_name(self.get_data())
        NFO_found_str = 'NFO found' if NFO_FileName.exists() else 'NFO not found'
        plot_str = text_limit_string(self.entity_data['m_plot'], PLOT_STR_MAXSIZE)

        rating = self.get_rating()
        if rating == -1:
            rating = 'not rated'

        options = collections.OrderedDict()
        options['EDIT_TITLE']             = u"Edit Title: '{0}'".format(self.get_name()).encode('utf-8')
        options['EDIT_RELEASEYEAR']       = u"Edit Release Year: '{0}'".format(self.get_releaseyear()).encode('utf-8')
        options['EDIT_GENRE']             = u"Edit Genre: '{0}'".format(self.get_genre()).encode('utf-8')
        options['EDIT_DEVELOPER']         = u"Edit Developer: '{0}'".format(self.get_developer()).encode('utf-8')
        options['EDIT_NPLAYERS']          = u"Edit NPlayers: '{0}'".format(self.get_number_of_players()).encode('utf-8')
        options['EDIT_ESRB']              = u"Edit ESRB rating: '{0}'".format(self.get_esrb_rating()).encode('utf-8')
        options['EDIT_RATING']            = u"Edit Rating: '{0}'".format(rating).encode('utf-8')
        options['EDIT_PLOT']              = u"Edit Plot: '{0}'".format(plot_str).encode('utf-8')
        options['LOAD_PLOT']              = "Load Plot from TXT file ..."
        options['IMPORT_NFO_FILE']        = u"Import NFO file (default, {0})".format(NFO_found_str).encode('utf-8')
        options['SAVE_NFO_FILE']          = "Save NFO file (default location)"

        return options

    #
    # Returns a dictionary of options to choose from
    # with which you can do advanced modifications on this specific rom.
    #
    def get_advanced_modification_options(self):
        log_debug('ROM::get_advanced_modification_options() Returning edit options')
        log_debug('ROM::get_advanced_modification_options() Returning edit options')
        options = collections.OrderedDict()
        options['CHANGE_ROM_FILE']          = "Change ROM file: '{0}'".format(self.get_filename())
        options['CHANGE_ALT_APPLICATION']   = "Alternative application: '{0}'".format(self.get_alternative_application())
        options['CHANGE_ALT_ARGUMENTS']     = "Alternative arguments: '{0}'".format(self.get_alternative_arguments())

        return options

    #
    # Reads an NFO file with ROM information.
    # See comments in fs_export_ROM_NFO() about verbosity.
    # About reading files in Unicode http://stackoverflow.com/questions/147741/character-reading-from-file-in-python
    #
    # todo: Replace with nfo_file_path.readXml() and just use XPath
    def update_with_nfo_file(self, nfo_file_path, verbose = True):
        log_debug('Rom.update_with_nfo_file() Loading "{0}"'.format(nfo_file_path.getPath()))
        if not nfo_file_path.exists():
            if verbose:
                kodi_notify_warn('NFO file not found {0}'.format(nfo_file_path.getPath()))
            log_debug("Rom.update_with_nfo_file() NFO file not found '{0}'".format(nfo_file_path.getPath()))
            return False

        # todo: Replace with nfo_file_path.readXml() and just use XPath

        # --- Import data ---
        # >> Read file, put in a string and remove line endings.
        # >> We assume NFO files are UTF-8. Decode data to Unicode.
        # file = open(nfo_file_path, 'rt')
        nfo_str = nfo_file_path.readAllUnicode()
        nfo_str = nfo_str.replace('\r', '').replace('\n', '')

        # Search for metadata tags. Regular expression is non-greedy.
        # See https://docs.python.org/2/library/re.html#re.findall
        # If RE has no groups it returns a list of strings with the matches.
        # If RE has groups then it returns a list of groups.
        item_title     = re.findall('<title>(.*?)</title>', nfo_str)
        item_year      = re.findall('<year>(.*?)</year>', nfo_str)
        item_genre     = re.findall('<genre>(.*?)</genre>', nfo_str)
        item_developer = re.findall('<developer>(.*?)</developer>', nfo_str)
        item_nplayers  = re.findall('<nplayers>(.*?)</nplayers>', nfo_str)
        item_esrb      = re.findall('<esrb>(.*?)</esrb>', nfo_str)
        item_rating    = re.findall('<rating>(.*?)</rating>', nfo_str)
        item_plot      = re.findall('<plot>(.*?)</plot>', nfo_str)

        # >> Future work: ESRB and maybe nplayer fields must be sanitized.
        if len(item_title) > 0:     self.entity_data['m_name']      = text_unescape_XML(item_title[0])
        if len(item_year) > 0:      self.entity_data['m_year']      = text_unescape_XML(item_year[0])
        if len(item_genre) > 0:     self.entity_data['m_genre']     = text_unescape_XML(item_genre[0])
        if len(item_developer) > 0: self.entity_data['m_developer'] = text_unescape_XML(item_developer[0])
        if len(item_nplayers) > 0:  self.entity_data['m_nplayers']  = text_unescape_XML(item_nplayers[0])
        if len(item_esrb) > 0:      self.entity_data['m_esrb']      = text_unescape_XML(item_esrb[0])
        if len(item_rating) > 0:    self.entity_data['m_rating']    = text_unescape_XML(item_rating[0])
        if len(item_plot) > 0:      self.entity_data['m_plot']      = text_unescape_XML(item_plot[0])

        if verbose:
            kodi_notify('Imported {0}'.format(nfo_file_path.getPath()))

        return

    def __str__(self):
        """Overrides the default implementation"""
        return json.dumps(self.entity_data)

# -------------------------------------------------------------------------------------------------
# Abstract base class for launching anything that is supported.
# Implement classes that inherit this base class to support new ways of launching.
# -------------------------------------------------------------------------------------------------
class LauncherABC(MetaDataItemABC):
    __metaclass__ = abc.ABCMeta

    #
    # In an abstract class launcher_data is mandatory.
    #
    def __init__(self, PATHS, settings, launcher_data, objectRepository, executorFactory):
        self.executorFactory = executorFactory
        self.application     = None
        self.arguments       = None
        self.title           = None
        super(LauncherABC, self).__init__(PATHS, settings, launcher_data, objectRepository)

    # --------------------------------------------------------------------------------------------
    # Core methods
    # --------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def get_launcher_type(self): pass

    # By default Launchers do not support ROMs. Redefine in child class if Launcher has ROMs.
    def supports_launching_roms(self): return False

    # By default Launchers do not PClone ROMs. Redefine in child class if necessary.
    def supports_parent_clone_roms(self): return False

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Builds a new Launcher.
    # Leave category_id empty to add launcher to root folder.
    # Returns True if Launcher was sucesfully built.
    # Returns False if Launcher was not built (user canceled the dialogs or some other
    # error happened).
    #
    def build(self, category):
        log_debug('LauncherABC::build() Starting ...')

        # --- Call hook before wizard ---
        if not self._build_pre_wizard_hook(): return False

        # --- Launcher build code (ask user about launcher stuff) ---
        wizard = WizardDialog_Dummy(None, 'categoryID', category.get_id())
        wizard = WizardDialog_Dummy(wizard, 'type', self.get_launcher_type())
        # >> Call Child class wizard builder method
        wizard = self._builder_get_wizard(wizard)
        # >> Run wizard
        self.entity_data = wizard.runWizard(self.entity_data)
        if not self.entity_data: return False
        self.entity_data['timestamp_launcher'] = time.time()

        # --- Call hook after wizard ---
        if not self._build_post_wizard_hook(): return False

        return True

    #
    # Creates a new launcher using a wizard of dialogs.
    # Child concrete classes must implement this method.
    #
    @abc.abstractmethod
    def _builder_get_wizard(self, wizard): pass

    @abc.abstractmethod
    def _build_pre_wizard_hook(self): pass

    @abc.abstractmethod
    def _build_post_wizard_hook(self): pass

    def _builder_get_title_from_app_path(self, input, item_key, launcher):
        if input: return input
        appPath = FileName(launcher['application'])
        title = appPath.getBaseNoExt()
        title_formatted = title.replace('.' + title.split('.')[-1], '').replace('.', ' ')

        return title_formatted

    def _builder_get_appbrowser_filter(self, item_key, launcher):
        if item_key in launcher:
            application = launcher[item_key]
            if application == 'JAVA':
                return '.jar'

        return '.bat|.exe|.cmd|.lnk' if is_windows() else ''

    #
    # Wizard helper, when a user wants to set a custom value instead of the predefined list items.
    #
    def _builder_user_selected_custom_browsing(self, item_key, launcher):
        return launcher[item_key] == 'BROWSE'

    # --------------------------------------------------------------------------------------------
    # Launcher edit methods
    # --------------------------------------------------------------------------------------------
    #
    # Returns a dictionary of options to choose from with which you can edit or manage this
    # specific launcher in the "Edit Launcher" context menu.
    # Different launchers have a different may menu, hence this method is abstract.
    #
    @abc.abstractmethod
    def get_main_edit_options(self):
        pass

    #
    # Returns a dictionary of options to choose from with which you can edit the metadata
    # of a launcher.
    # All launchers have the same metadata so method is defined here.
    #
    def get_metadata_edit_options(self):
        log_debug('LauncherABC::get_metadata_edit_options() Starting ...')
        plot_str = text_limit_string(self.entity_data['m_plot'], PLOT_STR_MAXSIZE)
        rating = self.get_rating() if self.get_rating() != -1 else 'not rated'
        NFO_FileName = fs_get_launcher_NFO_name(self.settings, self.entity_data)
        NFO_found_str = 'NFO found' if NFO_FileName.exists() else 'NFO not found'

        options = collections.OrderedDict()
        options['EDIT_METADATA_TITLE']       = "Edit Title: '{0}'".format(self.get_name())
        options['EDIT_METADATA_PLATFORM']    = "Edit Platform: {0}".format(self.entity_data['platform'])
        options['EDIT_METADATA_RELEASEYEAR'] = "Edit Release Year: '{0}'".format(self.entity_data['m_year'])
        options['EDIT_METADATA_GENRE']       = "Edit Genre: '{0}'".format(self.entity_data['m_genre'])
        options['EDIT_METADATA_DEVELOPER']   = "Edit Developer: '{0}'".format(self.entity_data['m_developer'])
        options['EDIT_METADATA_RATING']      = "Edit Rating: '{0}'".format(rating)
        options['EDIT_METADATA_PLOT']        = "Edit Plot: '{0}'".format(plot_str)
        options['IMPORT_NFO_FILE']           = 'Import NFO file (default {0})'.format(NFO_found_str)
        options['IMPORT_NFO_FILE_BROWSE']    = 'Import NFO file (browse NFO file) ...'
        options['SAVE_NFO_FILE']             = 'Save NFO file (default location)'

        return options

    #
    # get_advanced_modification_options() is custom for every concrete launcher class.
    #
    @abc.abstractmethod
    def get_advanced_modification_options(self): pass

    # ---------------------------------------------------------------------------------------------
    # Execution methods
    # ---------------------------------------------------------------------------------------------
    #
    # Launchs a ROM launcher or standalone launcher
    # For standalone launchers romext is the extension of the application (only used in Windoze)
    #
    @abc.abstractmethod
    def launch(self):
        log_debug('LauncherABC::launch() Starting ...')

        # --- Create executor object ---
        if self.executorFactory is None:
            log_error('LauncherABC::launch() self.executorFactory is None')
            log_error('Cannot create an executor for {0}'.format(self.application.getPath()))
            kodi_notify_error('LauncherABC::launch() self.executorFactory is None'
                              'This is a bug, please report it.')
            return
        executor = self.executorFactory.create(self.application)
        if executor is None:
            log_error('Cannot create an executor for {0}'.format(self.application.getPath()))
            kodi_notify_error('Cannot execute application')
            return

        log_debug('Name        = "{0}"'.format(self.title))
        log_debug('Application = "{0}"'.format(self.application.getPath()))
        log_debug('Arguments   = "{0}"'.format(self.arguments))
        log_debug('Executor    = "{0}"'.format(executor.__class__.__name__))

        # --- Execute app ---
        self._launch_pre_exec(self.title, self.is_in_windowed_mode())
        executor.execute(self.application, self.arguments, self.is_non_blocking())
        self._launch_post_exec(self.is_in_windowed_mode())

    #
    # These two functions do things like stopping music before lunch, toggling full screen, etc.
    # Variables set in this function:
    # self.kodi_was_playing      True if Kodi player was ON, False otherwise
    # self.kodi_audio_suspended  True if Kodi audio suspended before launching
    #
    def _launch_pre_exec(self, title, toggle_screen_flag):
        log_debug('LauncherABC::_launch_pre_exec() Starting ...')

        # --- User notification ---
        if self.settings['display_launcher_notify']:
            kodi_notify('Launching {0}'.format(title))

        # --- Stop/Pause Kodi mediaplayer if requested in settings ---
        self.kodi_was_playing = False
        # id="media_state_action" default="0" values="Stop|Pause|Let Play"
        media_state_action = self.settings['media_state_action']
        media_state_str = ['Stop', 'Pause', 'Let Play'][media_state_action]
        log_verb('_launch_pre_exec() media_state_action is "{0}" ({1})'.format(media_state_str, media_state_action))
        if media_state_action == 0 and xbmc.Player().isPlaying():
            log_verb('_launch_pre_exec() Calling xbmc.Player().stop()')
            xbmc.Player().stop()
            xbmc.sleep(100)
            self.kodi_was_playing = True
        elif media_state_action == 1 and xbmc.Player().isPlaying():
            log_verb('_launch_pre_exec() Calling xbmc.Player().pause()')
            xbmc.Player().pause()
            xbmc.sleep(100)
            self.kodi_was_playing = True

        # --- Force audio suspend if requested in "Settings" --> "Advanced"
        # >> See http://forum.kodi.tv/showthread.php?tid=164522
        self.kodi_audio_suspended = False
        if self.settings['suspend_audio_engine']:
            log_verb('_launch_pre_exec() Suspending Kodi audio engine')
            xbmc.audioSuspend()
            xbmc.enableNavSounds(False)
            xbmc.sleep(100)
            self.kodi_audio_suspended = True
        else:
            log_verb('_launch_pre_exec() DO NOT suspend Kodi audio engine')

        # --- Force joystick suspend if requested in "Settings" --> "Advanced"
        # >> See https://forum.kodi.tv/showthread.php?tid=287826&pid=2627128#pid2627128
        # >> See https://forum.kodi.tv/showthread.php?tid=157499&pid=1722549&highlight=input.enablejoystick#pid1722549
        # >> See https://forum.kodi.tv/showthread.php?tid=313615
        self.kodi_joystick_suspended = False
        # if self.settings['suspend_joystick_engine']:
            # log_verb('_launch_pre_exec() Suspending Kodi joystick engine')
            # >> Research. Get the value of the setting first
            # >> Apparently input.enablejoystick is not supported on Kodi Krypton anymore.
            # c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
            #          ' "method" : "Settings.GetSettingValue",'
            #          ' "params" : {"setting":"input.enablejoystick"}}')
            # response = xbmc.executeJSONRPC(c_str)
            # log_debug('JSON      ''{0}'''.format(c_str))
            # log_debug('Response  ''{0}'''.format(response))

            # c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
            #          ' "method" : "Settings.SetSettingValue",'
            #          ' "params" : {"setting" : "input.enablejoystick", "value" : false} }')
            # response = xbmc.executeJSONRPC(c_str)
            # log_debug('JSON      ''{0}'''.format(c_str))
            # log_debug('Response  ''{0}'''.format(response))
            # self.kodi_joystick_suspended = True

            # log_error('_launch_pre_exec() Suspending Kodi joystick engine not supported on Kodi Krypton!')
        # else:
            # log_verb('_launch_pre_exec() DO NOT suspend Kodi joystick engine')

        # --- Toggle Kodi windowed/fullscreen if requested ---
        if toggle_screen_flag:
            log_verb('_launch_pre_exec() Toggling Kodi fullscreen')
            kodi_toogle_fullscreen()
        else:
            log_verb('_launch_pre_exec() Toggling Kodi fullscreen DEACTIVATED in Launcher')

        # --- Pause Kodi execution some time ---
        delay_tempo_ms = self.settings['delay_tempo']
        log_verb('_launch_pre_exec() Pausing {0} ms'.format(delay_tempo_ms))
        xbmc.sleep(delay_tempo_ms)
        log_debug('LauncherABC::_launch_pre_exec() function ENDS')

    def _launch_post_exec(self, toggle_screen_flag):
        log_debug('LauncherABC::_launch_post_exec() Starting ...')

        # --- Stop Kodi some time ---
        delay_tempo_ms = self.settings['delay_tempo']
        log_verb('_launch_post_exec() Pausing {0} ms'.format(delay_tempo_ms))
        xbmc.sleep(delay_tempo_ms)

        # --- Toggle Kodi windowed/fullscreen if requested ---
        if toggle_screen_flag:
            log_verb('_launch_post_exec() Toggling Kodi fullscreen')
            kodi_toogle_fullscreen()
        else:
            log_verb('_launch_post_exec() Toggling Kodi fullscreen DEACTIVATED in Launcher')

        # --- Resume audio engine if it was suspended ---
        # Calling xmbc.audioResume() takes a loong time (2/4 secs) if audio was not properly suspended!
        # Also produces this in Kodi's log:
        # WARNING: CActiveAE::StateMachine - signal: 0 from port: OutputControlPort not handled for state: 7
        #   ERROR: ActiveAE::Resume - failed to init
        if self.kodi_audio_suspended:
            log_verb('_launch_post_exec() Kodi audio engine was suspended before launching')
            log_verb('_launch_post_exec() Resuming Kodi audio engine')
            xbmc.audioResume()
            xbmc.enableNavSounds(True)
            xbmc.sleep(100)
        else:
            log_verb('_launch_post_exec() DO NOT resume Kodi audio engine')

        # --- Resume joystick engine if it was suspended ---
        if self.kodi_joystick_suspended:
            log_verb('_launch_post_exec() Kodi joystick engine was suspended before launching')
            log_verb('_launch_post_exec() Resuming Kodi joystick engine')
            # response = xbmc.executeJSONRPC(c_str)
            # log_debug('JSON      ''{0}'''.format(c_str))
            # log_debug('Response  ''{0}'''.format(response))
            log_verb('_launch_post_exec() Not supported on Kodi Krypton!')
        else:
            log_verb('_launch_post_exec() DO NOT resume Kodi joystick engine')

        # --- Resume Kodi playing if it was paused. If it was stopped, keep it stopped. ---
        media_state_action = self.settings['media_state_action']
        media_state_str = ['Stop', 'Pause', 'Let Play'][media_state_action]
        log_verb('_launch_post_exec() media_state_action is "{0}" ({1})'.format(media_state_str, media_state_action))
        log_verb('_launch_post_exec() self.kodi_was_playing is {0}'.format(self.kodi_was_playing))
        if self.kodi_was_playing and media_state_action == 1:
            log_verb('_launch_post_exec() Calling xbmc.Player().play()')
            xbmc.Player().play()
        log_debug('LauncherABC::_launch_post_exec() function ENDS')

    # ---------------------------------------------------------------------------------------------
    # Launcher metadata and flags related methods
    # ---------------------------------------------------------------------------------------------
    def get_platform(self): return self.entity_data['platform']

    def set_platform(self, platform): self.entity_data['platform'] = platform

    def get_category_id(self): return self.entity_data['categoryID']

    def update_category(self, category_id): self.entity_data['categoryID'] = category_id

    def is_in_windowed_mode(self): return self.entity_data['toggle_window']

    def set_windowed_mode(self, windowed_mode):
        self.entity_data['toggle_window'] = windowed_mode
        return self.is_in_windowed_mode()

    def is_non_blocking(self):
        return 'non_blocking' in self.entity_data and self.entity_data['non_blocking']

    def set_non_blocking(self, is_non_blocking):
        self.entity_data['non_blocking'] = is_non_blocking
        return self.is_non_blocking()

    # Change the application this launcher uses. Override if application is changeable.
    def change_application(self): return False

    def get_timestamp(self):
        timestamp = self.entity_data['timestamp_launcher']
        if timestamp is None or timestamp == '':
            return float(0)

        return float(timestamp)

    def update_timestamp(self): self.entity_data['timestamp_launcher'] = time.time()

    def get_report_timestamp(self):
        timestamp = self.entity_data['timestamp_report']
        if timestamp is None or timestamp == '':
            return float(0)

        return float(timestamp)

    def update_report_timestamp(self): self.entity_data['timestamp_report'] = time.time()

    # ---------------------------------------------------------------------------------------------
    # Launcher asset methods
    # ---------------------------------------------------------------------------------------------
    #
    # Returns an ordered dictionary with all the object assets, ready to be edited.
    # Keys are AssetInfo objects.
    # Values are the current file for the asset as Unicode string or '' if the asset is not set.
    #
    def get_assets_odict(self):
        asset_info_list = g_assetFactory.get_asset_list_by_IDs(LAUNCHER_ASSET_ID_LIST)
        asset_odict = collections.OrderedDict()
        for asset_info in asset_info_list:
            asset_fname_str = self.entity_data[asset_info.key] if self.entity_data[asset_info.key] else ''
            asset_odict[asset_info] = asset_fname_str

        return asset_odict

    #
    # Get a list of the assets that can be mapped to a defaultable asset.
    # They must be images, no videos, no documents.
    # The defaultable assets are always the same: icon, fanart, banner, poster, clearlogo.
    #
    def get_mappable_asset_list(self):
        return g_assetFactory.get_asset_list_by_IDs(MAPPABLE_LAUNCHER_ASSET_ID_LIST)

    #
    # Gets the database filename mapped for asset_info.
    # Note that the mapped asset uses diferent fields wheter it is a Category/Launcher/ROM
    #
    def get_mapped_asset_key(self, asset_info):
        return self.entity_data[asset_info.default_key]

    def set_mapped_asset_key(self, asset_info, mapped_to_info):
        self.entity_data[asset_info.default_key] = mapped_to_info.key

    # ---------------------------------------------------------------------------------------------
    # NFO files for metadata
    # ---------------------------------------------------------------------------------------------
    #
    # Python data model: lists and dictionaries are mutable. It means the can be changed if passed as
    # parameters of functions. However, items can not be replaced by new objects!
    # Notably, numbers, strings and tuples are immutable. Dictionaries and lists are mutable.
    #
    # See http://stackoverflow.com/questions/986006/how-do-i-pass-a-variable-by-reference
    # See https://docs.python.org/2/reference/datamodel.html
    #
    # Function asumes that the NFO file already exists.
    #
    def import_nfo_file(self, nfo_file_path):
        # --- Get NFO file name ---
        log_debug('launcher.import_nfo_file() Importing launcher NFO "{0}"'.format(nfo_file_path.getPath()))

        # --- Import data ---
        if nfo_file_path.exists():
            # >> Read NFO file data
            try:
                item_nfo = nfo_file_path.readAllUnicode()
                item_nfo = item_nfo.replace('\r', '').replace('\n', '')
            except:
                kodi_notify_warn('Exception reading NFO file {0}'.format(nfo_file_path.getPath()))
                log_error("launcher.import_nfo_file() Exception reading NFO file '{0}'".format(nfo_file_path.getPath()))
                return False
            # log_debug("fs_import_launcher_NFO() item_nfo '{0}'".format(item_nfo))
        else:
            kodi_notify_warn('NFO file not found {0}'.format(nfo_file_path.getBase()))
            log_info("launcher.import_nfo_file() NFO file not found '{0}'".format(nfo_file_path.getPath()))
            return False

        # Find data
        item_year      = re.findall('<year>(.*?)</year>',           item_nfo)
        item_genre     = re.findall('<genre>(.*?)</genre>',         item_nfo)
        item_developer = re.findall('<developer>(.*?)</developer>', item_nfo)
        item_rating    = re.findall('<rating>(.*?)</rating>',       item_nfo)
        item_plot      = re.findall('<plot>(.*?)</plot>',           item_nfo)

        # >> Careful about object mutability! This should modify the dictionary
        # >> passed as argument outside this function.
        if item_year:      self.update_releaseyear(text_unescape_XML(item_year[0]))
        if item_genre:     self.update_genre(text_unescape_XML(item_genre[0]))
        if item_developer: self.update_developer(text_unescape_XML(item_developer[0]))
        if item_rating:    self.update_rating(text_unescape_XML(item_rating[0]))
        if item_plot:      self.update_plot(text_unescape_XML(item_plot[0]))

        log_verb("import_nfo_file() Imported '{0}'".format(nfo_file_path.getPath()))

        return True

    #
    # Standalone launchers:
    #   NFO files are stored in self.settings["launchers_nfo_dir"] if not empty.
    #   If empty, it defaults to DEFAULT_LAUN_NFO_DIR.
    #
    # ROM launchers:
    #   Same as standalone launchers.
    #
    def export_nfo_file(self, nfo_FileName):
        # --- Get NFO file name ---
        log_debug('export_nfo_file() Exporting launcher NFO "{0}"'.format(nfo_FileName.getPath()))

        # If NFO file does not exist then create them. If it exists, overwrite.
        nfo_content = []
        nfo_content.append('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')
        nfo_content.append('<!-- Exported by AEL on {0} -->\n'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
        nfo_content.append('<launcher>\n')
        nfo_content.append(XML_text('year',      self.get_releaseyear()))
        nfo_content.append(XML_text('genre',     self.get_genre()))
        nfo_content.append(XML_text('developer', self.get_developer()))
        nfo_content.append(XML_text('rating',    self.get_rating()))
        nfo_content.append(XML_text('plot',      self.get_plot()))
        nfo_content.append('</launcher>\n')
        full_string = ''.join(nfo_content).encode('utf-8')
        try:
            nfo_FileName.writeAll(full_string)
        except:
            kodi_notify_warn('Exception writing NFO file {0}'.format(nfo_FileName.getPath()))
            log_error("export_nfo_file() Exception writing'{0}'".format(nfo_FileName.getPath()))
            return False
        log_debug("export_nfo_file() Created '{0}'".format(nfo_FileName.getPath()))

        return True

    def export_configuration(self, path_to_export, category):
        launcher_fn_str = 'Launcher_' + text_title_to_filename_str(self.get_name()) + '.xml'
        log_debug('launcher.export_configuration() Exporting Launcher configuration')
        log_debug('launcher.export_configuration() Name     "{0}"'.format(self.get_name()))
        log_debug('launcher.export_configuration() ID       {0}'.format(self.get_id()))
        log_debug('launcher.export_configuration() l_fn_str "{0}"'.format(launcher_fn_str))

        if not path_to_export: return

        export_FN = FileName(path_to_export, isdir = True).pjoin(launcher_fn_str)
        if export_FN.exists():
            confirm = kodi_dialog_yesno('Overwrite file {0}?'.format(export_FN.getPath()))
            if not confirm:
                kodi_notify_warn('Export of Launcher XML cancelled')
        
        category_data = category.get_data() if category is not None else {}

        # --- Print error message is something goes wrong writing file ---
        try:
            autoconfig_export_launcher(self.entity_data, export_FN, category_data)
        except AEL_Error as E:
            kodi_notify_warn('{0}'.format(E))
        else:
            kodi_notify('Exported Launcher "{0}" XML config'.format(self.get_name()))
        # >> No need to update categories.xml and timestamps so return now.

    # ---------------------------------------------------------------------------------------------
    # Misc functions
    # ---------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
# Standalone application launcher
# -------------------------------------------------------------------------------------------------
class StandaloneLauncher(LauncherABC):
    def __init__(self, PATHS, settings, launcher_dic, objectRepository, executorFactory):
        # --- Create default Standalone Launcher if empty launcher_dic---
        # Concrete classes are responsible of creating a default entity_data dictionary
        # with sensible defaults.
        if launcher_dic is None:
            launcher_dic = fs_new_launcher()
            launcher_dic['id'] = misc_generate_random_SID()
            launcher_dic['type'] = OBJ_LAUNCHER_STANDALONE
        super(StandaloneLauncher, self).__init__(PATHS, settings, launcher_dic, objectRepository, executorFactory)

    # --------------------------------------------------------------------------------------------
    # Core methods
    # --------------------------------------------------------------------------------------------
    def get_object_name(self): return 'Standalone launcher'

    def get_assets_kind(self): return KIND_ASSET_LAUNCHER

    def get_launcher_type(self): return OBJ_LAUNCHER_STANDALONE

    def save_to_disk(self): self.objectRepository.save_launcher(self.entity_data)

    # Object becomes invalid after deletion
    def delete_from_disk(self):
        self.objectRepository.delete_launcher(self.entity_data)
        self.entity_data = None
        self.objectRepository = None

    def supports_launching_roms(self): return False

    def supports_parent_clone_roms(self): return False

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Returns True if Launcher was sucesfully built.
    # Returns False if Launcher was not built (user canceled the dialogs or some other
    #
    def build(self, launcher): return super(StandaloneLauncher, self).build(launcher)

    #
    # Creates a new launcher using a wizard of dialogs.
    # _builder_get_wizard() is always defined in Launcher concrete classes and it's called by
    # parent build() method.
    #
    def _builder_get_wizard(self, wizard):
        wizard = WizardDialog_FileBrowse(wizard, 'application', 'Select the launcher application',
            1, self._builder_get_appbrowser_filter)
        wizard = WizardDialog_Dummy(wizard, 'args', '')
        wizard = WizardDialog_Keyboard(wizard, 'args', 'Application arguments')
        wizard = WizardDialog_Dummy(wizard, 'm_name', '',
            self._builder_get_title_from_app_path)
        wizard = WizardDialog_Keyboard(wizard, 'm_name','Set the title of the launcher',
            self._builder_get_title_from_app_path)
        wizard = WizardDialog_Selection(wizard, 'platform', 'Select the platform',
            AEL_platform_list)

        return wizard

    def _build_pre_wizard_hook(self): return True

    def _build_post_wizard_hook(self): return True

    # --------------------------------------------------------------------------------------------
    # Launcher edit methods
    # --------------------------------------------------------------------------------------------
    def get_main_edit_options(self, category):
        log_debug('StandaloneLauncher::get_main_edit_options() Starting ...')

        options = collections.OrderedDict()
        options['EDIT_METADATA']          = 'Edit Metadata ...'
        options['EDIT_ASSETS']            = 'Edit Assets/Artwork ...'
        options['EDIT_DEFAULT_ASSETS']    = 'Choose default Assets/Artwork ...'
        options['EDIT_LAUNCHER_CATEGORY'] = "Change Category: '{0}'".format(category.get_name())
        options['EDIT_LAUNCHER_STATUS']   = 'Launcher status: {0}'.format(self.get_finished_str())
        options['LAUNCHER_ADVANCED_MODS'] = 'Advanced Modifications ...'
        options['EXPORT_LAUNCHER']        = 'Export Launcher XML configuration ...'
        options['DELETE_LAUNCHER']        = 'Delete Launcher'

        return options

    def get_advanced_modification_options(self):
        log_debug('StandaloneLauncher::get_advanced_modification_options() Starting ...')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'

        options = collections.OrderedDict()
        options['CHANGE_APPLICATION']   = "Change Application: '{0}'".format(self.entity_data['application'])
        options['MODIFY_ARGS']          = "Modify Arguments: '{0}'".format(self.entity_data['args'])
        options['ADDITIONAL_ARGS']      = "Modify aditional arguments ..."
        options['TOGGLE_WINDOWED']      = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['TOGGLE_NONBLOCKING']   = "Non-blocking launcher (now {0})".format(non_blocking_str)

        return options

    # ---------------------------------------------------------------------------------------------
    # Execution methods
    # ---------------------------------------------------------------------------------------------
    def launch(self):
        log_debug('StandaloneLauncher::launch() Starting ...')
        self.title       = self.entity_data['m_name']
        self.application = FileName(self.entity_data['application'])
        self.arguments   = self.entity_data['args']

        # --- Check for errors and abort if errors found ---
        if not self.application.exists():
            log_error('Launching app not found "{0}"'.format(self.application.getPath()))
            kodi_notify_warn('App {0} not found.'.format(self.application.getPath()))
            return

        # --- Argument substitution ---
        log_info('Raw arguments   "{0}"'.format(self.arguments))
        self.arguments = self.arguments.replace('$apppath$' , self.application.getDir())
        log_info('Final arguments "{0}"'.format(self.arguments))

        # --- Call LauncherABC.launch(). Executor object is created there and invoked ---
        super(StandaloneLauncher, self).launch()
        log_debug('StandaloneLauncher::launch() END ...')

    # ---------------------------------------------------------------------------------------------
    # Launcher metadata and flags related methods
    # ---------------------------------------------------------------------------------------------
    def change_application(self):
        current_application = self.entity_data['application']
        selected_application = xbmcgui.Dialog().browse(1, 'Select the launcher application', 'files',
                                                      self._get_appbrowser_filter('application', self.entity_data),
                                                      False, False, current_application).decode('utf-8')

        if selected_application is None or selected_application == current_application:
            return False

        self.entity_data['application'] = selected_application

    def set_args(self, args): self.entity_data['args'] = args

    def get_args(self): return self.entity_data['args']

    def get_additional_argument(self, index):
        args = self.get_all_additional_arguments()
        return args[index]

    def get_all_additional_arguments(self):
        return self.entity_data['args_extra']

    def add_additional_argument(self, arg):
        if not self.entity_data['args_extra']:
            self.entity_data['args_extra'] = []

        self.entity_data['args_extra'].append(arg)
        log_debug('launcher.add_additional_argument() Appending extra_args to launcher {0}'.format(self.get_id()))

    def set_additional_argument(self, index, arg):
        if not self.entity_data['args_extra']:
            self.entity_data['args_extra'] = []
        self.entity_data['args_extra'][index] = arg
        log_debug('launcher.set_additional_argument() Edited args_extra[{0}] to "{1}"'.format(index, self.entity_data['args_extra'][index]))

    def remove_additional_argument(self, index):
        del self.entity_data['args_extra'][index]
        log_debug("launcher.remove_additional_argument() Deleted launcher['args_extra'][{0}]".format(index))

# -------------------------------------------------------------------------------------------------
# Abstract base class for launching anything ROMs or item based.
# This class support Parent/Clone generation, multidisc support, and ROM No-Intro/REDUMP audit.
# Inherit from this base class to implement your own specific ROM launcher.
# -------------------------------------------------------------------------------------------------
class ROMLauncherABC(LauncherABC):
    __metaclass__ = abc.ABCMeta

    # launcher_data is always valid, concrete classes fill it with defaults.
    def __init__(self, PATHS, settings, launcher_data, objectRepository,
                 executorFactory, romsetRepository, statsStrategy):
        self.roms = {}
        self.romsetRepository = romsetRepository
        self.statsStrategy = statsStrategy
        super(ROMLauncherABC, self).__init__(PATHS, settings, launcher_data, objectRepository, executorFactory)

    # --------------------------------------------------------------------------------------------
    # Core functions
    # --------------------------------------------------------------------------------------------
    # By default ROM Launchers supports Launching ROMs (of course), PClone ROMs and ROM Audit.
    # Override this methods if necessary in child classes.
    def supports_launching_roms(self): return True

    def supports_parent_clone_roms(self): return True

    def supports_parent_clone_roms(self): return False

    def supports_ROM_audit(self): return True

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # In ROM launchers create the ROM asset paths. Child classes must call this method or
    # problems will happen.
    #
    @abc.abstractmethod
    def _build_post_wizard_hook(self):
        log_debug('ROMLauncherABC::_build_pre_wizard_hook() Starting ...')

        # Choose launcher ROM XML filename. There may be launchers with same name in different
        # categories, or even launcher with the same name in the same category.
        roms_base_noext = fs_get_ROMs_basename(self.get_name(), self.entity_data['m_name'], self.get_id())
        self.entity_data['roms_base_noext'] = roms_base_noext

        # --- Selected asset path ---
        # A) User chooses one and only one assets path
        # B) If this path is different from the ROM path then asset naming scheme 1 is used.
        # B) If this path is the same as the ROM path then asset naming scheme 2 is used.
        # >> Create asset directories. Function detects if we are using naming scheme 1 or 2.
        # >> launcher is edited using Python passing by assignment.
        self.rom_assets_init_dirs()

        return True

    def _builder_get_extensions_from_app_path(self, input, item_key ,launcher):
        if input: return input

        app = launcher['application']
        appPath = FileName(app)

        extensions = emudata_get_program_extensions(appPath.getBase())
        return extensions

    def _builder_get_arguments_from_application_path(self, input, item_key, launcher):
        if input: return input
        app = launcher['application']
        appPath = FileName(app)
        default_arguments = emudata_get_program_arguments(appPath.getBase())

        return default_arguments

    def _builder_get_value_from_rompath(self, input, item_key, launcher):
        if input: return input
        romPath = launcher['rompath']

        return romPath

    def _builder_get_value_from_assetpath(self, input, item_key, launcher):
        if input: return input
        romPath = FileName(launcher['assets_path'])
        romPath = romPath.pjoin('games')

        return romPath.getPath()

    # --------------------------------------------------------------------------------------------
    # Launcher edit methods
    # --------------------------------------------------------------------------------------------
    @abc.abstractmethod
    def get_main_edit_options(self): pass

    # get_metadata_edit_options() has a general implementation in LauncherABC class for 
    # all launchers.

    #
    # get_advanced_modification_options() is custom for every concrete launcher class.
    #
    @abc.abstractmethod
    def get_advanced_modification_options(self): pass

    # Returns the dialog options to choose from when managing the roms.
    def get_manage_roms_options(self):
        log_debug('ROMLauncherABC::get_manage_roms_options() Returning options')

        options = collections.OrderedDict()
        options['SET_ROMS_DEFAULT_ARTWORK'] = 'Choose ROMs default artwork ...'
        options['SET_ROMS_ASSET_DIRS']      = 'Manage ROMs asset directories ...'
        options['SCAN_LOCAL_ARTWORK']       = 'Scan ROMs local artwork'
        options['SCRAPE_LOCAL_ARTWORK']     = 'Scrape ROMs local artwork'
        options['REMOVE_DEAD_ROMS']         = 'Remove dead/missing ROMs'
        options['IMPORT_ROMS']              = 'Import ROMs metadata from NFO files'
        options['EXPORT_ROMS']              = 'Export ROMs metadata to NFO files'
        options['DELETE_ROMS_NFO']          = 'Delete ROMs NFO files'
        options['CLEAR_ROMS']               = 'Clear ROMs from launcher'

        return options

    def get_audit_roms_options(self):
        log_debug('ROMLauncherABC::get_audit_roms_options() Returning edit options')
        display_mode_str       = self.entity_data['launcher_display_mode']
        no_intro_display_mode  = self.entity_data['nointro_display_mode']

        options = collections.OrderedDict()
        options['CHANGE_DISPLAY_MODE']    = 'Change launcher display mode (now {0}) ...'.format(display_mode_str)
        options['CREATE_PARENTCLONE_DAT'] = 'Create Parent/Clone DAT based on ROM filenames'
        options['CHANGE_DISPLAY_ROMS']    = 'Display ROMs (now {0}) ...'.format(no_intro_display_mode)
        options['ADD_NO_INTRO']           = "Add No-Intro/Redump DAT: '{0}'".format(nointro_xml_file)
        options['DELETE_NO_INTRO']        = 'Delete No-Intro/Redump DAT'
        options['UPDATE_ROM_AUDIT']       = 'Update ROM audit'

        return options

    # ---------------------------------------------------------------------------------------------
    # Execution methods
    # ---------------------------------------------------------------------------------------------
    def launch(self):
        self.title = self.rom.get_name()
        self.selected_rom_file = None

        applicationIsSet = self._launch_selectApplicationToUse()
        argumentsAreSet  = self._launch_selectArgumentsToUse()
        romIsSelected    = self._launch_selectRomFileToUse()

        if not applicationIsSet or not argumentsAreSet or not romIsSelected:
            return

        self._parseArguments()

        if self.statsStrategy is not None:
            self.statsStrategy.update_launched_rom_stats(self.rom)
            self.save_rom(self.rom)

        super(RomLauncherABC, self).launch()

    @abc.abstractmethod
    def _launch_selectApplicationToUse(self): return True

    @abc.abstractmethod
    def _launch_selectArgumentsToUse(self): return True

    @abc.abstractmethod
    def _launch_selectRomFileToUse(self): return True

    # --- Argument substitution ---
    def _launch_parseArguments(self):
        log_info('RomLauncher() raw arguments   "{0}"'.format(self.arguments))

        # Application based arguments replacements
        if self.application and isinstance(self.application, FileName):
            apppath = self.application.getDir()

            log_info('RomLauncher() application  "{0}"'.format(self.application.getPath()))
            log_info('RomLauncher() appbase      "{0}"'.format(self.application.getBase()))
            log_info('RomLauncher() apppath      "{0}"'.format(apppath))

            self.arguments = self.arguments.replace('$apppath$', apppath)
            self.arguments = self.arguments.replace('$appbase$', self.application.getBase())

        # ROM based arguments replacements
        if self.selected_rom_file:
            # --- Escape quotes and double quotes in ROMFileName ---
            # >> This maybe useful to Android users with complex command line arguments
            if self.escape_romfile:
                log_info("RomLauncher() Escaping ROMFileName ' and \"")
                self.selected_rom_file.escapeQuotes()

            rompath       = self.selected_rom_file.getDir()
            rombase       = self.selected_rom_file.getBase()
            rombase_noext = self.selected_rom_file.getBase_noext()

            log_info('RomLauncher() romfile      "{0}"'.format(self.selected_rom_file.getPath()))
            log_info('RomLauncher() rompath      "{0}"'.format(rompath))
            log_info('RomLauncher() rombase      "{0}"'.format(rombase))
            log_info('RomLauncher() rombasenoext "{0}"'.format(rombase_noext))

            self.arguments = self.arguments.replace('$rom$', self.selected_rom_file.getPath())
            self.arguments = self.arguments.replace('$romfile$', self.selected_rom_file.getPath())
            self.arguments = self.arguments.replace('$rompath$', rompath)
            self.arguments = self.arguments.replace('$rombase$', rombase)
            self.arguments = self.arguments.replace('$rombasenoext$', rombase_noext)

            # >> Legacy names for argument substitution
            self.arguments = self.arguments.replace('%rom%', self.selected_rom_file.getPath())
            self.arguments = self.arguments.replace('%ROM%', self.selected_rom_file.getPath())

        category_id = self.get_category_id()
        if category_id is None:
            category_id = ''

        # Default arguments replacements
        self.arguments = self.arguments.replace('$categoryID$', category_id)
        self.arguments = self.arguments.replace('$launcherID$', self.entity_data['id'])
        self.arguments = self.arguments.replace('$romID$', self.rom.get_id())
        self.arguments = self.arguments.replace('$romtitle$', self.title)

        # automatic substitution of rom values
        for rom_key, rom_value in self.rom.get_data().iteritems():
            if isinstance(rom_value, basestring):
                self.arguments = self.arguments.replace('${}$'.format(rom_key), rom_value)        

        # automatic substitution of launcher values
        for launcher_key, launcher_value in self.entity_data.iteritems():
            if isinstance(launcher_value, basestring):
                self.arguments = self.arguments.replace('${}$'.format(launcher_key), launcher_value)

        log_info('RomLauncher() final arguments "{0}"'.format(self.arguments))

    # ---------------------------------------------------------------------------------------------
    # ROM methods
    # ---------------------------------------------------------------------------------------------


    # ---------------------------------------------------------------------------------------------
    # ROM asset methods
    # ---------------------------------------------------------------------------------------------
    #
    # Creates path for assets (artwork) and automatically fills in the path_ fields in the
    # launcher dictionary.
    #
    def rom_assets_init_dirs(self):
        assets_dir_FN = FileName(self.entity_data['assets_path'], isdir = True)
        log_verb('ROMLauncherABC::rom_assets_init_dirs() assets_dir_FN "{0}"'.format(assets_dir_FN.getPath()))

        # --- Fill in launcher fields and create asset directories ---
        if self.entity_data['platform'] == 'MAME':
            log_verb('ROMLauncherABC::rom_assets_init_dirs() Creating MAME asset paths')
            self.rom_assets_create_dir(assets_dir_FN, 'path_title', 'titles')
            self.rom_assets_create_dir(assets_dir_FN, 'path_snap', 'snaps')
            self.rom_assets_create_dir(assets_dir_FN, 'path_boxfront', 'cabinets')
            self.rom_assets_create_dir(assets_dir_FN, 'path_boxback', 'cpanels')
            self.rom_assets_create_dir(assets_dir_FN, 'path_cartridge', 'PCBs')
            self.rom_assets_create_dir(assets_dir_FN, 'path_fanart', 'fanarts')
            self.rom_assets_create_dir(assets_dir_FN, 'path_banner', 'marquees')
            self.rom_assets_create_dir(assets_dir_FN, 'path_clearlogo', 'clearlogos')
            self.rom_assets_create_dir(assets_dir_FN, 'path_flyer', 'flyers')
            self.rom_assets_create_dir(assets_dir_FN, 'path_map', 'maps')
            self.rom_assets_create_dir(assets_dir_FN, 'path_manual', 'manuals')
            self.rom_assets_create_dir(assets_dir_FN, 'path_trailer', 'trailers')
        else:
            log_verb('ROMLauncherABC::rom_assets_init_dirs() Creating Standard asset paths')
            self.rom_assets_create_dir(assets_dir_FN, 'path_title', 'titles')
            self.rom_assets_create_dir(assets_dir_FN, 'path_snap', 'snaps')
            self.rom_assets_create_dir(assets_dir_FN, 'path_boxfront', 'boxfronts')
            self.rom_assets_create_dir(assets_dir_FN, 'path_boxback', 'boxbacks')
            self.rom_assets_create_dir(assets_dir_FN, 'path_cartridge', 'cartridges')
            self.rom_assets_create_dir(assets_dir_FN, 'path_fanart', 'fanarts')
            self.rom_assets_create_dir(assets_dir_FN, 'path_banner', 'banners')
            self.rom_assets_create_dir(assets_dir_FN, 'path_clearlogo', 'clearlogos')
            self.rom_assets_create_dir(assets_dir_FN, 'path_flyer', 'flyers')
            self.rom_assets_create_dir(assets_dir_FN, 'path_map', 'maps')
            self.rom_assets_create_dir(assets_dir_FN, 'path_manual', 'manuals')
            self.rom_assets_create_dir(assets_dir_FN, 'path_trailer', 'trailers')

    #
    # Create asset path and assign it to Launcher dictionary.
    #
    def rom_assets_create_dir(self, assets_dir_FN, key, path_name):
        asset_dir_FN = assets_dir_FN.pjoin(path_name, isdir = True)
        self.entity_data[key] = asset_dir_FN.getPath()
        log_debug('ROMLauncherABC::rom_assets_create_dir() Creating "{0}"'.format(asset_dir_FN.getPath()))
        asset_dir_FN.makedirs()

    def get_ROM_assets(self):
        assets = {}
        assets[ASSET_BANNER]     = self.entity_data['s_banner']      if self.entity_data['s_banner']     else ''
        assets[ASSET_ICON]       = self.entity_data['s_icon']        if self.entity_data['s_icon']       else ''
        assets[ASSET_FANART]     = self.entity_data['s_fanart']      if self.entity_data['s_fanart']     else ''
        assets[ASSET_POSTER]     = self.entity_data['s_poster']      if self.entity_data['s_poster']     else ''
        assets[ASSET_CLEARLOGO]  = self.entity_data['s_clearlogo']   if self.entity_data['s_clearlogo']  else ''
        assets[ASSET_CONTROLLER] = self.entity_data['s_controller']  if self.entity_data['s_controller'] else ''
        assets[ASSET_TRAILER]    = self.entity_data['s_trailer']     if self.entity_data['s_trailer']    else ''

        return assets

    def get_ROM_asset_default(self, asset_info):
        return self.entity_data[asset_info.rom_default_key] if asset_info.rom_default_key in self.entity_data else None

    def get_ROM_asset_defaults(self):
        default_assets = {}
        default_assets[ASSET_BANNER]     = ASSET_KEYS_TO_CONSTANTS[self.entity_data['roms_default_banner']]    if self.entity_data['roms_default_banner']     else ''
        default_assets[ASSET_ICON]       = ASSET_KEYS_TO_CONSTANTS[self.entity_data['roms_default_icon']]      if self.entity_data['roms_default_icon']       else ''
        default_assets[ASSET_FANART]     = ASSET_KEYS_TO_CONSTANTS[self.entity_data['roms_default_fanart']]    if self.entity_data['roms_default_fanart']     else ''
        default_assets[ASSET_POSTER]     = ASSET_KEYS_TO_CONSTANTS[self.entity_data['roms_default_poster']]    if self.entity_data['roms_default_poster']     else ''
        default_assets[ASSET_CLEARLOGO]  = ASSET_KEYS_TO_CONSTANTS[self.entity_data['roms_default_clearlogo']] if self.entity_data['roms_default_clearlogo']  else ''

        return default_assets

    # ---------------------------------------------------------------------------------------------
    # Utility functions of ROM Launchers
    # Use the same function names as in ObjectRepository class.
    # ---------------------------------------------------------------------------------------------
    def load_ROMs(self): self.roms = self.romsetRepository.load_ROMs(self)

    def save_current_ROMs(self):
        self.romset_repository.save_rom_set(self, self.roms)

    def save_ROM(self, rom):
        if not self.has_roms(): self.load_roms()
        self.roms[rom.get_id()] = rom
        self.romset_repository.save_rom_set(self, self.roms)

    def update_ROM_set(self, roms):
        if not isinstance(roms, dict):
            roms = dict((rom.get_id(), rom) for rom in roms)
        self.romset_repository.save_rom_set(self, roms)
        self.roms = roms

    def delete_ROM_databases(self):
        self.romset_repository.delete_all_by_launcher(self)

    def delete_ROM(self, rom_id):
        if not self.has_roms(): self.load_roms()
        self.roms.pop(rom_id)
        self.romset_repository.save_rom_set(self, self.roms)

    def select_ROM(self, rom_id):
        if not self.has_roms(): self.load_roms()
        if self.roms is None:
            log_error('Unable to load romset')
            return None

        if not rom_id in self.roms:
            log_error('RomID {0} not found in romset'.format(rom_id))
            return None
        self.rom = self.roms[rom_id]

        return self.rom

    def has_ROMs(self):
        return self.roms is not None and len(self.roms) > 0

    def has_ROM(self, rom_id):
        if not self.has_roms(): self.load_roms()

        return rom_id in self.roms

    def get_number_of_ROMs(self):
        return self.entity_data['num_roms']

    def actual_amount_of_ROMs(self):
        if not self.has_roms(): self.load_roms()

        return len(self.roms)

    def get_roms(self):
        if not self.has_roms(): self.load_roms()

        return self.roms.values() if self.roms else None

    def get_ROM_IDs(self):
        if not self.has_roms(): self.load_roms()

        return self.roms.keys() if self.roms else None

    def reset_PClone_ROMs(self):
        self.romset_repository.delete_by_launcher(self, ROMSET_CPARENT)
        self.romset_repository.delete_by_launcher(self, ROMSET_PCLONE)
        self.romset_repository.delete_by_launcher(self, ROMSET_PARENTS)

    # -------------------------------------------------------------------------------------------------
    # Favourite ROM creation/management
    # -------------------------------------------------------------------------------------------------
    #
    # Creates a new Favourite ROM dictionary from parent ROM and Launcher.
    #
    # No-Intro Missing ROMs are not allowed in Favourites or Virtual Launchers.
    # fav_status = ['OK', 'Unlinked ROM', 'Unlinked Launcher', 'Broken'] default 'OK'
    #  'OK'                ROM filename exists and launcher exists and ROM id exists
    #  'Unlinked ROM'      ROM filename exists but ROM ID in launcher does not
    #  'Unlinked Launcher' ROM filename exists but Launcher ID not found
    #                      Note that if the launcher does not exists implies ROM ID does not exist.
    #                      If launcher doesn't exist ROM JSON cannot be loaded.
    #  'Broken'            ROM filename does not exist. ROM is unplayable
    #
    def convert_rom_to_favourite(self, rom_id):
        rom = self.select_rom(rom_id)
        # >> Copy original rom     
        # todo: Should we make a FavouriteRom class inheriting Rom?
        favourite = rom.copy()

        # Delete nointro_status field from ROM. Make sure this is done in the copy to be
        # returned to avoid chaning the function parameters (dictionaries are mutable!)
        # See http://stackoverflow.com/questions/5844672/delete-an-element-from-a-dictionary
        # NOTE keep it!
        # del favourite['nointro_status']

        # >> Copy parent launcher fields into Favourite ROM
        favourite.set_custom_attribute('launcherID',            self.get_id())
        favourite.set_custom_attribute('platform',              self.get_platform())
        favourite.set_custom_attribute('application',           self.get_custom_attribute('application'))
        favourite.set_custom_attribute('args',                  self.get_custom_attribute('args'))
        favourite.set_custom_attribute('args_extra',            self.get_custom_attribute('args_extra'))
        favourite.set_custom_attribute('rompath',               self.get_rom_path().getPath())
        favourite.set_custom_attribute('romext',                self.get_custom_attribute('romext'))
        favourite.set_custom_attribute('toggle_window',         self.is_in_windowed_mode())
        favourite.set_custom_attribute('non_blocking',          self.is_non_blocking())
        favourite.set_custom_attribute('roms_default_icon',     self.get_custom_attribute('roms_default_icon'))
        favourite.set_custom_attribute('roms_default_fanart',   self.get_custom_attribute('roms_default_fanart'))
        favourite.set_custom_attribute('roms_default_banner',   self.get_custom_attribute('roms_default_banner'))
        favourite.set_custom_attribute('roms_default_poster',   self.get_custom_attribute('roms_default_poster'))
        favourite.set_custom_attribute('roms_default_clearlogo',self.get_custom_attribute('roms_default_clearlogo'))

        # >> Favourite ROM unique fields
        # >> Favourite ROMs in "Most played ROMs" DB also have 'launch_count' field.
        favourite.set_favourite_status('OK')

        return favourite

    def get_duplicated_asset_dirs(self):
        duplicated_bool_list   = [False] * len(ROM_ASSET_LIST)
        duplicated_name_list   = []

        # >> Check for duplicated asset paths
        for i, asset_i in enumerate(ROM_ASSET_LIST[:-1]):
            A_i = assets_get_info_scheme(asset_i)
            for j, asset_j in enumerate(ROM_ASSET_LIST[i+1:]):
                A_j = assets_get_info_scheme(asset_j)
                # >> Exclude unconfigured assets (empty strings).
                if not self.entity_data[A_i.path_key] or not self.entity_data[A_j.path_key]: continue
                # log_debug('asset_get_duplicated_asset_list() Checking {0:<9} vs {1:<9}'.format(A_i.name, A_j.name))
                if self.entity_data[A_i.path_key] == self.entity_data[A_j.path_key]:
                    duplicated_bool_list[i] = True
                    duplicated_name_list.append('{0} and {1}'.format(A_i.name, A_j.name))
                    log_info('asset_get_duplicated_asset_list() DUPLICATED {0} and {1}'.format(A_i.name, A_j.name))

        return duplicated_name_list

    def set_default_rom_asset(self, asset_kind, mapped_to_kind):
        self.entity_data[asset_kind.rom_default_key] = mapped_to_kind.key

    def get_asset_path(self, asset_info):
        if not asset_info:
            return None

        return self._get_value_as_filename(asset_info.path_key)

    def set_asset_path(self, asset_info, path):
        log_debug('Setting "{}" to {}'.format(asset_info.path_key, path))
        self.entity_data[asset_info.path_key] = path

    def get_rom_path(self):
        return self._get_value_as_filename('rompath')

    def change_rom_path(self, path):
        self.entity_data['rompath'] = path

    def get_rom_asset_path(self):
        return self._get_value_as_filename('ROM_asset_path')

    def get_roms_base(self):
        return self.entity_data['roms_base_noext'] if 'roms_base_noext' in self.entity_data else None

    def update_roms_base(self, roms_base_noext):
        self.entity_data['roms_base_noext'] = roms_base_noext

    def get_roms_xml_file(self):
        return self.entity_data['roms_xml_file']
    
    def set_roms_xml_file(self, xml_file):
        self.entity_data['roms_xml_file'] = xml_file

    def clear_roms(self):
        self.entity_data['num_roms'] = 0
        self.roms = {}
        self.romset_repository.delete_all_by_launcher(self)

    def get_display_mode(self):
        return self.entity_data['launcher_display_mode'] if 'launcher_display_mode' in self.entity_data else LAUNCHER_DMODE_FLAT

    def change_display_mode(self, mode):
        if mode == LAUNCHER_DMODE_PCLONE or mode == LAUNCHER_DMODE_1G1R:
            # >> Check if user configured a No-Intro DAT. If not configured  or file does
            # >> not exists refuse to switch to PClone view and force normal mode.
            if not self.has_nointro_xml():
                log_info('RomsLauncher.change_display_mode() No-Intro DAT not configured.')
                log_info('RomsLauncher.change_display_mode() Forcing Flat view mode.')
                mode = LAUNCHER_DMODE_FLAT
            else:
                nointro_xml_file_FName = self.get_nointro_xml_filepath()
                if not nointro_xml_file_FName.exists():
                    log_info('RomsLauncher.change_display_mode() No-Intro DAT not found.')
                    log_info('RomsLauncher.change_display_mode() Forcing Flat view mode.')
                    kodi_dialog_OK('No-Intro DAT cannot be found. PClone or 1G1R view mode cannot be set.')
                    mode = LAUNCHER_DMODE_FLAT

        self.entity_data['launcher_display_mode'] = mode
        log_debug('launcher_display_mode = {0}'.format(mode))

        return mode

    def get_nointro_display_mode(self):
        return self.entity_data['nointro_display_mode'] if 'nointro_display_mode' in self.entity_data else LAUNCHER_DMODE_FLAT

    def change_nointro_display_mode(self, mode):
        self.entity_data['nointro_display_mode'] = mode
        log_info('Launcher nointro display mode changed to "{0}"'.format(self.entity_data['nointro_display_mode']))
        return mode

    def has_nointro_xml(self):
        return self.entity_data['nointro_xml_file']

    def get_nointro_xml_filepath(self):
        return self._get_value_as_filename('nointro_xml_file')

    def set_nointro_xml_file(self, path):
        self.entity_data['nointro_xml_file'] = path

    def reset_nointro_xmldata(self):
        if self.entity_data['nointro_xml_file']:
            log_info('Deleting XML DAT file and forcing launcher to Normal view mode.')
            self.entity_data['nointro_xml_file'] = ''

    def set_audit_stats(self, num_of_roms, num_audit_parents, num_audit_clones, num_audit_have, num_audit_miss, num_audit_unknown):
        self.set_number_of_roms(get_number_of_roms)
        self.entity_data['num_parents'] = num_audit_parents
        self.entity_data['num_clones']  = num_audit_clones
        self.entity_data['num_have']    = num_audit_have
        self.entity_data['num_miss']    = num_audit_miss
        self.entity_data['num_unknown'] = num_audit_unknown

    def set_number_of_roms(self, num_of_roms = -1):
        if num_of_roms == -1:
            num_of_roms = self.actual_amount_of_roms()
        self.entity_data['num_roms'] = num_of_roms

    def supports_multidisc(self):
        return self.entity_data['multidisc']

    def set_multidisc_support(self, supports_multidisc):
        self.entity_data['multidisc'] = supports_multidisc

        return self.supports_multidisc()

# -------------------------------------------------------------------------------------------------
# Collection Launcher
# Class hierarchy: CollectionLauncher --> ROMLauncherABC --> LauncherABC --> MetaDataItemABC --> object
# ------------------------------------------------------------------------------------------------- 
class CollectionLauncher(ROMLauncherABC):
    def __init__(self, PATHS, settings, collection_dic, 
                 executorFactory, romset_repository, statsStrategy):
        # Concrete classes are responsible of creating a default entity_data dictionary
        # with sensible defaults.
        if collection_dic is None:
            collection_dic = fs_new_collection()
            collection_dic['id'] = misc_generate_random_SID()
        super(CollectionLauncher, self).__init__(
            PATHS, settings, collection_dic, None, romset_repository, None, False
        )

    def get_object_name(self): return 'ROM Collection'

    def get_assets_kind(self): return KIND_ASSET_CATEGORY

    def get_launcher_type(self): return OBJ_LAUNCHER_COLLECTION

    def save_to_disk(self): self.objectRepository.save_collection(self.entity_data)

    def delete_from_disk(self):
        # Object becomes invalid after deletion
        self.objectRepository.delete_collection(self.entity_data)
        self.entity_data = None
        self.objectRepository = None

    def supports_launching_roms(self): return True

    def supports_parent_clone_roms(self): return False

    def _builder_get_wizard(self, wizard): return wizard

    def _build_pre_wizard_hook(self):
        log_debug('CollectionLauncher::_build_pre_wizard_hook() Starting ...')
        return True

    def _build_post_wizard_hook(self):
        log_debug('CollectionLauncher::_build_post_wizard_hook() Starting ...')
        return True

    # get_edit_options() is implemented in RomLauncher but Categories editing options
    # are different.
    def get_edit_options(self):
        options = collections.OrderedDict()
        options['EDIT_METADATA']       = 'Edit Metadata ...'
        options['EDIT_ASSETS']         = 'Edit Assets/Artwork ...'
        options['EDIT_DEFAULT_ASSETS'] = 'Choose default Assets/Artwork ...'
        options['EXPORT_COLLECTION']   = 'Export Collection XML'
        options['DELETE_COLLECTION']   = 'Delete Collection'

        return options

    # get_metadata_edit_options() has a general implementation in Launcher class for 
    # Standard ROM Launchers. ROM Collections metadata is different from a Standard ROM Launcher
    # so reimplement the method here.
    def get_metadata_edit_options(self):
        plot_str = text_limit_string(self.entity_data['m_plot'], PLOT_STR_MAXSIZE)
        rating = self.get_rating() if self.get_rating() != -1 else 'not rated'
        NFO_FileName = fs_get_launcher_NFO_name(self.settings, self.entity_data)
        NFO_found_str = 'NFO found' if NFO_FileName.exists() else 'NFO not found'

        options = collections.OrderedDict()
        options['EDIT_METADATA_TITLE']     = "Edit Title: '{0}'".format(self.get_name())
        options['EDIT_METADATA_GENRE']     = "Edit Genre: '{0}'".format(self.entity_data['m_genre'])
        options['EDIT_METADATA_RATING']    = "Edit Rating: '{0}'".format(rating)
        options['EDIT_METADATA_PLOT']      = "Edit Plot: '{0}'".format(plot_str)
        options['IMPORT_NFO_FILE_DEFAULT'] = 'Import NFO file (default {0})'.format(NFO_found_str)
        options['IMPORT_NFO_FILE_BROWSE']  = 'Import NFO file (browse NFO file) ...'
        options['SAVE_NFO_FILE_DEFAULT']   = 'Save NFO file (default location)'

        return options

    def launch(self): pass

    def _selectApplicationToUse(self): return False

    def _selectArgumentsToUse(self): return False

    def _selectRomFileToUse(self): return False

# -------------------------------------------------------------------------------------------------
# --- Virtual Launcher ---
# Virtual Launchers are ROM launchers which contain other ROMs from real launchers.
# Virtual Launchers cannot be edited.
# Virtual Launcher ROMs are Favourite ROMs that can be executed.
# ------------------------------------------------------------------------------------------------- 
class VirtualLauncher(ROMLauncherABC):
    def __init__(self, PATHS, settings, collection_dic, 
                 executorFactory, romset_repository, statsStrategy):
        # Look at the VirtualCategory construction for complete this.
        super(VirtualLauncher, self).__init__(
            launcher_data, settings, None, romset_repository, None, False
        )

    def get_object_name(self): return 'Virtual launcher'

    def get_assets_kind(self): return KIND_ASSET_LAUNCHER

    def get_launcher_type(self): return OBJ_LAUNCHER_VIRTUAL

    def supports_launching_roms(self): return True

    def supports_parent_clone_roms(self): return False

    def supports_ROM_audit(self): return True

    def _builder_get_wizard(self, wizard): return wizard

    def _build_pre_wizard_hook(self): return True

    def _build_post_wizard_hook(self): return True

    def get_main_edit_options(self): pass

    def get_advanced_modification_options(self): pass

    def launch(self): pass

    def _selectApplicationToUse(self): return False

    def _selectArgumentsToUse(self): return False

    def _selectRomFileToUse(self): return False

    def has_nointro_xml(self): return False

# -------------------------------------------------------------------------------------------------
# Standard ROM launcher where user can fully customize all settings.
#
# The standard ROM launcher also supports Parent/Clone view modes and No-Intro/REDUMP DAT audit.
# -------------------------------------------------------------------------------------------------
class StandardRomLauncher(ROMLauncherABC):
    #
    # Handle in this constructor the creation of a new empty ROM Launcher.
    # Concrete classes are responsible of creating a default entity_data dictionary
    # with sensible defaults.
    #
    def __init__(self, PATHS, settings, launcher_dic, objectRepository,
                 executorFactory, romsetRepository, statsStrategy):
        if launcher_dic is None:
            launcher_dic = fs_new_launcher()
            launcher_dic['id'] = misc_generate_random_SID()
            launcher_dic['type'] = OBJ_LAUNCHER_ROM
        super(StandardRomLauncher, self).__init__(
            PATHS, settings, launcher_dic, objectRepository, executorFactory, romsetRepository, statsStrategy
        )

    # --------------------------------------------------------------------------------------------
    # Core functions
    # --------------------------------------------------------------------------------------------
    def get_object_name(self): return 'ROM Launcher'

    def get_assets_kind(self): return KIND_ASSET_LAUNCHER

    def get_launcher_type(self): return OBJ_LAUNCHER_ROM

    def save_to_disk(self): self.objectRepository.save_launcher(self.entity_data)

    # Object becomes invalid after deletion
    def delete_from_disk(self):
        self.objectRepository.delete_launcher(self.entity_data)
        self.entity_data = None
        self.objectRepository = None

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Creates a new launcher using a wizard of dialogs. Called by parent build() method.
    #
    def _builder_get_wizard(self, wizard):
        wizard = WizardDialog_FileBrowse(wizard, 'application', 'Select the launcher application',
            1, self._builder_get_appbrowser_filter)
        wizard = WizardDialog_FileBrowse(wizard, 'rompath', 'Select the ROMs path',
            0, '')
        wizard = WizardDialog_Dummy(wizard, 'romext', '',
            self._builder_get_extensions_from_app_path)
        wizard = WizardDialog_Keyboard(wizard, 'romext','Set files extensions, use "|" as separator. (e.g lnk|cbr)')
        wizard = WizardDialog_Dummy(wizard, 'args', '',
            self._builder_get_arguments_from_application_path)
        wizard = WizardDialog_Keyboard(wizard, 'args', 'Application arguments')
        wizard = WizardDialog_Dummy(wizard, 'm_name', '',
            self._builder_get_title_from_app_path)
        wizard = WizardDialog_Keyboard(wizard, 'm_name','Set the title of the launcher',
            self._builder_get_title_from_app_path)
        wizard = WizardDialog_Selection(wizard, 'platform', 'Select the platform',
            AEL_platform_list)
        wizard = WizardDialog_Dummy(wizard, 'assets_path', '',
            self._builder_get_value_from_rompath)
        wizard = WizardDialog_FileBrowse(wizard, 'assets_path', 'Select asset/artwork directory',
            0, '')

        return wizard

    def _build_pre_wizard_hook(self):
        log_debug('StandardRomLauncher::_build_pre_wizard_hook() Starting ...')

        return True

    def _build_post_wizard_hook(self):
        log_debug('StandardRomLauncher::_build_post_wizard_hook() Starting ...')

        return super(StandardRomLauncher, self)._build_post_wizard_hook()

    # --------------------------------------------------------------------------------------------
    # Launcher edit methods
    # --------------------------------------------------------------------------------------------
    def get_main_edit_options(self, category):
        log_debug('StandardRomLauncher::get_main_edit_options() Returning edit options')

        options = collections.OrderedDict()
        options['EDIT_METADATA']          = 'Edit Metadata ...'
        options['EDIT_ASSETS']            = 'Edit Assets/Artwork ...'
        options['EDIT_DEFAULT_ASSETS']    = 'Choose default Assets/Artwork ...'
        options['EDIT_LAUNCHER_CATEGORY'] = "Change Category: '{0}'".format(category.get_name())
        options['EDIT_LAUNCHER_STATUS']   = 'Launcher status: {0}'.format(self.get_finished_str())
        options['LAUNCHER_ADVANCED_MODS'] = 'Advanced Modifications ...'
        options['LAUNCHER_MANAGE_ROMS']   = 'Manage ROMs ...'
        options['LAUNCHER_AUDIT_ROMS']    = 'Audit ROMs / Launcher view mode ...'
        options['EXPORT_LAUNCHER_XML']    = 'Export Launcher XML configuration ...'
        options['DELETE_LAUNCHER']        = 'Delete Launcher'

        return options

    #
    # get_advanced_modification_options() is custom for every concrete launcher class.
    #
    def get_advanced_modification_options(self):
        log_debug('StandardRomLauncher::get_advanced_modification_options() Returning edit options')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'
        multidisc_str     = 'ON' if self.entity_data['multidisc'] else 'OFF'

        options = collections.OrderedDict()
        options['EDIT_APPLICATION']        = "Edit Application: '{0}'".format(self.entity_data['application'])
        options['EDIT_ARGS']               = "Edit Arguments: '{0}'".format(self.entity_data['args'])
        options['EDIT_ADDITIONAL_ARGS']    = "Edit Aditional Arguments ..."
        options['EDIT_ROMPATH']            = "Edit ROM path: '{0}'".format(self.entity_data['rompath'])
        options['EDIT_ROMEXT']             = "Edit ROM extensions: '{0}'".format(self.entity_data['romext'])
        options['EDIT_TOGGLE_WINDOWED']    = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['EDIT_TOGGLE_NONBLOCKING'] = "Non-blocking launcher (now {0})".format(non_blocking_str)
        options['EDIT_TOGGLE_MULTIDISC']   = "Multidisc ROM support (now {0})".format(multidisc_str)

        return options

    # ---------------------------------------------------------------------------------------------
    # Execution methods
    # ---------------------------------------------------------------------------------------------
    def _launch_selectApplicationToUse(self):
        if self.rom.has_alternative_application():
            log_info('StandardRomLauncher() Using ROM altapp')
            self.application = FileName(self.rom.get_alternative_application())
        else:
            self.application = FileName(self.entity_data['application'])

        # --- Check for errors and abort if found --- todo: CHECK
        if not self.application.exists():
            log_error('StandardRomLauncher::_selectApplicationToUse(): Launching app not found "{0}"'.format(self.application.getPath()))
            kodi_notify_warn('Launching app not found {0}'.format(self.application.getPath()))
            return False

        return True

    def _launch_selectArgumentsToUse(self):
        if self.rom.has_alternative_arguments():
            log_info('StandardRomLauncher() Using ROM altarg')
            self.arguments = self.rom.get_alternative_arguments()
        elif self.entity_data['args_extra']:
             # >> Ask user what arguments to launch application
            log_info('StandardRomLauncher() Using Launcher args_extra')
            launcher_args = self.entity_data['args']
            arg_list = [self.entity_data_args] + self.entity_data['args_extra']
            dialog = xbmcgui.Dialog()
            dselect_ret = dialog.select('Select launcher arguments', arg_list)
            if dselect_ret < 0:
                return False
            log_info('StandardRomLauncher() User chose args index {0} ({1})'.format(dselect_ret, arg_list[dselect_ret]))
            self.arguments = arg_list[dselect_ret]
        else:
            self.arguments = self.entity_data['args']

        return True

    def _launch_selectRomFileToUse(self):
        if not self.rom.has_multiple_disks():
            self.selected_rom_file = self.rom.get_file()
            return True

        disks = self.rom.get_disks()
        log_info('StandardRomLauncher._selectRomFileToUse() Multidisc ROM set detected')
        dialog = xbmcgui.Dialog()
        dselect_ret = dialog.select('Select ROM to launch in multidisc set', disks)
        if dselect_ret < 0:
           return False

        selected_rom_base = disks[dselect_ret]
        log_info('StandardRomLauncher._selectRomFileToUse() Selected ROM "{0}"'.format(selected_rom_base))

        ROM_temp = self.rom.get_file()
        ROM_dir = FileName(ROM_temp.getDir())
        ROMFileName = ROM_dir.pjoin(selected_rom_base)

        log_info('StandardRomLauncher._selectRomFileToUse() ROMFileName OP "{0}"'.format(ROMFileName.getPath()))
        log_info('StandardRomLauncher._selectRomFileToUse() ROMFileName  P "{0}"'.format(ROMFileName.getPath()))

        if not ROMFileName.exists():
            log_error('ROM not found "{0}"'.format(ROMFileName.getPath()))
            kodi_notify_warn('ROM not found "{0}"'.format(ROMFileName.getPath()))
            return False

        self.selected_rom_file = ROMFileName

        return True

    # ---------------------------------------------------------------------------------------------
    # Launcher metadata and flags related methods
    # ---------------------------------------------------------------------------------------------
    # All of the in the parent class LauncherABC.
    def change_application(self):
        current_application = self.entity_data['application']
        selected_application = xbmcgui.Dialog().browse(1, 'Select the launcher application', 'files',
                                                      self._get_appbrowser_filter('application', self.entity_data), 
                                                      False, False, current_application).decode('utf-8')

        if selected_application is None or selected_application == current_application:
            return False

        self.entity_data['application'] = selected_application
        return True

    def change_arguments(self, args):
        self.entity_data['args'] = args

    def get_args(self):
        return self.entity_data['args']

    def get_additional_argument(self, index):
        args = self.get_all_additional_arguments()
        return args[index]

    def get_all_additional_arguments(self):
        return self.entity_data['args_extra']

    def add_additional_argument(self, arg):

        if not self.entity_data['args_extra']:
            self.entity_data['args_extra'] = []

        self.entity_data['args_extra'].append(arg)
        log_debug('launcher.add_additional_argument() Appending extra_args to launcher {0}'.format(self.get_id()))

    def set_additional_argument(self, index, arg):
        if not self.entity_data['args_extra']:
            self.entity_data['args_extra'] = []

        self.entity_data['args_extra'][index] = arg
        log_debug('launcher.set_additional_argument() Edited args_extra[{0}] to "{1}"'.format(index, self.entity_data['args_extra'][index]))

    def remove_additional_argument(self, index):
        del self.entity_data['args_extra'][index]
        log_debug("launcher.remove_additional_argument() Deleted launcher['args_extra'][{0}]".format(index))

    # ---------------------------------------------------------------------------------------------
    # Launcher asset methods
    # ---------------------------------------------------------------------------------------------
    # All Launcher asset functions must be in parent class LauncherABC.

    # ---------------------------------------------------------------------------------------------
    # NFO files for metadata
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # Misc functions
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # ROM methods
    # ---------------------------------------------------------------------------------------------
    # Move ROMs method to parent class ROMLauncherABC.
    def get_roms_filtered(self):
        if not self.has_roms():
            self.load_roms()

        filtered_roms = []
        view_mode     = self.get_display_mode()
        dp_mode       = self.get_nointro_display_mode()
        pclone_index  = self.get_pclone_indices()

        dp_modes_for_have    = [NOINTRO_DMODE_HAVE, NOINTRO_DMODE_HAVE_UNK, NOINTRO_DMODE_HAVE_MISS]
        dp_modes_for_miss    = [NOINTRO_DMODE_HAVE_MISS, NOINTRO_DMODE_MISS, NOINTRO_DMODE_MISS_UNK]
        dp_modes_for_unknown = [NOINTRO_DMODE_HAVE_UNK, NOINTRO_DMODE_MISS_UNK, NOINTRO_DMODE_UNK]

        for rom_id in self.roms:
            rom = self.roms[rom_id]
            nointro_status = rom.get_nointro_status()

            # >> Filter ROM
            # >> Always include a parent ROM regardless of filters in 'Parent/Clone mode'
            # >> and '1G1R mode' launcher_display_mode if it has 1 or more clones.
            if not view_mode == LAUNCHER_DMODE_FLAT and len(pclone_index[rom_id]):
                filtered_roms.append(rom)

            elif nointro_status == NOINTRO_STATUS_HAVE and dp_mode in dp_mode_for_have:
                filtered_roms.append(rom)

            elif nointro_status == NOINTRO_STATUS_MISS and dp_mode in dp_modes_for_miss:
                filtered_roms.append(rom)

            elif nointro_status == NOINTRO_STATUS_UNKNOWN and dp_mode in dp_modes_for_unknown:
                filtered_roms.append(rom)

            # >> Always copy roms with unknown status (NOINTRO_STATUS_NONE)
            else:
                filtered_roms.append(rom)

        return filtered_roms

    def get_rom_extensions_combined(self):
        return self.entity_data['romext']

    def get_rom_extensions(self):
        if not 'romext' in self.entity_data:
            return []

        return self.entity_data['romext'].split("|")

    def change_rom_extensions(self, ext):
        self.entity_data['romext'] = ext

    def get_parent_roms(self):
        return self.romset_repository.find_by_launcher(self, LAUNCHER_DMODE_PCLONE)

    def get_pclone_indices(self):
        return self.romset_repository.find_index_file_by_launcher(self, ROMSET_PCLONE)

    def get_parent_indices(self):
        return self.romset_repository.find_index_file_by_launcher(self, ROMSET_CPARENT)

    def update_parent_rom_set(self, roms):
        if not isinstance(roms,dict):
            roms = dict((rom.get_id(), rom) for rom in roms)

        self.romset_repository.save_rom_set(self, roms, LAUNCHER_DMODE_PCLONE)


# --- Retroplayer launcher ---
# See https://github.com/Wintermute0110/plugin.program.advanced.emulator.launcher/issues/33
# See https://forum.kodi.tv/showthread.php?tid=295463&pid=2620489#pid2620489
# -------------------------------------------------------------------------------------------------
class RetroplayerLauncher(ROMLauncherABC):
    #
    # Handle in this constructor the creation of a new empty ROM Launcher.
    # Concrete classes are responsible of creating a default entity_data dictionary
    # with sensible defaults.
    #
    def __init__(self, PATHS, settings, launcher_dic, objectRepository,
                 executorFactory, romsetRepository, statsStrategy):
        if launcher_dic is None:
            launcher_dic = fs_new_launcher()
            launcher_dic['id'] = misc_generate_random_SID()
            launcher_dic['type'] = OBJ_LAUNCHER_RETROPLAYER
        super(RetroplayerLauncher, self).__init__(
            PATHS, settings, launcher_dic, objectRepository, executorFactory, romsetRepository, statsStrategy
        )

    # --------------------------------------------------------------------------------------------
    # Core functions
    # --------------------------------------------------------------------------------------------
    def get_object_name(self): return 'Retroplayer launcher'

    def get_assets_kind(self): return KIND_ASSET_LAUNCHER

    def get_launcher_type(self): return OBJ_LAUNCHER_RETROPLAYER

    def save_to_disk(self): self.objectRepository.save_launcher(self.entity_data)

    def delete_from_disk(self):
        # Object becomes invalid after deletion.
        self.objectRepository.delete_launcher(self.entity_data)
        self.entity_data = None
        self.objectRepository = None

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Creates a new launcher using a wizard of dialogs. Called by build()
    #
    def _builder_get_wizard(self, wizard):
        log_debug('RetroplayerLauncher::_builder_get_wizard() Starting ...')

        # Retroplayer launcher must not ask for a launcher app name.
        wizard = WizardDialog_Dummy(wizard, 'application', RETROPLAYER_LAUNCHER_APP_NAME)
        wizard = WizardDialog_FileBrowse(wizard, 'rompath', 'Select the ROMs path',
            0, '')
        wizard = WizardDialog_Dummy(wizard, 'romext', '',
            self._builder_get_extensions_from_app_path)
        wizard = WizardDialog_Keyboard(wizard, 'romext','Set ROM extensions, use "|" as separator. (e.g lnk|cbr)')
        wizard = WizardDialog_Dummy(wizard, 'args', '$rom$')
        # Why m_name is repeated???
        wizard = WizardDialog_Dummy(wizard, 'm_name', '',
            self._builder_get_title_from_app_path)
        wizard = WizardDialog_Keyboard(wizard, 'm_name','Set the title of the launcher',
            self._builder_get_title_from_app_path)
        wizard = WizardDialog_Selection(wizard, 'platform', 'Select the platform',
            AEL_platform_list)
        wizard = WizardDialog_Dummy(wizard, 'assets_path', '',
            self._builder_get_value_from_rompath)
        wizard = WizardDialog_FileBrowse(wizard, 'assets_path', 'Select asset/artwork directory',
            0, '')

        return wizard

    def _build_pre_wizard_hook(self):
        log_debug('RetroplayerLauncher::_build_pre_wizard_hook() Starting ...')

        return True

    def _build_post_wizard_hook(self):
        log_debug('RetroplayerLauncher::_build_post_wizard_hook() Starting ...')

        return super(RetroplayerLauncher, self)._build_post_wizard_hook()

    # --------------------------------------------------------------------------------------------
    # Launcher edit methods
    # --------------------------------------------------------------------------------------------
    def get_main_edit_options(self, category):
        log_debug('RetroplayerLauncher::get_main_edit_options() Returning edit options')

        options = collections.OrderedDict()
        options['EDIT_METADATA']          = 'Edit Metadata ...'
        options['EDIT_ASSETS']            = 'Edit Assets/Artwork ...'
        options['EDIT_DEFAULT_ASSETS']    = 'Choose default Assets/Artwork ...'
        options['EDIT_LAUNCHER_CATEGORY'] = "Change Category: '{0}'".format(category.get_name())
        options['EDIT_LAUNCHER_STATUS']   = 'Launcher status: {0}'.format(self.get_finished_str())
        options['LAUNCHER_ADVANCED_MODS'] = 'Advanced Modifications ...'
        options['LAUNCHER_MANAGE_ROMS']   = 'Manage ROMs ...'
        options['LAUNCHER_AUDIT_ROMS']    = 'Audit ROMs / Launcher view mode ...'
        options['EXPORT_LAUNCHER_XML']    = 'Export Launcher XML configuration ...'
        options['DELETE_LAUNCHER']        = 'Delete Launcher'

        return options

    def get_advanced_modification_options(self):
        log_debug('RetroplayerLauncher::get_advanced_modification_options() Returning edit options')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'
        multidisc_str     = 'ON' if self.entity_data['multidisc'] else 'OFF'

        options = collections.OrderedDict()
        options['EDIT_ROMPATH']            = "Change ROM path: '{0}'".format(self.entity_data['rompath'])
        options['EDIT_ROMEXT']             = "Modify ROM extensions: '{0}'".format(self.entity_data['romext'])
        options['EDIT_TOGGLE_WINDOWED']    = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['EDIT_TOGGLE_NONBLOCKING'] = "Non-blocking launcher (now {0})".format(non_blocking_str)
        options['EDIT_TOGGLE_MULTIDISC']   = "Multidisc ROM support (now {0})".format(multidisc_str)

        return options

    # ---------------------------------------------------------------------------------------------
    # Execution methods
    # ---------------------------------------------------------------------------------------------
    def launch(self):
        log_info('RetroplayerLauncher::launch() Executing ROM with Kodi Retroplayer ...')
        self.title = self.rom.get_name()
        self._selectApplicationToUse()

        ROMFileName = self._selectRomFileToUse()

        # >> Create listitem object
        label_str = ROMFileName.getBase()
        listitem = xbmcgui.ListItem(label = label_str, label2 = label_str)
        # >> Listitem metadata
        # >> How to fill gameclient = string (game.libretro.fceumm) ???
        genre_list = list(rom['m_genre'])
        listitem.setInfo('game', {'title'    : label_str,     'platform'  : 'Test platform',
                                  'genres'   : genre_list,    'developer' : rom['m_developer'],
                                  'overview' : rom['m_plot'], 'year'      : rom['m_year'] })
        log_info('RetroplayerLauncher() application.getPath() "{0}"'.format(application.getPath()))
        log_info('RetroplayerLauncher() ROMFileName.getPath() "{0}"'.format(ROMFileName.getPath()))
        log_info('RetroplayerLauncher() label_str             "{0}"'.format(label_str))

        # --- User notification ---
        if self.settings['display_launcher_notify']:
            kodi_notify('Launching "{0}" with Retroplayer'.format(self.title))

        log_verb('RetroplayerLauncher() Calling xbmc.Player().play() ...')
        xbmc.Player().play(ROMFileName.getPath(), listitem)
        log_verb('RetroplayerLauncher() Calling xbmc.Player().play() returned. Leaving function.')

    def _launch_selectApplicationToUse(self): raise AddonError('Implement me!')

    def _launch_selectArgumentsToUse(self): raise AddonError('Implement me!')

    def _launch_selectRomFileToUse(self): raise AddonError('Implement me!')

    # ---------------------------------------------------------------------------------------------
    # Misc methods
    # ---------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
# Read RetroarchLauncher.md
# -------------------------------------------------------------------------------------------------
class RetroarchLauncher(StandardRomLauncher):
    #
    # Handle in this constructor the creation of a new empty ROM Launcher.
    # Concrete classes are responsible of creating a default entity_data dictionary
    # with sensible defaults.
    #
    def __init__(self, PATHS, settings, launcher_dic, objectRepository,
                 executorFactory, romsetRepository, statsStrategy):
        if launcher_dic is None:
            launcher_dic = fs_new_launcher()
            launcher_dic['id'] = misc_generate_random_SID()
            launcher_dic['type'] = OBJ_LAUNCHER_RETROARCH
        super(RetroarchLauncher, self).__init__(
            PATHS, settings, launcher_dic, objectRepository, executorFactory, romsetRepository, statsStrategy
        )

    # --------------------------------------------------------------------------------------------
    # Core functions
    # --------------------------------------------------------------------------------------------
    def get_object_name(self): return 'Retroarch launcher'

    def get_assets_kind(self): return KIND_ASSET_LAUNCHER

    def get_launcher_type(self): return OBJ_LAUNCHER_RETROARCH

    def save_to_disk(self): self.objectRepository.save_launcher(self.entity_data)

    def delete_from_disk(self):
        # Object becomes invalid after deletion.
        self.objectRepository.delete_launcher(self.entity_data)
        self.entity_data = None
        self.objectRepository = None

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Creates a new launcher using a wizard of dialogs.
    #
    def _builder_get_wizard(self, wizard):
        log_debug('RetroarchLauncher::_builder_get_wizard() Starting ...')
        wizard = WizardDialog_Dummy(wizard, 'application',
            self._builder_get_retroarch_app_folder(self.settings))
        wizard = WizardDialog_FileBrowse(wizard, 'application', 'Select the Retroarch path',
            0, '')
        wizard = WizardDialog_DictionarySelection(wizard, 'retro_config', 'Select the configuration',
            self._builder_get_available_retroarch_configurations)
        wizard = WizardDialog_FileBrowse(wizard, 'retro_config', 'Select the configuration',
            0, '', None, self._builder_user_selected_custom_browsing)
        wizard = WizardDialog_DictionarySelection(wizard, 'retro_core_info', 'Select the core',
            self._builder_get_available_retroarch_cores, self._builder_load_selected_core_info)
        wizard = WizardDialog_Keyboard(wizard, 'retro_core_info', 'Enter path to core file',
            self._builder_load_selected_core_info, self._builder_user_selected_custom_browsing)
        wizard = WizardDialog_FileBrowse(wizard, 'rompath', 'Select the ROMs path',
            0, '')
        wizard = WizardDialog_Keyboard(wizard, 'romext','Set files extensions, use "|" as separator. (e.g nes|zip)')
        wizard = WizardDialog_Dummy(wizard, 'args',
            self._builder_get_default_retroarch_arguments())
        wizard = WizardDialog_Keyboard(wizard, 'args', 'Extra application arguments')
        wizard = WizardDialog_Keyboard(wizard, 'm_name','Set the title of the launcher',
            self._builder_get_title_from_app_path)
        wizard = WizardDialog_Selection(wizard, 'platform', 'Select the platform',
            AEL_platform_list)
        wizard = WizardDialog_Dummy(wizard, 'assets_path', '',
            self._builder_get_value_from_rompath)
        wizard = WizardDialog_FileBrowse(wizard, 'assets_path', 'Select asset/artwork directory',
            0, '')

        return wizard

    #
    # In all platforms except Android:
    #   1) Check if user has configured the Retroarch executable, cores and system dir.
    #   2) Check if user has configured the Retroarch cores dir.
    #   3) Check if user has configured the Retroarch system dir.
    #
    # In Android:
    #   1) ...
    #
    # If any condition fails abort Retroarch launcher creation.
    #
    def _build_pre_wizard_hook(self):
        log_debug('RetroarchLauncher::_build_pre_wizard_hook() Starting ...')

        return True

    def _build_post_wizard_hook(self):
        log_debug('RetroarchLauncher::_build_post_wizard_hook() Starting ...')

        return super(RetroarchLauncher, self)._build_post_wizard_hook()

    def _builder_get_retroarch_app_folder(self, settings):
        if not is_android():
            # --- All platforms except Android ---
            retroarch_folder = FileName(settings['retroarch_system_dir'], isdir = True)
            if retroarch_folder.exists():
                return retroarch_folder.getPath()

        else:
            # --- Android ---
            android_retroarch_folders = [
                '/storage/emulated/0/Android/data/com.retroarch/',
                '/data/data/com.retroarch/',
                '/storage/sdcard0/Android/data/com.retroarch/',
                '/data/user/0/com.retroarch'
            ]
            for retroach_folder_path in android_retroarch_folders:
                retroarch_folder = FileName(retroach_folder_path)
                if retroarch_folder.exists():
                    return retroarch_folder.getPath()

        return '/'

    def _builder_get_available_retroarch_configurations(self, item_key, launcher):
        configs = collections.OrderedDict()
        configs['BROWSE'] = 'Browse for configuration'

        retroarch_folders = []
        retroarch_folders.append(FileName(launcher['application']))

        if is_android():
            retroarch_folders.append(FileName('/storage/emulated/0/Android/data/com.retroarch/'))
            retroarch_folders.append(FileName('/data/data/com.retroarch/'))
            retroarch_folders.append(FileName('/storage/sdcard0/Android/data/com.retroarch/'))
            retroarch_folders.append(FileName('/data/user/0/com.retroarch/'))

        for retroarch_folder in retroarch_folders:
            log_debug("get_available_retroarch_configurations() scanning path '{0}'".format(retroarch_folder.getPath()))
            files = retroarch_folder.recursiveScanFilesInPathAsFileNameObjects('*.cfg')
            if len(files) < 1: continue
            for file in files:
                log_debug("get_available_retroarch_configurations() adding config file '{0}'".format(file.getPath()))
                configs[file.getPath()] = file.getBase_noext()

            return configs

        return configs

    def _builder_get_available_retroarch_cores(self, item_key, launcher):
        cores = collections.OrderedDict()
        cores['BROWSE'] = 'Manual enter path to core'
        cores_ext = '*.*'

        if is_windows():
            cores_ext = '*.dll'
        else:
            cores_ext = '*.so'

        config_file   = FileName(launcher['retro_config'])
        parent_dir    = config_file.getDirAsFileName()
        configuration = config_file.readPropertyFile()
        info_folder   = self._create_path_from_retroarch_setting(configuration['libretro_info_path'], parent_dir)
        cores_folder  = self._create_path_from_retroarch_setting(configuration['libretro_directory'], parent_dir)
        log_debug("get_available_retroarch_cores() scanning path '{0}'".format(cores_folder.getPath()))

        if not info_folder.exists():
            log_warning('Retroarch info folder not found {}'.format(info_folder.getPath()))
            return cores
    
        if not cores_folder.exists():
            log_warning('Retroarch cores folder not found {}'.format(cores_folder.getPath()))
            return cores

        files = cores_folder.scanFilesInPathAsFileNameObjects(cores_ext)
        for file in files:
                
            log_debug("get_available_retroarch_cores() adding core '{0}'".format(file.getPath()))    
            info_file = self._switch_core_to_info_file(file, info_folder)

            if not info_file.exists():
                log_warning('get_available_retroarch_cores() Cannot find "{}". Skipping core "{}"'.format(info_file.getPath(), file.getBase()))
                continue

            log_debug("get_available_retroarch_cores() using info '{0}'".format(info_file.getPath()))    
            core_info = info_file.readPropertyFile()
            cores[info_file.getPath()] = core_info['display_name']

        return cores

    def _builder_load_selected_core_info(self, input, item_key, launcher):
        if input == 'BROWSE':
            return input

        if is_windows():
            cores_ext = 'dll'
        else:
            cores_ext = 'so'

        if input.endswith(cores_ext):
            core_file = FileName(input)
            launcher['retro_core']  = core_file.getPath()
            return input

        config_file     = FileName(launcher['retro_config'])
        parent_dir      = config_file.getDirAsFileName()
        configuration   = config_file.readPropertyFile()
        cores_folder    = self._create_path_from_retroarch_setting(configuration['libretro_directory'], parent_dir)
        info_file       = FileName(input)
        
        if not cores_folder.exists():
            log_warning('Retroarch cores folder not found {}'.format(cores_folder.getPath()))
            kodi_notify_error('Retroarch cores folder not found {}'.format(cores_folder.getPath()))
            return ''

        core_file = self._switch_info_to_core_file(info_file, cores_folder, cores_ext)
        core_info = info_file.readPropertyFile()

        launcher[item_key]      = info_file.getPath()
        launcher['retro_core']  = core_file.getPath()
        launcher['romext']      = core_info['supported_extensions']
        launcher['platform']    = core_info['systemname']
        launcher['m_developer'] = core_info['manufacturer']
        launcher['m_name']      = core_info['systemname']

        return input

    def _builder_get_default_retroarch_arguments(self):
        args = ''
        if is_android():
            args += '-e IME com.android.inputmethod.latin/.LatinIME -e REFRESH 60'

        return args

    # --------------------------------------------------------------------------------------------
    # Launcher edit methods
    # --------------------------------------------------------------------------------------------
    def get_main_edit_options(self, category):
        log_debug('RetroarchLauncher::get_main_edit_options() Returning edit options')

        options = collections.OrderedDict()
        options['EDIT_METADATA']          = 'Edit Metadata ...'
        options['EDIT_ASSETS']            = 'Edit Assets/Artwork ...'
        options['EDIT_DEFAULT_ASSETS']    = 'Choose default Assets/Artwork ...'
        options['EDIT_LAUNCHER_CATEGORY'] = "Change Category: '{0}'".format(category.get_name())
        options['EDIT_LAUNCHER_STATUS']   = 'Launcher status: {0}'.format(self.get_finished_str())
        options['LAUNCHER_ADVANCED_MODS'] = 'Advanced Modifications ...'
        options['LAUNCHER_MANAGE_ROMS']   = 'Manage ROMs ...'
        options['LAUNCHER_AUDIT_ROMS']    = 'Audit ROMs / Launcher view mode ...'
        options['EXPORT_LAUNCHER_XML']    = 'Export Launcher XML configuration ...'
        options['DELETE_LAUNCHER']        = 'Delete Launcher'

        return options

    def get_advanced_modification_options(self):
        log_debug('RetroarchLauncher::get_advanced_modification_options() Returning edit options')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'
        multidisc_str     = 'ON' if self.entity_data['multidisc'] else 'OFF'

        options = super(RetroarchLauncher, self).get_advanced_modification_options()
        options['CHANGE_APPLICATION']   = "Change Retroarch path: '{0}'".format(self.entity_data['application'])
        options['MODIFY_ARGS'] = "Modify Arguments: '{0}'".format(self.entity_data['args'])
        options['ADDITIONAL_ARGS'] = "Modify aditional arguments ..."
        options['CHANGE_ROMPATH'] = "Change ROM path: '{0}'".format(self.entity_data['rompath'])
        options['CHANGE_ROMEXT'] = "Modify ROM extensions: '{0}'".format(self.entity_data['romext'])
        options['TOGGLE_WINDOWED'] = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['TOGGLE_NONBLOCKING'] = "Non-blocking launcher (now {0})".format(non_blocking_str)
        options['TOGGLE_MULTIDISC'] = "Multidisc ROM support (now {0})".format(multidisc_str)

        return options

    # ---------------------------------------------------------------------------------------------
    # Execution methods
    # ---------------------------------------------------------------------------------------------
    def _launch_selectApplicationToUse(self):
        if is_windows():
            self.application = FileName(self.entity_data['application'])
            self.application = self.application.append('retroarch.exe')  
            return True

        if is_android():
            self.application = FileName('/system/bin/am')
            return True

        # TODO other os
        self.application = ''

        return False

    def _launch_selectArgumentsToUse(self):
        if is_windows() or is_linux():
            self.arguments =  '-L "$retro_core$" '
            self.arguments += '-c "$retro_config$" '
            self.arguments += '"$rom$"'
            self.arguments += self.entity_data['args']
            return True

        if is_android():
            self.arguments =  'start --user 0 -a android.intent.action.MAIN -c android.intent.category.LAUNCHER '
            self.arguments += '-n com.retroarch/.browser.retroactivity.RetroActivityFuture '
            self.arguments += '-e ROM \'$rom$\' '
            self.arguments += '-e LIBRETRO $retro_core$ '
            self.arguments += '-e CONFIGFILE $retro_config$ '
            self.arguments += self.entity_data['args'] if 'args' in self.entity_data else ''
            return True

        # TODO: other OSes
        return False

    def _launch_selectRomFileToUse(self): raise AddonError('Implement me!')

    # ---------------------------------------------------------------------------------------------
    # Misc methods
    # ---------------------------------------------------------------------------------------------
    def change_application(self):
        current_application = self.entity_data['application']
        selected_application = xbmcgui.Dialog().browse(0, 'Select the Retroarch path', 'files',
                                                       '', False, False, current_application).decode('utf-8')

        if selected_application is None or selected_application == current_application:
            return False
        self.entity_data['application'] = selected_application

        return True

    def _create_path_from_retroarch_setting(self, path_from_setting, parent_dir):
        if not path_from_setting.endswith('\\') and not path_from_setting.endswith('/'):
            path_from_setting = path_from_setting + parent_dir.path_separator()

        if path_from_setting.startswith(':\\'):
            path_from_setting = path_from_setting[2:]
            return parent_dir.pjoin(path_from_setting)
        else:
            folder = FileName(path_from_setting)
            if '/data/user/0/' in folder.getPath():
                alternative_folder = foldexr.getPath()
                alternative_folder = alternative_folder.replace('/data/user/0/', '/data/data/')
                folder = FileName(alternative_folder)

            return folder

    def _switch_core_to_info_file(self, core_file, info_folder):
        info_file = core_file.switchExtension('info')
   
        if is_android():
            info_file = info_folder.pjoin(info_file.getBase().replace('_android.', '.'))
        else:
            info_file = info_folder.pjoin(info_file.getBase())

        return info_file

    def _switch_info_to_core_file(self, info_file, cores_folder, cores_ext):
        core_file = info_file.switchExtension(cores_ext)
        if is_android():
            core_file = cores_folder.pjoin(core_file.getBase().replace('.', '_android.'))
        else:
            core_file = cores_folder.pjoin(core_file.getBase())

        return core_file

# -------------------------------------------------------------------------------------------------
# Launcher for .lnk files (windows)
# -------------------------------------------------------------------------------------------------
class LnkLauncher(StandardRomLauncher):
    #
    # Handle in this constructor the creation of a new empty ROM Launcher.
    # Concrete classes are responsible of creating a default entity_data dictionary
    # with sensible defaults.
    #
    def __init__(self, PATHS, settings, launcher_dic, objectRepository,
                 executorFactory, romsetRepository, statsStrategy):
        if launcher_dic is None:
            launcher_dic = fs_new_launcher()
            launcher_dic['id'] = misc_generate_random_SID()
            launcher_dic['type'] = OBJ_LAUNCHER_RETROARCH
        super(LnkLauncher, self).__init__(
            PATHS, settings, launcher_dic, objectRepository, executorFactory, romsetRepository, statsStrategy
        )

    # --------------------------------------------------------------------------------------------
    # Core functions
    # --------------------------------------------------------------------------------------------
    def get_object_name(self): return 'LNK launcher'

    def get_assets_kind(self): return KIND_ASSET_LAUNCHER

    def get_launcher_type(self): return OBJ_LAUNCHER_LNK

    def save_to_disk(self): self.objectRepository.save_launcher(self.entity_data)

    # --------------------------------------------------------------------------------------------
    # Launcher build wizard methods
    # --------------------------------------------------------------------------------------------
    #
    # Creates a new launcher using a wizard of dialogs.
    #
    def _builder_get_wizard(self, wizard):
        log_debug('LnkLauncher::_builder_get_wizard() Returning edit options')
        wizard = WizardDialog_FileBrowse(wizard, 'rompath', 'Select the LNKs path',
            0, '')
        wizard = WizardDialog_Dummy(wizard, 'romext', 'lnk')
        wizard = WizardDialog_Dummy(wizard, 'args', '$rom$')
        wizard = WizardDialog_Dummy(wizard, 'm_name', '',
            self._get_title_from_app_path)
        wizard = WizardDialog_Keyboard(wizard, 'm_name','Set the title of the launcher',
            self._get_title_from_app_path)
        wizard = WizardDialog_Selection(wizard, 'platform', 'Select the platform',
            AEL_platform_list)
        wizard = WizardDialog_Dummy(wizard, 'assets_path', '',
            self._get_value_from_rompath)
        wizard = WizardDialog_FileBrowse(wizard, 'assets_path', 'Select asset/artwork directory',
            0, '')

        return wizard

    # --------------------------------------------------------------------------------------------
    # Launcher edit methods
    # --------------------------------------------------------------------------------------------
    def get_main_edit_options(self, category):
        log_debug('LnkLauncher::get_main_edit_options() Returning edit options')

        options = collections.OrderedDict()
        options['EDIT_METADATA']          = 'Edit Metadata ...'
        options['EDIT_ASSETS']            = 'Edit Assets/Artwork ...'
        options['EDIT_DEFAULT_ASSETS']    = 'Choose default Assets/Artwork ...'
        options['EDIT_LAUNCHER_CATEGORY'] = "Change Category: '{0}'".format(category.get_name())
        options['EDIT_LAUNCHER_STATUS']   = 'Launcher status: {0}'.format(self.get_finished_str())
        options['LAUNCHER_ADVANCED_MODS'] = 'Advanced Modifications ...'
        options['LAUNCHER_MANAGE_ROMS']   = 'Manage ROMs ...'
        options['EXPORT_LAUNCHER_XML']    = 'Export Launcher XML configuration ...'
        options['DELETE_LAUNCHER']        = 'Delete Launcher'

        return options

    def get_advanced_modification_options(self):
        log_debug('LnkLauncher::get_advanced_modification_options() Returning edit options')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'
        multidisc_str     = 'ON' if self.entity_data['multidisc'] else 'OFF'

        options = collections.OrderedDict()
        options['EDIT_ROMPATH']            = "Change ROM path: '{0}'".format(self.entity_data['rompath'])
        options['EDIT_ROMEXT']             = "Modify ROM extensions: '{0}'".format(self.entity_data['romext'])
        options['EDIT_TOGGLE_WINDOWED']    = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['EDIT_TOGGLE_NONBLOCKING'] = "Non-blocking launcher (now {0})".format(non_blocking_str)
        options['EDIT_TOGGLE_MULTIDISC']   = "Multidisc ROM support (now {0})".format(multidisc_str)

        return options

    # ---------------------------------------------------------------------------------------------
    # Execution methods
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # Misc methods
    # ---------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
# Launcher to use with a local Steam application and account.
# -------------------------------------------------------------------------------------------------
class SteamLauncher(ROMLauncherABC):
    def __init__(self, launcher_data, settings, executorFactory, romset_repository, statsStrategy):
        super(SteamLauncher, self).__init__(
            launcher_data, settings, executorFactory, romset_repository, statsStrategy, False
        )

    def get_launcher_type(self): return LAUNCHER_STEAM

    def get_launcher_type_name(self): return 'Steam launcher'

    def get_steam_id(self): return self.entity_data['steamid']

    def get_edit_options(self):
        options = super(SteamLauncher, self).get_edit_options()
        del options['AUDIT_ROMS']

        return options

    def get_advanced_modification_options(self):
        log_debug('SteamLauncher::get_advanced_modification_options() Returning edit options')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'

        options = super(SteamLauncher, self).get_advanced_modification_options()
        options['TOGGLE_WINDOWED'] = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['TOGGLE_NONBLOCKING'] = "Non-blocking launcher (now {0})".format(non_blocking_str)

        return options

    def _selectApplicationToUse(self):
        self.application = FileName('steam://rungameid/')

        return True

    def _selectArgumentsToUse(self):
        self.arguments = '$steamid$'

        return True

    def _selectRomFileToUse(self):
        steam_id = self.rom.get_custom_attribute('steamid', '')
        log_info('SteamLauncher._selectRomFileToUse() ROM ID {0}: @{1}"'.format(steam_id, self.title))

        return True

       #def launch(self):
       #    
       #    self.title  = self.rom['m_name']
       #    
       #    url = 'steam://rungameid/'
       #
       #    self.application = FileName('steam://rungameid/')
       #    self.arguments = str(self.rom['steamid'])
       #
       #    log_info('SteamLauncher() ROM ID {0}: @{1}"'.format(self.rom['steamid'], self.rom['m_name']))
       #    self.statsStrategy.updateRecentlyPlayedRom(self.rom)
       #    
       #    super(SteamLauncher, self).launch()
       #    pass

    def _get_builder_wizard(self, wizard):
        wizard = WizardDialog_Dummy(wizard, 'application', 'Steam')
        wizard = WizardDialog_Keyboard(wizard, 'steamid','Steam ID')
        wizard = WizardDialog_Dummy(wizard, 'm_name', 'Steam')
        wizard = WizardDialog_Keyboard(wizard, 'm_name','Set the title of the launcher',
            self._get_title_from_app_path)
        wizard = WizardDialog_Selection(wizard, 'platform', 'Select the platform',
            AEL_platform_list, wizard)
        wizard = WizardDialog_FileBrowse(wizard, 'assets_path', 'Select asset/artwork directory',
            0, '')
        wizard = WizardDialog_Dummy(wizard, 'rompath', '',
            self._get_value_from_assetpath)

        return wizard

    def _get_value_from_assetpath(self, input, item_key, launcher):
        if input: return input

        romPath = FileName(launcher['assets_path'])
        romPath = romPath.pjoin('games')

        return romPath.getPath()
 
# -------------------------------------------------------------------------------------------------
# Launcher to use with Nvidia Gamestream servers.
# -------------------------------------------------------------------------------------------------
class NvidiaGameStreamLauncher(ROMLauncherABC):
    def __init__(self, launcher_data, settings, executorFactory, romset_repository, statsStrategy):
        super(NvidiaGameStreamLauncher, self).__init__(
            launcher_data, settings, executorFactory, romset_repository, statsStrategy, False)

    def get_launcher_type(self): return LAUNCHER_NVGAMESTREAM

    def get_launcher_type_name(self): return 'NVIDIA GameStream launcher'

    def get_server(self): return self.entity_data['server']

    def get_certificates_path(self): return self._get_value_as_filename('certificates_path')

    def get_edit_options(self):
        options = super(NvidiaGameStreamLauncher, self).get_edit_options()
        del options['AUDIT_ROMS']

        return options

    def get_advanced_modification_options(self):
        log_debug('NvidiaGameStreamLauncher::get_advanced_modification_options() Returning edit options')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'
        
        options = super(SteamLauncher, self).get_advanced_modification_options()
        options['TOGGLE_WINDOWED'] = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['TOGGLE_NONBLOCKING'] = "Non-blocking launcher (now {0})".format(non_blocking_str)

    def _selectApplicationToUse(self):
        streamClient = self.entity_data['application']

        # java application selected (moonlight-pc)
        if '.jar' in streamClient:
            self.application = FileName(os.getenv("JAVA_HOME"))
            if is_windows():
                self.application = self.application.pjoin('bin\\java.exe')
            else:
                self.application = self.application.pjoin('bin/java')

            return True

        if is_windows():
            self.application = FileName(streamClient)
            return True

        if is_android():
            self.application = FileName('/system/bin/am')
            return True

        return True

    def _selectArgumentsToUse(self):
        streamClient = self.entity_data['application']

        # java application selected (moonlight-pc)
        if '.jar' in streamClient:
            self.arguments =  '-jar "$application$" '
            self.arguments += '-host $server$ '
            self.arguments += '-fs '
            self.arguments += '-app "$gamestream_name$" '
            self.arguments += self.entity_data['args']
            return True

        if is_android():
            if streamClient == 'NVIDIA':
                self.arguments =  'start --user 0 -a android.intent.action.VIEW '
                self.arguments += '-n com.nvidia.tegrazone3/com.nvidia.grid.UnifiedLaunchActivity '
                self.arguments += '-d nvidia://stream/target/2/$streamid$'
                return True

            elif streamClient == 'MOONLIGHT':
                self.arguments =  'start --user 0 -a android.intent.action.MAIN '
                self.arguments += '-c android.intent.category.LAUNCHER ' 
                self.arguments += '-n com.limelight/.Game '
                self.arguments += '-e Host $server$ '
                self.arguments += '-e AppId $streamid$ '
                self.arguments += '-e AppName "$gamestream_name$" '
                self.arguments += '-e PcName "$server_hostname$" '
                self.arguments += '-e UUID $server_id$ '
                self.arguments += '-e UniqueId {} '.format(misc_generate_random_SID())

                return True

        # else
        self.arguments = self.entity_data['args']

        return True 
  
    def _selectRomFileToUse(self): return True

    def get_advanced_modification_options(self):
        log_debug('NvidiaGameStreamLauncher::get_advanced_modification_options() Returning edit options')
        toggle_window_str = 'ON' if self.entity_data['toggle_window'] else 'OFF'
        non_blocking_str  = 'ON' if self.entity_data['non_blocking'] else 'OFF'

        options = super(NvidiaGameStreamLauncher, self).get_advanced_modification_options()
        options['TOGGLE_WINDOWED'] = "Toggle Kodi into windowed mode (now {0})".format(toggle_window_str)
        options['TOGGLE_NONBLOCKING'] = "Non-blocking launcher (now {0})".format(non_blocking_str)

        return options

    #
    # Creates a new launcher using a wizard of dialogs.
    #
    def _get_builder_wizard(self, wizard):
        info_txt  = 'To pair with your Geforce Experience Computer we need to make use of valid certificates. '
        info_txt += 'Unfortunately at this moment we cannot create these certificates directly from within Kodi.\n'
        info_txt += 'Please read the wiki for details how to create them before you go further.'

        wizard = WizardDialog_FormattedMessage(wizard, 'certificates_path', 'Pairing with Gamestream PC',
            info_txt)
        wizard = WizardDialog_DictionarySelection(wizard, 'application', 'Select the client',
            {'NVIDIA': 'Nvidia', 'MOONLIGHT': 'Moonlight'}, 
            self._check_if_selected_gamestream_client_exists, lambda pk, p: is_android())
        wizard = WizardDialog_DictionarySelection(wizard, 'application', 'Select the client',
            {'JAVA': 'Moonlight-PC (java)', 'EXE': 'Moonlight-Chrome (not supported yet)'},
            None, lambda pk,p: not is_android())
        wizard = WizardDialog_FileBrowse(wizard, 'application', 'Select the Gamestream client jar',
            1, self._get_appbrowser_filter, None, lambda pk, p: not is_android())
        wizard = WizardDialog_Keyboard(wizard, 'args', 'Additional arguments', 
            None, lambda pk, p: not is_android())
        wizard = WizardDialog_Input(wizard, 'server', 'Gamestream Server',
            xbmcgui.INPUT_IPADDRESS, self._validate_gamestream_server_connection)
        wizard = WizardDialog_Keyboard(wizard, 'm_name','Set the title of the launcher', 
            self._get_title_from_app_path)
        wizard = WizardDialog_FileBrowse(wizard, 'assets_path', 'Select asset/artwork directory', 0, '')
        wizard = WizardDialog_Dummy(wizard, 'rompath', '', 
            self._get_value_from_assetpath)
        # Pairing with pin code will be postponed untill crypto and certificate support in kodi
        # wizard = WizardDialog_Dummy(wizard, 'pincode', None, generatePairPinCode)
        wizard = WizardDialog_Dummy(wizard, 'certificates_path', None,
            self._try_to_resolve_path_to_nvidia_certificates)
        wizard = WizardDialog_FileBrowse(wizard, 'certificates_path', 'Select the path with valid certificates', 
            0, '', self._validate_nvidia_certificates) 
        wizard = WizardDialog_Selection(wizard, 'platform', 'Select the platform',
            AEL_platform_list)

        return wizard

    def _generatePairPinCode(self, input, item_key, launcher):
        return gamestreamServer(None, None).generatePincode()

    def _check_if_selected_gamestream_client_exists(self, input, item_key, launcher):
        if input == 'NVIDIA':
            nvidiaDataFolder = FileName('/data/data/com.nvidia.tegrazone3/', isdir = True)
            nvidiaAppFolder = FileName('/storage/emulated/0/Android/data/com.nvidia.tegrazone3/')
            if not nvidiaAppFolder.exists() and not nvidiaDataFolder.exists():
                kodi_notify_warn("Could not find Nvidia Gamestream client. Make sure it's installed.")

        elif input == 'MOONLIGHT':
            moonlightDataFolder = FileName('/data/data/com.limelight/', isdir = True)
            moonlightAppFolder = FileName('/storage/emulated/0/Android/data/com.limelight/')
            if not moonlightAppFolder.exists() and not moonlightDataFolder.exists():
                kodi_notify_warn("Could not find Moonlight Gamestream client. Make sure it's installed.")

        return input

    def _try_to_resolve_path_to_nvidia_certificates(self, input, item_key, launcher):
        path = GameStreamServer.try_to_resolve_path_to_nvidia_certificates()

        return path

    def _validate_nvidia_certificates(self, input, item_key, launcher):
        certificates_path = FileName(input)
        gs = GameStreamServer(input, certificates_path)
        if not gs.validate_certificates():
            kodi_notify_warn(
                'Could not find certificates to validate. Make sure you already paired with '
                'the server with the Shield or Moonlight applications.')

        return certificates_path.getPath()

    def _validate_gamestream_server_connection(self, input, item_key, launcher):
        gs = GameStreamServer(input, None)
        if not gs.connect():
            kodi_notify_warn('Could not connect to gamestream server')

        launcher['server_id'] = gs.get_uniqueid()
        launcher['server_hostname'] = gs.get_hostname()

        log_debug('validate_gamestream_server_connection() Found correct gamestream server with id "{}" and hostname "{}"'.format(launcher['server_id'],launcher['server_hostname']))

        return input

# ------------------------------------------------------------------------------------------------
# --- AEL Object Factory -------------------------------------------------------------------------
#
# * Used to create an AEL object that is a child of MetaDataItemACB().
#
# * A global and unique instance of AELObjectFactory is created in main.py to create all
#   required objects in the addon.
#
# * For performance reasons the ListItem renderers access the databases directly using functions
#   from disk_IO.py.
#
# * Only Launcher objects can create ROM objects.
#
# * Every object (Category, Launcher, ROM) must be able to save itself to disk. This is required
#   to simplify the recursive Edit Object menu.
#   For example:
#      launcher.save_to_disk()  Saves Launcher to disk
#      rom.save_to_disk()       Saves ROM to disk.
#
# * Abstract Factory Pattern
#   See https://www.oreilly.com/library/view/head-first-design/0596007124/ch04.html
#
# --- Category creation and edition --------------------------------------------------------------
#
#  1. Create a new Category:
#     category = AELObjectFactory.create_new(OBJ_CATEGORY)
#     category.save_to_disk()
#
#  3. Retrieve a list of all Categories from disk, sorted alphabetically by Name:
#     categories_list = AELObjectFactory.find_category_all()
#
#  2. Retrieve a Category from disk (for example, in Edit Category context menu):
#     category = AELObjectFactory.find_category(category_id)
#     category.save_to_disk()
#
# --- Launcher creation and edition --------------------------------------------------------------
#
#  4. Create a new real Launcher:
#     launcher = AELObjectFactory.create_new(OBJ_LAUNCHER_ROM)
#     OR
#     launcher = AELObjectFactory.create_new(OBJ_LAUNCHER_ROM)
#     launcher.build(category)
#     launcher.save_to_disk()
#
#  5. Retrieve a list of all real Launchers in a Category, sorted alphabetically by Name:
#     launcher_list = AELObjectFactory.find_launchers_in_cat(category_id)
#
#  6. Retrieve a real Launcher from disk (real launcher can be edited):
#     launcher = AELObjectFactory.find_launcher(category_id, launcher_id)
#     launcher.save_to_disk()
#
# --- ROM Collection creation and edition --------------------------------------------------------
#
#  7. Create a new ROM Collection. Category is implicit:
#     collection = AELObjectFactory.create_new(OBJ_LAUNCHER_COLLECTION)
#     collection.set_name('Sonic')
#     collection.save_to_disk()
#
#  8. Retrieve a list of all ROM Collection launchers from disk:
#     collections_list = AELObjectFactory.find_launchers_in_cat(VCATEGORY_COLLECTIONS_ID)
#
#  9. Retrieve a ROM Collection from disk (for example, in Edit Collection context menu):
#     collection = AELObjectFactory.find_launcher(VCATEGORY_COLLECTIONS_ID, launcher_id)
#     collection.save_to_disk()
#
# --- Virtual Launcher related functions ---------------------------------------------------------
#
# 10. Create a new Virtual Launcher:
#     vlauncher = AELObjectFactory.create_new(OBJ_LAUNCHER_VIRTUAL, VCATEGORY_TITLE_ID)
#     vlauncher.set_name('A')
#     vlauncher.save_to_disk()
#
# 11. Retrieve a list of all Virtual Launchers of a given type:
#     vlauncher_list = AELObjectFactory.find_launchers_in_cat(VCATEGORY_TITLE_ID)
#
# 12. Retrieve a Virtual Launcher from disk:
#     vlauncher = AELObjectFactory.find_launcher(VCATEGORY_TITLE_ID, launcher_id)
#
# --- Creation of ROMs ---------------------------------------------------------------------------
#
# 13. Create a new ROM:
#     launcher = AELObjectFactory.create_new(OBJ_LAUNCHER_ROM, category_id)
#     ROM = launcher.create_new_ROM()
#
# 14. Retrieve a ROM in a Launcher for edition:
#     launcher = AELObjectFactory.find_launcher(VCATEGORY_ACTUAL_LAUN_ID, launcher_id)
#     launcher.load_ROMs()
#     ROM = launcher.find_ROM(rom_id)
#     launcher.save_ROMs_disk()
#
# --- Favourite ROM creation ---------------------------------------------------------------------
#
# 16. Add ROM to Favourites:
#     launcher = AELObjectFactory.find_launcher(VCATEGORY_ACTUAL_LAUN_ID, launcher_id)
#     ROM = launcher.create_new_ROM()
#     favourites = AELObjectFactory.find_launcher(VCATEGORY_FAVOURITES_ID) # Launcher ID implicit
#     favourites.add_ROM(ROM)
#     favourites.save_to_disk()
#
# 17. Add ROM to Collection:
#     launcher = AELObjectFactory.find_launcher(VCATEGORY_ACTUAL_LAUN_ID, launcher_id)
#     ROM = launcher.create_new_ROM()
#     collection = AELObjectFactory.find_launcher(VCATEGORY_COLLECTIONS_ID, launcher_id)
#     collection.add_ROM(ROM)
#     collection.save_to_disk()
#
# 18. Build Virtual Launchers:
#     launcher_list = ...
#     all_ROMs = []
#     for launcher in launcher_list:
#         roms = launcher...
#         for rom in roms:
#             all_ROMs.insert(rom)
#     for name in names:
#         vlauncher = AELObjectFactory.create_new(OBJ_LAUNCHER_VIRTUAL, VCATEGORY_TITLE_ID)
#         vlauncher.set_name(name)
#         vlauncher.add_ROM(ROM)
#         vlauncher.save_to_disk()
#
# --- Render of ROMs in a Standard ROM Launcher --------------------------------------------------
#
# 19. Render ROMs in a Launcher:
#     launcher = AELObjectFactory.find_launcher(VCATEGORY_ACTUAL_LAUN_ID, launcher_id)
#     for rom in launcher.find_ROMs_all():
#         rom.get_name()
#
# 20. Render ROMs in a Launcher (filtered):
#
# 21. Render ROMs in a Collection:
#     collection = AELObjectFactory.find_launcher(VCATEGORY_COLLECTIONS_ID, launcher_id)
#     for rom in collection.find_ROMs_all():
#         rom.get_name()
#
# --- View context menu --------------------------------------------------------------------------
#
# 22. Render Category database information:
#     category = AELObjectFactory.find_category(category_id)
#
# 23. Render Launcher database information (Category is required):
#     launcher = AELObjectFactory.find_launcher(VCATEGORY_ACTUAL_LAUN_ID, launcher_id)
#     category = AELObjectFactory.find_category(launcher.get_category_ID())
#
# 24. Render ROM database information (Category and Launcher required)
#     launcher = AELObjectFactory.find_launcher(VCATEGORY_ACTUAL_LAUN_ID, launcher_id)
#     category = AELObjectFactory.find_category(launcher.get_category_ID())
#     ROM = launcher.find_ROM(rom_id)
#
class AELObjectFactory(object):
    def __init__(self, PATHS, settings, objectRepository, executorFactory):
        # PATHS and settings are used in the creation of all object.
        # executorFactory is used in the creation of Launcher objects.
        self.PATHS            = PATHS
        self.settings         = settings
        self.objectRepository = objectRepository
        self.executorFactory  = executorFactory

        # --- Pool of skeleton dictionaries to create virtual categories/launchers ---
        self.category_addon_root_dic = {
            'id' : VCATEGORY_ADDONROOT_ID,
            'type' : OBJ_CATEGORY_VIRTUAL,
            'm_name' : 'Root category',
        }

        self.recently_played_roms_dic = {
            'id' : VLAUNCHER_RECENT_ID,
            'type' : OBJ_CATEGORY_VIRTUAL,
            'm_name': 'Recently played',
            'roms_base_noext': 'history',
        }
        self.most_played_roms_dic = {
            'id' : VLAUNCHER_MOST_PLAYED_ID,
            'type' : OBJ_CATEGORY_VIRTUAL,
            'm_name': 'Most played',
            'roms_base_noext': 'most_played',
        }
        self.favourites_roms_dic = {
            'id' : VLAUNCHER_FAVOURITES_ID,
            'type' : OBJ_CATEGORY_VIRTUAL,
            'm_name': 'Favourites',
            'roms_base_noext': 'favourites',
        }

    #
    # Creates an empty Launcher derived object with default values when only the launcher type
    # is available, for example, when creating a new launcher in the context menu.
    #
    def create_new(self, obj_type):
        log_debug('AELObjectFactory::create_new() Creating empty {0}'.format(obj_type))

        return self._load(obj_type)

    #
    # DEPRECATED: this function must be internal callable only.
    # Creates a Launcher derived object when the data dictionary is available.
    # The type of object is the 'type' field in the dictionary.
    #
    def create_from_dic(self, obj_dic):
        id = obj_dic['id']
        obj_type = obj_dic['type']
        log_debug('AELObjectFactory::create_new() Creating {0} ID {1}'.format(obj_type, id))

        return self._load(obj_type, obj_dic)

    #
    # Retrieves a Category object from the database.
    # This method also creates Virtual Category objects.
    # Returns a Category object or None.
    #
    def find_category(self, category_id):
        category_dic = self.objectRepository.find_category(category_id)
        if category_dic is not None:
            category_obj = self._load(OBJ_CATEGORY, category_dic)

        elif category_id == VCATEGORY_ADDONROOT_ID:
            category_obj = self.create_from_dic(self.category_addon_root_dic)

        else:
            category_obj = None

        return category_obj

    #
    # Retrieves a list of Category objects, sorted alphabetically by Name.
    #
    def find_category_all(self):
        category_obj_list = []
        category_dic_list = self.objectRepository.find_category_all()
        # dump_object_to_log('category_dic_list', category_dic_list)
        for category_dic in category_dic_list:
            category_obj_list.append(self._load(OBJ_CATEGORY, category_dic))

        return category_obj_list

    #
    # Retrieves a Launcher object from the database.
    # This method also creates Virtual Launchers (Favourites, ROM Collection, etc.)
    # category_id is not used for Standard Launchers, but is is important for Virtual Launchers.
    # Returns a Launcher object or None.
    #
    def find_launcher(self, category_id, launcher_id):
        launcher_dic = self.objectRepository.find_launcher(launcher_id)
        if launcher_dic is not None:
            category_obj = self._load(launcher_dic['type'], launcher_dic)
        else:
            category_obj = None

        return category_obj

    #
    # Retrieves a list of Launcher objects in a category.
    # This method also works for Virtual Categories (ROM Collections, Browse by Title, etc.)
    #
    def find_launchers_in_cat(self, category_id):
        launcher_obj_list = []
        launcher_dic_list = self.objectRepository.find_launchers_by_category_id(category_id)
        # dump_object_to_log('launcher_dic_list', launcher_dic_list)
        for launcher_dic in launcher_dic_list:
            launcher_obj_list.append(self._load(launcher_dic['type'], launcher_dic))

        return launcher_obj_list

    #
    # To show "Select Launcher type" dialog. Only return real Launcher and not Virtual Launchers.
    #
    def get_launcher_types_odict(self):
        typeOptions = collections.OrderedDict()
        typeOptions[OBJ_LAUNCHER_STANDALONE]      = 'Standalone launcher (Game/Application)'
        typeOptions[OBJ_LAUNCHER_ROM]             = 'ROM launcher (Emulator)'
        typeOptions[OBJ_LAUNCHER_RETROPLAYER]     = 'ROM launcher (Kodi Retroplayer)'
        typeOptions[OBJ_LAUNCHER_RETROARCH]       = 'ROM launcher (Retroarch)'
        if is_windows():
            typeOptions[OBJ_LAUNCHER_LNK]         = 'LNK launcher (Windows only)'
        typeOptions[OBJ_LAUNCHER_NVGAMESTREAM]    = 'Nvidia GameStream'
        if not is_android():
            typeOptions[OBJ_LAUNCHER_STEAM]       = 'Steam launcher'
        # --- Disabled. AEL must not access favourites.xml ---
        # typeOptions[OBJ_LAUNCHER_KODI_FAVOURITES] = 'Kodi favourite launcher'

        return typeOptions

    #
    # obj_type is mandatory.
    # obj_dic may be a dictionary (database objects) or None (new objest).
    # Object constructor is responsible for filling the database dictionary with sensible
    # defaults if obj_dic = None.
    # ROM objects are created by Launcher objects and NOT here.
    #
    def _load(self, obj_type, obj_dic = None):
        # --- Categories ---
        if obj_type == OBJ_CATEGORY:
            return Category(self.PATHS, self.settings, obj_dic, self.objectRepository)

        elif obj_type == OBJ_CATEGORY_VIRTUAL:
            return VirtualCategory(self.PATHS, self.settings, obj_dic, self.objectRepository)

        # --- Virtual launchers ---
        elif obj_type == VLAUNCHER_RECENT_ID:
            return VirtualLauncher(
                self.recently_played_roms_dic, self.settings, ROMSetRepository(self.plugin_data_dir)
            )

        elif obj_type == VLAUNCHER_MOST_PLAYED_ID:
            return VirtualLauncher(
                self.most_played_roms_dic, self.settings, ROMSetRepository(self.plugin_data_dir)
            )

        elif obj_type == VLAUNCHER_FAVOURITES_ID:
            return VirtualLauncher(
                self.favourites_roms_dic, self.settings, ROMSetRepository(self.plugin_data_dir)
            )

        # --- Real launchers ---
        elif obj_type == OBJ_LAUNCHER_STANDALONE:
            return StandaloneLauncher(self.PATHS, self.settings, obj_dic, self.objectRepository,
                                      self.executorFactory)

        elif obj_type == OBJ_LAUNCHER_COLLECTION:
            # romset_repository = ROMSetRepository(self.PATHS.COLLECTIONS_FILE_PATH, False)
            ROMRepository = ROMSetRepository(self.PATHS, self.settings)
            statsStrategy = ROMStatisticsStrategy(self.PATHS, self.settings)

            return CollectionLauncher(self.PATHS, self.settings, obj_dic, romset_repository)

        elif obj_type == OBJ_LAUNCHER_ROM:
            ROMRepository = ROMSetRepository(self.PATHS, self.settings)
            statsStrategy = ROMStatisticsStrategy(self.PATHS, self.settings)

            return StandardRomLauncher(self.PATHS, self.settings, obj_dic, self.objectRepository,
                                       self.executorFactory, ROMRepository, statsStrategy)

        elif obj_type == OBJ_LAUNCHER_RETROPLAYER:
            ROMRepository = ROMSetRepository(self.PATHS, self.settings)
            statsStrategy = ROMStatisticsStrategy(self.PATHS, self.settings)

            return RetroplayerLauncher(self.PATHS, self.settings, obj_dic, self.objectRepository,
                                       self.executorFactory, ROMRepository, statsStrategy)

        elif obj_type == OBJ_LAUNCHER_RETROARCH:
            ROMRepository = ROMSetRepository(self.PATHS, self.settings)
            statsStrategy = ROMStatisticsStrategy(self.PATHS, self.settings)

            return RetroarchLauncher(self.PATHS, self.settings, obj_dic, self.objectRepository,
                                     self.executorFactory, ROMRepository, statsStrategy)

        # LNK launchers available only on Windows
        elif obj_type == OBJ_LAUNCHER_LNK:
            ROMRepository = ROMSetRepository(self.PATHS, self.settings)
            statsStrategy = ROMStatisticsStrategy(self.PATHS, self.settings)

            return LnkLauncher(self.PATHS, self.settings, obj_dic, self.objectRepository,
                               self.executorFactory, ROMRepository, statsStrategy)

        elif obj_type == OBJ_LAUNCHER_STEAM:
            ROMRepository = ROMSetRepository(self.PATHS, self.settings)
            statsStrategy = ROMStatisticsStrategy(self.PATHS, self.settings)

            return SteamLauncher(self.PATHS, self.settings, obj_dic, self.objectRepository,
                                 self.executorFactory, ROMRepository, statsStrategy)

        elif obj_type == OBJ_LAUNCHER_NVGAMESTREAM:
            ROMRepository = ROMSetRepository(self.PATHS, self.settings)
            statsStrategy = ROMStatisticsStrategy(self.PATHS, self.settings)

            return NvidiaGameStreamLauncher(self.PATHS, self.settings, obj_dic, self.objectRepository,
                                            self.executorFactory, ROMRepository, statsStrategy)

        # --- Disabled. AEL must not access favourites.xml ---
        # elif obj_type == OBJ_LAUNCHER_KODI_FAVOURITES:
        #     return KodiLauncher(launcher_data, self.settings, self.executorFactory)

        else:
            log_error('Unsupported requested type "{0}"'.format(obj_type))

        return None

# #################################################################################################
# #################################################################################################
# Executors
# #################################################################################################
# #################################################################################################
class ExecutorABC():
    __metaclass__ = abc.ABCMeta

    def __init__(self, logFile):
        self.logFile = logFile

    @abc.abstractmethod
    def execute(self, application, arguments, non_blocking): pass

class XbmcExecutor(ExecutorABC):
    # --- Execute Kodi built-in function under certain conditions ---
    def execute(self, application, arguments, non_blocking):
        xbmc.executebuiltin('XBMC.{0}'.format(arguments))

#
# --- Linux ---
# New in AEL 0.9.7: always close all file descriptions except 0, 1 and 2 on the child
# process. This is to avoid Kodi opens sockets be inherited by the child process. A
# wrapper script may terminate Kodi using JSON RPC and if file descriptors are not
# closed Kodi will complain that the remote interfacte cannot be initialised. I believe
# the cause is that the socket is kept open by the wrapper script.
#
class LinuxExecutor(ExecutorABC):
    def __init__(self, logFile, lirc_state):
        self.lirc_state = lirc_state
        super(LinuxExecutor, self).__init__(logFile)

    def execute(self, application, arguments, non_blocking):
        log_debug('LinuxExecutor::execute() Starting ...')
        arg_list  = shlex.split(arguments, posix = True)
        command = [application.getPath()] + arg_list

        # >> Old way of launching child process. os.system() is deprecated and should not
        # >> be used anymore.
        # os.system('"{0}" {1}'.format(application, arguments).encode('utf-8'))

         # >> New way of launching, uses subproces module. Also, save child process stdout.
        if non_blocking:
            # >> In a non-blocking launch stdout/stderr of child process cannot be recorded.
            log_info('Launching non-blocking process subprocess.Popen()')
            p = subprocess.Popen(command, close_fds = True)
        else:
            if self.lirc_state: xbmc.executebuiltin('LIRC.stop')
            with open(self.logFile.getPath(), 'w') as f:
                retcode = subprocess.call(
                    command, stdout = f, stderr = subprocess.STDOUT, close_fds = True)
            log_info('Process retcode = {0}'.format(retcode))
            if self.lirc_state: xbmc.executebuiltin('LIRC.start')
        log_debug('LinuxExecutor::execute() function ENDS')

class AndroidExecutor(ExecutorABC):
    def __init__(self):
        super(AndroidExecutor, self).__init__(None)

    def execute(self, application, arguments, non_blocking):
        log_debug('AndroidExecutor::execute() Starting ...')
        retcode = os.system("{0} {1}".format(application.getPath(), arguments).encode('utf-8'))
        log_info('Process retcode = {0}'.format(retcode))
        log_debug('AndroidExecutor::execute() function ENDS')

class OSXExecutor(ExecutorABC):
    def execute(self, application, arguments, non_blocking):
        log_debug('OSXExecutor::execute() Starting ...')
        arg_list  = shlex.split(arguments, posix = True)
        command = [application.getPath()] + arg_list

        # >> Old way.
        # os.system('"{0}" {1}'.format(application, arguments).encode('utf-8'))

        # >> New way.
        with open(self.logFile.getPath(), 'w') as f:
            retcode = subprocess.call(command, stdout = f, stderr = subprocess.STDOUT)
        log_info('Process retcode = {0}'.format(retcode))
        log_debug('OSXExecutor::execute() function ENDS')

class WindowsLnkFileExecutor(ExecutorABC):
    def execute(self, application, arguments, non_blocking):
        log_debug('WindowsLnkFileExecutor::execute() Starting ...')
        log_debug('Launching LNK application')
        # os.system('start "AEL" /b "{0}"'.format(application).encode('utf-8'))
        retcode = subprocess.call('start "AEL" /b "{0}"'.format(application.getPath()).encode('utf-8'), shell = True)
        log_info('LNK app retcode = {0}'.format(retcode))
        log_debug('WindowsLnkFileExecutor::execute() function ENDS')

#
# CMD/BAT files in Windows
#
class WindowsBatchFileExecutor(ExecutorABC):
    def __init__(self, logFile, show_batch_window):
        self.show_batch_window = show_batch_window
        super(WindowsBatchFileExecutor, self).__init__(logFile)

    def execute(self, application, arguments, non_blocking):
        log_debug('WindowsBatchFileExecutor::execute() Starting ...')
        arg_list  = shlex.split(arguments, posix = True)
        command = [application.getPath()] + arg_list
        apppath = application.getDir()
        
        # --- Workaround to run UNC paths in Windows ---
        # >> Retroarch now support ROMs in UNC paths (Samba remotes)
        new_command = list(command)
        for i, _ in enumerate(command):
            if command[i][0] == '\\':
                new_command[i] = '\\' + command[i]
                log_debug('Executor (Windows BatchFile): Before arg #{0} = "{1}"'.format(i, command[i]))
                log_debug('Executor (Windows BatchFile): Now    arg #{0} = "{1}"'.format(i, new_command[i]))
        command = list(new_command)
        log_debug('Executor (Windows BatchFile): command = {0}'.format(command))
        
        log_debug('Executor (Windows BatchFile) Launching BAT application')
        log_debug('Executor (Windows BatchFile) Ignoring setting windows_cd_apppath')
        log_debug('Executor (Windows BatchFile) Ignoring setting windows_close_fds')
        log_debug('Executor (Windows BatchFile) show_batch_window = {0}'.format(self.show_batch_window))
        info = subprocess.STARTUPINFO()
        info.dwFlags = 1
        info.wShowWindow = 5 if self.show_batch_window else 0
        retcode = subprocess.call(command, cwd = apppath.encode('utf-8'), close_fds = True, startupinfo = info)
        log_info('Executor (Windows BatchFile) Process BAR retcode = {0}'.format(retcode))
        log_debug('WindowsBatchFileExecutor::execute() function ENDS')

#
# --- Windoze ---
# NOTE subprocess24_hack.py was hacked to always set CreateProcess() bInheritHandles to 0.
# bInheritHandles [in] If this parameter TRUE, each inheritable handle in the calling 
# process is inherited by the new process. If the parameter is FALSE, the handles are not 
# inherited. Note that inherited handles have the same value and access rights as the original handles.
# See https://msdn.microsoft.com/en-us/library/windows/desktop/ms682425(v=vs.85).aspx
#
# Same behaviour can be achieved in current version of subprocess with close_fds.
# If close_fds is true, all file descriptors except 0, 1 and 2 will be closed before the 
# child process is executed. (Unix only). Or, on Windows, if close_fds is true then no handles 
# will be inherited by the child process. Note that on Windows, you cannot set close_fds to 
# true and also redirect the standard handles by setting stdin, stdout or stderr.
#
# If I keep old launcher behaviour in Windows (close_fds = True) then program output cannot
# be redirected to a file.
#
class WindowsExecutor(ExecutorABC):
    def __init__(self, logFile, cd_apppath, close_fds):
        self.windows_cd_apppath = cd_apppath
        self.windows_close_fds  = close_fds
        super(WindowsExecutor, self).__init__(logFile)

    def execute(self, application, arguments, non_blocking):
        log_debug('WindowsExecutor::execute() Starting ...')
        arg_list  = shlex.split(arguments, posix = True)
        command = [application.getPath()] + arg_list
        apppath = application.getDir()

        # --- Workaround to run UNC paths in Windows ---
        # >> Retroarch now support ROMs in UNC paths (Samba remotes)
        new_command = list(command)
        for i, _ in enumerate(command):
            if command[i][0] == '\\':
                new_command[i] = '\\' + command[i]
                log_debug('WindowsExecutor: Before arg #{0} = "{1}"'.format(i, command[i]))
                log_debug('WindowsExecutor: Now    arg #{0} = "{1}"'.format(i, new_command[i]))
        command = list(new_command)
        log_debug('WindowsExecutor: command = {0}'.format(command))

        # >> cwd = apppath.encode('utf-8') fails if application path has Unicode on Windows
        # >> A workaraound is to use cwd = apppath.encode(sys.getfilesystemencoding()) --> DOES NOT WORK
        # >> For the moment AEL cannot launch executables on Windows having Unicode paths.
        log_debug('Launching regular application')
        log_debug('windows_cd_apppath = {0}'.format(self.windows_cd_apppath))
        log_debug('windows_close_fds  = {0}'.format(self.windows_close_fds))

        # >> Note that on Windows, you cannot set close_fds to true and also redirect the 
        # >> standard handles by setting stdin, stdout or stderr.
        if self.windows_cd_apppath and self.windows_close_fds:
            retcode = subprocess.call(command, cwd = apppath.encode('utf-8'), close_fds = True)
        elif self.windows_cd_apppath and not self.windows_close_fds:
            with open(self.logFile.getPath(), 'w') as f:
                retcode = subprocess.call(command, cwd = apppath.encode('utf-8'), close_fds = False,
                                            stdout = f, stderr = subprocess.STDOUT)
        elif not self.windows_cd_apppath and self.windows_close_fds:
            retcode = subprocess.call(command, close_fds = True)
        elif not self.windows_cd_apppath and not self.windows_close_fds:
            with open(self.logFile.getPath(), 'w') as f:
                retcode = subprocess.call(command, close_fds = False, stdout = f, stderr = subprocess.STDOUT)
        else:
            raise AddonError('Logical error')
        log_info('Process retcode = {0}'.format(retcode))
        log_debug('WindowsExecutor::execute() function ENDS')

class WebBrowserExecutor(ExecutorABC):
    def execute(self, application, arguments, non_blocking):
        log_debug('WebBrowserExecutor::execute() Starting ...')
        command = application.getPath() + arguments
        log_debug('Launching URL "{0}"'.format(command))
        webbrowser.open(command)
        log_debug('WebBrowserExecutor::execute() function ENDS')

# -------------------------------------------------------------------------------------------------
# Abstract Factory Pattern
# See https://www.oreilly.com/library/view/head-first-design/0596007124/ch04.html
# -------------------------------------------------------------------------------------------------
class ExecutorFactory(object):
    def __init__(self, g_PATHS, settings):
        self.settings = settings
        self.logFile  = g_PATHS.LAUNCHER_REPORT_FILE_PATH

    def create_from_pathstring(self, application_string):
        return self.create(FileName(application_string))

    def create(self, application):
        if application.getBase().lower().replace('.exe' , '') == 'xbmc' \
            or 'xbmc-fav-' in application.getPath() or 'xbmc-sea-' in application.getPath():
            return XbmcExecutor(self.logFile)

        elif re.search('.*://.*', application.getPath()):
            return WebBrowserExecutor(self.logFile)

        elif is_windows():
            # >> BAT/CMD file.
            if application.getExt().lower() == '.bat' or application.getExt().lower() == '.cmd' :
                return WindowsBatchFileExecutor(self.logFile, self.settings['show_batch_window'])
            # >> Standalone launcher where application is a LNK file
            elif application.getExt().lower() == '.lnk': 
                return WindowsLnkFileExecutor(self.logFile)

            # >> Standard Windows executor
            return WindowsExecutor(self.logFile,
                self.settings['windows_cd_apppath'], self.settings['windows_close_fds'])

        elif is_android():
            return AndroidExecutor()

        elif is_linux():
            return LinuxExecutor(self.logFile, self.settings['lirc_state'])

        elif is_osx():
            return OSXExecutor(self.logFile)

        else:
            log_error('ExecutorFactory::create() Cannot determine the running platform')
            kodi_notify_warn('Cannot determine the running platform')

        return None

# #################################################################################################
# #################################################################################################
# ROM scanners
# #################################################################################################
# #################################################################################################
class RomScannersFactory(object):
    def __init__(self, PATHS, settings):
        self.settings = settings
        self.reports_dir = PATHS.REPORTS_DIR
        self.addon_dir = PATHS.ADDON_DATA_DIR

    def create(self, launcher, scraping_strategy):
        launcherType = launcher.get_launcher_type()
        log_info('RomScannersFactory: Creating romscanner for {}'.format(launcherType))

        if not launcher.supports_launching_roms():
            return NullScanner(launcher, self.settings)
        
        if launcherType == LAUNCHER_STEAM:
            return SteamScanner(self.reports_dir, self.addon_dir, launcher, self.settings, scraping_strategy)

        if launcherType == LAUNCHER_NVGAMESTREAM:
            return NvidiaStreamScanner(self.reports_dir, self.addon_dir, launcher, romset, self.settings, scraping_strategy)
                
        return RomFolderScanner(self.reports_dir, self.addon_dir, launcher, self.settings, scraping_strategy)

class ScannerStrategyABC(KodiProgressDialogStrategy):
    __metaclass__ = abc.ABCMeta

    def __init__(self, launcher, settings):
        self.launcher = launcher
        self.settings = settings
        super(ScannerStrategy, self).__init__()

    #
    # Scans for new roms based on the type of launcher.
    #
    @abc.abstractmethod
    def scan(self):
        return {}

    #
    # Cleans up ROM collection.
    # Remove Remove dead/missing ROMs ROMs
    #
    @abc.abstractmethod
    def cleanup(self):
        return {}

class NullScanner(ScannerStrategyABC):
    def scan(self):
        return {}

    def cleanup(self):
        return {}

class RomScannerStrategy(ScannerStrategyABC):
    __metaclass__ = abc.ABCMeta

    def __init__(self, reports_dir, addon_dir, launcher, settings, scraping_strategy):
        
        self.reports_dir = reports_dir
        self.addon_dir = addon_dir
                
        self.scraping_strategy = scraping_strategy

        super(RomScannerStrategy, self).__init__(launcher, settings)

    def scan(self):
        
        # --- Open ROM scanner report file ---
        launcher_report = FileReporter(self.reports_dir, self.launcher.get_data(), LogReporter(self.launcher.get_data()))
        launcher_report.open('RomScanner() Starting ROM scanner')

        # >> Check if there is an XML for this launcher. If so, load it.
        # >> If file does not exist or is empty then return an empty dictionary.
        launcher_report.write('Loading launcher ROMs ...')
        roms = self.launcher.get_roms()

        if roms is None:
            roms = []
        
        num_roms = len(roms)
        launcher_report.write('{0} ROMs currently in database'.format(num_roms))
        
        launcher_report.write('Collecting candidates ...')
        candidates = self._getCandidates(launcher_report)
        num_candidates = len(candidates)
        log_info('{0} candidates found'.format(num_candidates))

        launcher_report.write('Removing dead ROMs ...')
        num_removed_roms = self._removeDeadRoms(candidates, roms)        

        if num_removed_roms > 0:
            kodi_notify('{0} dead ROMs removed successfully'.format(num_removed_roms))
            log_info('{0} dead ROMs removed successfully'.format(num_removed_roms))
        else:
            log_info('No dead ROMs found')

        new_roms = self._processFoundItems(candidates, roms, launcher_report)
        
        if not new_roms:
            return None

        num_new_roms = len(new_roms)
        roms = roms + new_roms

        launcher_report.write('******************** ROM scanner finished. Report ********************')
        launcher_report.write('Removed dead ROMs {0:6d}'.format(num_removed_roms))
        launcher_report.write('Files checked     {0:6d}'.format(num_candidates))
        launcher_report.write('New added ROMs    {0:6d}'.format(num_new_roms))
        
        if len(roms) == 0:
            launcher_report.write('WARNING Launcher has no ROMs!')
            launcher_report.close()
            kodi_dialog_OK('No ROMs found! Make sure launcher directory and file extensions are correct.')
            return None
        
        if num_new_roms == 0:
            kodi_notify('Added no new ROMs. Launcher has {0} ROMs'.format(len(roms)))
        else:
            kodi_notify('Added {0} new ROMs'.format(num_new_roms))

        # --- Close ROM scanner report file ---
        launcher_report.write('*** END of the ROM scanner report ***')
        launcher_report.close()

        return roms

    def cleanup(self):
        launcher_report = LogReporter(self.launcher.get_data())
        launcher_report.open('RomScanner() Starting Dead ROM cleaning')
        log_debug('RomScanner() Starting Dead ROM cleaning')

        roms = self.launcher.get_roms()
        if roms is None:
            launcher_report.close()
            log_info('RomScanner() No roms available to cleanup')
            return {}
        
        num_roms = len(roms)
        launcher_report.write('{0} ROMs currently in database'.format(num_roms))
        
        launcher_report.write('Collecting candidates ...')
        candidates = self._getCandidates(launcher_report)
        num_candidates = len(candidates)
        log_info('{0} candidates found'.format(num_candidates))

        launcher_report.write('Removing dead ROMs ...')
        num_removed_roms = self._removeDeadRoms(candidates, roms)        

        if num_removed_roms > 0:
            kodi_notify('{0} dead ROMs removed successfully'.format(num_removed_roms))
            log_info('{0} dead ROMs removed successfully'.format(num_removed_roms))
        else:
            log_info('No dead ROMs found')

        launcher_report.close()
        return roms

    # ~~~ Scan for new files (*.*) and put them in a list ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @abc.abstractmethod
    def _getCandidates(self, launcher_report):
        return []

    # --- Remove dead entries -----------------------------------------------------------------
    @abc.abstractmethod
    def _removeDeadRoms(self, candidates, roms):
        return 0

    # ~~~ Now go processing item by item ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @abc.abstractmethod
    def _processFoundItems(self, items, roms, launcher_report):
        return []

class RomFolderScanner(RomScannerStrategy):
    # ~~~ Scan for new files (*.*) and put them in a list ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _getCandidates(self, launcher_report):
        kodi_busydialog_ON()
        files = []
        launcher_path = self.launcher.get_rom_path()
        launcher_report.write('Scanning files in {0}'.format(launcher_path.getPath()))

        if self.settings['scan_recursive']:
            log_info('Recursive scan activated')
            files = launcher_path.recursiveScanFilesInPath('*.*')
        else:
            log_info('Recursive scan not activated')
            files = launcher_path.scanFilesInPath('*.*')

        kodi_busydialog_OFF()

        num_files = len(files)
        launcher_report.write('  File scanner found {0} files'.format(num_files))

        return files

    # --- Remove dead entries -----------------------------------------------------------------
    def _removeDeadRoms(self, candidates, roms):
        num_roms = len(roms)
        num_removed_roms = 0
        if num_roms == 0:
            log_info('Launcher is empty. No dead ROM check.')
            return num_removed_roms
        
        log_debug('Starting dead items scan')
        i = 0
            
        self._startProgressPhase('Advanced Emulator Launcher', 'Checking for dead ROMs ...')
            
        for rom in reversed(roms):
            fileName = rom.get_file()
            log_debug('Searching {0}'.format(fileName.getPath()))
            self._updateProgress(i * 100 / num_roms)
            
            if not fileName.exists():
                log_debug('Not found')
                log_debug('Deleting from DB {0}'.format(fileName.getPath()))
                roms.remove(rom)
                num_removed_roms += 1
            i += 1
            
        self._endProgressPhase()

        return num_removed_roms

    # ~~~ Now go processing item by item ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _processFoundItems(self, items, roms, launcher_report):

        num_items = len(items)    
        new_roms = []

        self._startProgressPhase('Advanced Emulator Launcher', 'Scanning found items')
        log_debug('============================== Processing ROMs ==============================')
        launcher_report.write('Processing files ...')
        num_items_checked = 0
        
        allowedExtensions = self.launcher.get_rom_extensions()
        launcher_multidisc = self.launcher.supports_multidisc()

        for item in sorted(items):
            self._updateProgress(num_items_checked * 100 / num_items)
            
            # --- Get all file name combinations ---
            ROM = FileName(item)
            launcher_report.write('>>> {0}'.format(ROM.getPath()).encode('utf-8'))

            # ~~~ Update progress dialog ~~~
            file_text = 'ROM {0}'.format(ROM.getBase())
            self._updateProgressMessage(file_text, 'Checking if has ROM extension ...')
                        
            # --- Check if filename matchs ROM extensions ---
            # The recursive scan has scanned all files. Check if this file matches some of 
            # the ROM extensions. If this file isn't a ROM skip it and go for next one in the list.
            processROM = False

            for ext in allowedExtensions:
                if ROM.getExt() == '.' + ext:
                    launcher_report.write("  Expected '{0}' extension detected".format(ext))
                    processROM = True
                    break

            if not processROM: 
                launcher_report.write('  File has not an expected extension. Skipping file.')
                continue
                        
            # --- Check if ROM belongs to a multidisc set ---
            self._updateProgressMessage(file_text, 'Checking if ROM belongs to multidisc set..')
                       
            MultiDiscInROMs = False
            MDSet = text_get_multidisc_info(ROM)
            if MDSet.isMultiDisc and launcher_multidisc:
                log_info('ROM belongs to a multidisc set.')
                log_info('isMultiDisc "{0}"'.format(MDSet.isMultiDisc))
                log_info('setName     "{0}"'.format(MDSet.setName))
                log_info('discName    "{0}"'.format(MDSet.discName))
                log_info('extension   "{0}"'.format(MDSet.extension))
                log_info('order       "{0}"'.format(MDSet.order))
                launcher_report.write('  ROM belongs to a multidisc set.')
                
                # >> Check if the set is already in launcher ROMs.
                MultiDisc_rom_id = None
                for new_rom in new_roms:
                    temp_FN = new_rom.get_file()
                    if temp_FN.getBase() == MDSet.setName:
                        MultiDiscInROMs  = True
                        MultiDisc_rom    = new_rom
                        break

                log_info('MultiDiscInROMs is {0}'.format(MultiDiscInROMs))

                # >> If the set is not in the ROMs then this ROM is the first of the set.
                # >> Add the set
                if not MultiDiscInROMs:
                    log_info('First ROM in the set. Adding to ROMs ...')
                    # >> Manipulate ROM so filename is the name of the set
                    ROM_dir = FileName(ROM.getDir())
                    ROM_temp = ROM_dir.pjoin(MDSet.setName)
                    log_info('ROM_temp OP "{0}"'.format(ROM_temp.getPath()))
                    log_info('ROM_temp  P "{0}"'.format(ROM_temp.getPath()))
                    ROM = ROM_temp
                # >> If set already in ROMs, just add this disk into the set disks field.
                else:
                    log_info('Adding additional disk "{0}"'.format(MDSet.discName))
                    MultiDisc_rom.add_disk(MDSet.discName)
                    # >> Reorder disks like Disk 1, Disk 2, ...
                    
                    # >> Process next file
                    log_info('Processing next file ...')
                    continue
            elif MDSet.isMultiDisc and not launcher_multidisc:
                launcher_report.write('  ROM belongs to a multidisc set but Multidisc support is disabled.')
            else:
                launcher_report.write('  ROM does not belong to a multidisc set.')
 
            # --- Check that ROM is not already in the list of ROMs ---
            # >> If file already in ROM list skip it
            self._updateProgressMessage(file_text, 'Checking if ROM is not already in collection...')
            repeatedROM = False
            for rom in roms:
                rpath = rom.get_filename() 
                if rpath == item: 
                    repeatedROM = True
        
            if repeatedROM:
                launcher_report.write('  File already into launcher ROM list. Skipping file.')
                continue
            else:
                launcher_report.write('  File not in launcher ROM list. Processing it ...')

            # --- Ignore BIOS ROMs ---
            # Name of bios is: '[BIOS] Rom name example (Rev A).zip'
            if self.settings['scan_ignore_bios']:
                BIOS_re = re.findall('\[BIOS\]', ROM.getBase())
                if len(BIOS_re) > 0:
                    log_info("BIOS detected. Skipping ROM '{0}'".format(ROM.path))
                    continue

            # ~~~~~ Process new ROM and add to the list ~~~~~
            # --- Create new rom dictionary ---
            # >> Database always stores the original (non transformed/manipulated) path
            new_rom = Rom()
            new_rom.set_file(ROM)

            searchTerm = text_format_ROM_name_for_scraping(ROM.getBase_noext())
            self._updateProgressMessage(steamGame['name'], 'Scraping {0}...'.format(ROM.getBase_noext()))
            self.scraping_strategy.scrape(searchTerm, ROM, new_rom)
            # !!!! MOVED CODE BELOW TO SCRAPING_STRATEGY UNTILL PROPERLY MERGED !!!
            #
            #if self.scrapers:
            #    for scraper in self.scrapers:
            #        self._updateProgressMessage(file_text, 'Scraping {0}...'.format(scraper.getName()))
            #        scraper.scrape(searchTerm, ROM, new_rom)
            #
            #romdata = new_rom.get_data()
            #log_verb('Set Title     file "{0}"'.format(romdata['s_title']))
            #log_verb('Set Snap      file "{0}"'.format(romdata['s_snap']))
            #log_verb('Set Boxfront  file "{0}"'.format(romdata['s_boxfront']))
            #log_verb('Set Boxback   file "{0}"'.format(romdata['s_boxback']))
            #log_verb('Set Cartridge file "{0}"'.format(romdata['s_cartridge']))
            #log_verb('Set Fanart    file "{0}"'.format(romdata['s_fanart']))
            #log_verb('Set Banner    file "{0}"'.format(romdata['s_banner']))
            #log_verb('Set Clearlogo file "{0}"'.format(romdata['s_clearlogo']))
            #log_verb('Set Flyer     file "{0}"'.format(romdata['s_flyer']))
            #log_verb('Set Map       file "{0}"'.format(romdata['s_map']))
            #log_verb('Set Manual    file "{0}"'.format(romdata['s_manual']))
            #log_verb('Set Trailer   file "{0}"'.format(romdata['s_trailer']))
            
            # --- This was the first ROM in a multidisc set ---
            if launcher_multidisc and MDSet.isMultiDisc and not MultiDiscInROMs:
                log_info('Adding to ROMs dic first disk "{0}"'.format(MDSet.discName))
                new_rom.add_disk(MDSet.discName)
            
            new_roms.append(new_rom)
            
            # ~~~ Check if user pressed the cancel button ~~~
            if self._isProgressCanceled():
                self._endProgressPhase()
                kodi_dialog_OK('Stopping ROM scanning. No changes have been made.')
                log_info('User pressed Cancel button when scanning ROMs. ROM scanning stopped.')
                return None
            
            num_items_checked += 1
           
        self._endProgressPhase()
        return new_roms

class SteamScanner(RomScannerStrategy):
    
    # ~~~ Scan for new items not yet in the rom collection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _getCandidates(self, launcher_report):
               
        log_debug('Reading Steam account')
        self._startProgressPhase('Advanced Emulator Launcher', 'Reading Steam account...')

        apikey = self.settings['steam-api-key']
        steamid = self.launcher.get_steam_id()
        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={}&steamid={}&include_appinfo=1'.format(apikey, steamid)
        
        self._updateProgress(70)
        body = net_get_URL_original(url)
        self._updateProgress(80)
        
        steamJson = json.loads(body)
        games = steamJson['response']['games']
        
        self._endProgressPhase()
        return games

    # --- Remove dead entries -----------------------------------------------------------------
    def _removeDeadRoms(self, candidates, roms):
    
        if roms is None or len(roms) == 0:
            log_info('Launcher is empty. No dead ROM check.')
            return 0

        log_debug('Starting dead items scan')
        num_roms = len(roms)
        num_removed_roms = 0
        i = 0
            
        self._startProgressPhase('Advanced Emulator Launcher', 'Checking for dead ROMs ...')
        
        steamGameIds = set(steamGame['appid'] for steamGame in candidates)

        for rom in reversed(roms):
            romSteamId = rom.get_custom_attribute('steamid')
            
            log_debug('Searching {0}'.format(romSteamId))
            self._updateProgress(i * 100 / num_roms)
            i += 1

            if romSteamId not in steamGameIds:
                log_debug('Not found. Deleting from DB {0}'.format(rom.get_name()))
                roms.remove(rom)
                num_removed_roms += 1
            
        self._endProgressPhase()

        return num_removed_roms

    def _processFoundItems(self, items, roms, launcher_report):
        
        if items is None or len(items) == 0:
            log_info('No steam games available.')
            return []

        new_roms = []

        num_games = len(items)
        num_items_checked = 0
            
        self._startProgressPhase('Advanced Emulator Launcher', 'Checking for new ROMs ...')
        steamIdsAlreadyInCollection = set(rom.get_custom_attribute('steamid') for rom in roms)
        
        for steamGame in items:
            
            steamId = steamGame['appid']
            log_debug('Searching {} with #{}'.format(steamGame['name'], steamId))

            self._updateProgress(num_items_checked * 100 / num_games, steamGame['name'])
            
            if steamId not in steamIdsAlreadyInCollection:
                
                log_debug('========== Processing Steam game ==========')
                launcher_report.write('>>> title: {0}'.format(steamGame['name']))
                launcher_report.write('>>> ID: {0}'.format(steamGame['appid']))
        
                log_debug('Not found. Item {0} is new'.format(steamGame['name']))

                launcher_path = self.launcher.get_rom_path()
                romPath = launcher_path.pjoin('{0}.rom'.format(steamGame['appid']))

                # ~~~~~ Process new ROM and add to the list ~~~~~
                # --- Create new rom dictionary ---
                # >> Database always stores the original (non transformed/manipulated) path
                new_rom  = Rom()
                new_rom.set_file(romPath)

                new_rom.set_custom_attribute('steamid', steamGame['appid'])
                new_rom.set_custom_attribute('steam_name', steamGame['name'])  # so that we always have the original name
                new_rom.set_name(steamGame['name'])

                searchTerm = steamGame['name']
                
                self._updateProgressMessage(steamGame['name'], 'Scraping {0}...'.format(steamGame['name']))
                self.scraping_strategy.scrape(searchTerm, romPath, new_rom)
                # !!!! MOVED CODE BELOW TO SCRAPING_STRATEGY UNTILL PROPERLY MERGED !!!
                #if self.scrapers:
                #    for scraper in self.scrapers:
                #        self._updateProgressMessage(steamGame['name'], 'Scraping {0}...'.format(scraper.getName()))
                #        scraper.scrape(searchTerm, romPath, new_rom)
                #
                #romdata = new_rom.get_data()
                #log_verb('Set Title     file "{0}"'.format(romdata['s_title']))
                #log_verb('Set Snap      file "{0}"'.format(romdata['s_snap']))
                #log_verb('Set Boxfront  file "{0}"'.format(romdata['s_boxfront']))
                #log_verb('Set Boxback   file "{0}"'.format(romdata['s_boxback']))
                #log_verb('Set Cartridge file "{0}"'.format(romdata['s_cartridge']))
                #log_verb('Set Fanart    file "{0}"'.format(romdata['s_fanart']))
                #log_verb('Set Banner    file "{0}"'.format(romdata['s_banner']))
                #log_verb('Set Clearlogo file "{0}"'.format(romdata['s_clearlogo']))
                #log_verb('Set Flyer     file "{0}"'.format(romdata['s_flyer']))
                #log_verb('Set Map       file "{0}"'.format(romdata['s_map']))
                #log_verb('Set Manual    file "{0}"'.format(romdata['s_manual']))
                #log_verb('Set Trailer   file "{0}"'.format(romdata['s_trailer']))
            
                new_roms.append(new_rom)
                            
                # ~~~ Check if user pressed the cancel button ~~~
                if self._isProgressCanceled():
                    self._endProgressPhase()
                    kodi_dialog_OK('Stopping ROM scanning. No changes have been made.')
                    log_info('User pressed Cancel button when scanning ROMs. ROM scanning stopped.')
                    return None
            
                num_items_checked += 1

        self._endProgressPhase()    
        return new_roms

class NvidiaStreamScanner(RomScannerStrategy):

    # ~~~ Scan for new items not yet in the rom collection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _getCandidates(self, launcher_report):
        from gamestream import GameStreamServer

        log_debug('Reading Nvidia GameStream server')
        self._startProgressPhase('Advanced Emulator Launcher', 'Reading Nvidia GameStream server...')

        server_host = self.launcher.get_server()
        certificates_path = self.launcher.get_certificates_path()

        streamServer = GameStreamServer(server_host, certificates_path)
        connected = streamServer.connect()

        if not connected:
            kodi_notify_error('Unable to connect to gamestream server')
            return None

        self._updateProgress(50)
        games = streamServer.getApps()
                
        self._endProgressPhase()
        return games

    # --- Remove dead entries -----------------------------------------------------------------
    def _removeDeadRoms(self, candidates, roms):
    
        if roms is None or len(roms) == 0:
            log_info('Launcher is empty. No dead ROM check.')
            return 0

        log_debug('Starting dead items scan')
        num_roms = len(roms)
        num_removed_roms = 0
        i = 0
            
        self._startProgressPhase('Advanced Emulator Launcher', 'Checking for dead ROMs ...')
        
        streamIds = set(streamableGame['ID'] for streamableGame in candidates)

        for rom in reversed(roms):
            romStreamId = rom.get_custom_attribute('streamid')
            
            log_debug('Searching {0}'.format(romStreamId))
            self._updateProgress(i * 100 / num_roms)
            i += 1

            if romStreamId not in streamIds:
                log_debug('Not found. Deleting from DB {0}'.format(rom.get_name()))
                roms.remove(rom)
                num_removed_roms += 1
            
        self._endProgressPhase()

        return num_removed_roms

    def _processFoundItems(self, items, roms, launcher_report):
        if items is None or len(items) == 0:
            log_info('No Nvidia Gamestream games available.')
            return []

        new_roms = []

        num_games = len(items)
        num_items_checked = 0
            
        self._startProgressPhase('Advanced Emulator Launcher', 'Checking for new ROMs ...')
        streamIdsAlreadyInCollection = set(rom.get_custom_attribute('streamid') for rom in roms)
        
        for streamableGame in items:
            
            streamId = streamableGame['ID']
            log_debug('Searching {} with #{}'.format(streamableGame['AppTitle'], streamId))

            self._updateProgress(num_items_checked * 100 / num_games, streamableGame['AppTitle'])
            
            if streamId not in streamIdsAlreadyInCollection:
                
                log_debug('========== Processing Nvidia Gamestream game ==========')
                launcher_report.write('>>> title: {0}'.format(streamableGame['AppTitle']))
                launcher_report.write('>>> ID: {0}'.format(streamableGame['ID']))
        
                log_debug('Not found. Item {0} is new'.format(streamableGame['AppTitle']))

                launcher_path = launcher.get_rom_path()
                romPath = launcher_path.pjoin('{0}.rom'.format(streamableGame['ID']))

                # ~~~~~ Process new ROM and add to the list ~~~~~
                # --- Create new rom dictionary ---
                # >> Database always stores the original (non transformed/manipulated) path
                new_rom  = Rom()
                new_rom.set_file(romPath)

                new_rom.set_custom_attribute('streamid',        streamableGame['ID'])
                new_rom.set_custom_attribute('gamestream_name', streamableGame['AppTitle'])  # so that we always have the original name
                new_rom.set_name(streamableGame['AppTitle'])
                
                searchTerm = streamableGame['AppTitle']
                
                self._updateProgressMessage(steamGame['name'], 'Scraping {0}...'.format(streamableGame['AppTitle']))
                self.scraping_strategy.scrape(searchTerm, romPath, new_rom)
                #if self.scrapers:
                #    for scraper in self.scrapers:
                #        self._updateProgressMessage(streamableGame['AppTitle'], 'Scraping {0}...'.format(scraper.getName()))
                #        scraper.scrape(searchTerm, romPath, new_rom)
                #
                #romdata = new_rom.get_data()
                #log_verb('Set Title     file "{0}"'.format(romdata['s_title']))
                #log_verb('Set Snap      file "{0}"'.format(romdata['s_snap']))
                #log_verb('Set Boxfront  file "{0}"'.format(romdata['s_boxfront']))
                #log_verb('Set Boxback   file "{0}"'.format(romdata['s_boxback']))
                #log_verb('Set Cartridge file "{0}"'.format(romdata['s_cartridge']))
                #log_verb('Set Fanart    file "{0}"'.format(romdata['s_fanart']))
                #log_verb('Set Banner    file "{0}"'.format(romdata['s_banner']))
                #log_verb('Set Clearlogo file "{0}"'.format(romdata['s_clearlogo']))
                #log_verb('Set Flyer     file "{0}"'.format(romdata['s_flyer']))
                #log_verb('Set Map       file "{0}"'.format(romdata['s_map']))
                #log_verb('Set Manual    file "{0}"'.format(romdata['s_manual']))
                #log_verb('Set Trailer   file "{0}"'.format(romdata['s_trailer']))
            
                new_roms.append(new_rom)
                            
                # ~~~ Check if user pressed the cancel button ~~~
                if self._isProgressCanceled():
                    self._endProgressPhase()
                    kodi_dialog_OK('Stopping ROM scanning. No changes have been made.')
                    log_info('User pressed Cancel button when scanning ROMs. ROM scanning stopped.')
                    return None
            
                num_items_checked += 1

        self._endProgressPhase()
        return new_roms

# #################################################################################################
# #################################################################################################
# DAT files and ROM audit
# #################################################################################################
# #################################################################################################
class RomDatFileScanner(KodiProgressDialogStrategy):
    def __init__(self, settings):
        self.settings = settings
        super(RomDatFileScanner, self).__init__()

    #
    # Helper function to update ROMs No-Intro status if user configured a No-Intro DAT file.
    # Dictionaries are mutable, so roms can be changed because passed by assigment.
    # This function also creates the Parent/Clone indices:
    #   1) ADDON_DATA_DIR/db_ROMs/roms_base_noext_PClone_index.json
    #   2) ADDON_DATA_DIR/db_ROMs/roms_base_noext_parents.json
    #
    # A) If there are Unkown ROMs, a fake rom with name [Unknown ROMs] and id UNKNOWN_ROMS_PARENT_ID
    #    is created. This fake ROM is the parent of all Unknown ROMs.
    #    This fake ROM is added to roms_base_noext_parents.json database.
    #    This fake ROM is not present in the main JSON ROM database.
    # 
    # Returns:
    #   True  -> ROM audit was OK
    #   False -> There was a problem with the audit.
    #
    #def _roms_update_NoIntro_status(self, roms, nointro_xml_file_FileName):
    def update_roms_NoIntro_status(self, launcher, roms):
        __debug_progress_dialogs = False
        __debug_time_step = 0.0005

        # --- Reset the No-Intro status and removed No-Intro missing ROMs ---
        audit_have = audit_miss = audit_unknown = 0
        self._startProgressPhase('Advanced Emulator Launcher', 'Deleting Missing/Dead ROMs and clearing flags ...')
        self.roms_reset_NoIntro_status(launcher, roms)
        self._updateProgress(100)
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Check if DAT file exists ---
        nointro_xml_file_FileName = launcher.get_nointro_xml_filepath()
        if not nointro_xml_file_FileName.exists():
            log_warning('_roms_update_NoIntro_status() Not found {0}'.format(nointro_xml_file_FileName.getPath()))
            return False
        
        self._updateProgress(0, 'Loading No-Intro/Redump XML DAT file ...')
        roms_nointro = audit_load_NoIntro_XML_file(nointro_xml_file_FileName)
        self._updateProgress(100)

        if __debug_progress_dialogs: time.sleep(0.5)
        if not roms_nointro:
            log_warning('_roms_update_NoIntro_status() Error loading {0}'.format(nointro_xml_file_FileName.getPath()))
            return False

        # --- Remove BIOSes from No-Intro ROMs ---
        if self.settings['scan_ignore_bios']:
            log_info('_roms_update_NoIntro_status() Removing BIOSes from No-Intro ROMs ...')
            self._updateProgress(0, 'Removing BIOSes from No-Intro ROMs ...')
            num_items = len(roms_nointro)
            item_counter = 0
            filtered_roms_nointro = {}
            for rom_id in roms_nointro:
                rom_data = roms_nointro[rom_id]
                BIOS_str_list = re.findall('\[BIOS\]', rom_data['name'])
                if not BIOS_str_list:
                    filtered_roms_nointro[rom_id] = rom_data
                else:
                    log_debug('_roms_update_NoIntro_status() Removed BIOS "{0}"'.format(rom_data['name']))
                item_counter += 1
                self._updateProgress((item_counter*100)/num_items)
                if __debug_progress_dialogs: time.sleep(__debug_time_step)
            roms_nointro = filtered_roms_nointro
            self._updateProgress(100)
        else:
            log_info('_roms_update_NoIntro_status() User wants to include BIOSes.')

        # --- Put No-Intro ROM names in a set ---
        # >> Set is the fastest Python container for searching elements (implements hashed search).
        # >> No-Intro names include tags
        self._updateProgress(0, 'Creating No-Intro and ROM sets ...')
        roms_nointro_set = set(roms_nointro.keys())
        roms_set = set()
        for rom in roms:
            # >> Use the ROM basename.
            ROMFileName = rom.get_file()
            roms_set.add(ROMFileName.getBase_noext())
        self._updateProgress(100)
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Traverse Launcher ROMs and check if they are in the No-Intro ROMs list ---
        self._updateProgress(0, 'Audit Step 1/4: Checking Have and Unknown ROMs ...')
        num_items = len(roms)
        item_counter = 0
        for rom in roms:
            ROMFileName = rom.get_file()
            if ROMFileName.getBase_noext() in roms_nointro_set:
                rom.set_nointro_status(NOINTRO_STATUS_HAVE)
                audit_have += 1
                log_debug('_roms_update_NoIntro_status() HAVE    "{0}"'.format(ROMFileName.getBase_noext()))
            else:
                rom.set_nointro_status(NOINTRO_STATUS_UNKNOWN)
                audit_unknown += 1
                log_debug('_roms_update_NoIntro_status() UNKNOWN "{0}"'.format(ROMFileName.getBase_noext()))
            item_counter += 1
            self._updateProgress((item_counter*100)/num_items)
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
        self._updateProgress(100)

        # --- Mark Launcher dead ROMs as missing ---
        self._updateProgress(0, 'Audit Step 2/4: Checking Missing ROMs ...')
        num_items = len(roms)
        item_counter = 0
        for rom in roms:
            ROMFileName = rom.get_file()
            if not ROMFileName.exists():
                rom.set_nointro_status(NOINTRO_STATUS_MISS)
                audit_miss += 1
                log_debug('_roms_update_NoIntro_status() MISSING "{0}"'.format(ROMFileName.getBase_noext()))
            item_counter += 1
            self._updateProgress((item_counter*100)/num_items)
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
        self._updateProgress(100)

        # --- Now add missing ROMs to Launcher ---
        # >> Traverse the No-Intro set and add the No-Intro ROM if it's not in the Launcher
        # >> Added/Missing ROMs have their own romID.
        self._updateProgress(0, 'Audit Step 3/4: Adding Missing ROMs ...')
        num_items = len(roms_nointro_set)
        item_counter = 0
        ROMPath = launcher.get_rom_path()
        for nointro_rom in sorted(roms_nointro_set):
            # log_debug('_roms_update_NoIntro_status() Checking "{0}"'.format(nointro_rom))
            if nointro_rom not in roms_set:
                # Add new "fake" missing ROM. This ROM cannot be launched!
                # Added ROMs have special extension .nointro
                rom = Rom()
                rom.set_file(ROMPath.pjoin(nointro_rom + '.nointro'))
                rom.set_name(nointro_rom)
                rom.set_nointro_status(NOINTRO_STATUS_MISS)
                roms.append(rom)
                audit_miss += 1
                log_debug('_roms_update_NoIntro_status() ADDED   "{0}"'.format(rom.get_name()))
                # log_debug('_roms_update_NoIntro_status()    OP   "{0}"'.format(rom['filename']))
            item_counter += 1
            self._updateProgress((item_counter*100)/num_items)
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
        self._updateProgress(100)

        # --- Detect if the DAT file has PClone information or not ---
        dat_pclone_dic = audit_make_NoIntro_PClone_dic(roms_nointro)
        num_dat_clones = 0
        for parent_name in dat_pclone_dic: num_dat_clones += len(dat_pclone_dic[parent_name])
        log_verb('No-Intro/Redump DAT has {0} clone ROMs'.format(num_dat_clones))

        # --- Generate main pclone dictionary ---
        # >> audit_unknown_roms is an int of list = ['Parents', 'Clones']
        # log_debug("settings['audit_unknown_roms'] = {0}".format(self.settings['audit_unknown_roms']))
        unknown_ROMs_are_parents = True if self.settings['audit_unknown_roms'] == 0 else False
        log_debug('unknown_ROMs_are_parents = {0}'.format(unknown_ROMs_are_parents))
        # if num_dat_clones == 0 and self.settings['audit_create_pclone_groups']:
        #     # --- If DAT has no PClone information and user want then generate filename-based PClone groups ---
        #     # >> This feature is taken from NARS (NARS Advanced ROM Sorting)
        #     log_verb('Generating filename-based Parent/Clone groups')
        #     pDialog(0, 'Building filename-based Parent/Clone index ...')
        #     roms_pclone_index = audit_generate_filename_PClone_index(roms, roms_nointro, unknown_ROMs_are_parents)
        #     pDialog(100)
        #     if __debug_progress_dialogs: time.sleep(0.5)
        # else:
        #     # --- Make a DAT-based Parent/Clone index ---
        #     # >> Here we build a roms_pclone_index with info from the DAT file. 2 issues:
        #     # >> A) Redump DATs do not have cloneof information.
        #     # >> B) Also, it is at this point where a region custom parent may be chosen instead of
        #     # >>    the default one.
        #     log_verb('Generating DAT-based Parent/Clone groups')
        #     pDialog(0, 'Building DAT-based Parent/Clone index ...')
        #     roms_pclone_index = audit_generate_DAT_PClone_index(roms, roms_nointro, unknown_ROMs_are_parents)
        #     pDialog(100)
        #     if __debug_progress_dialogs: time.sleep(0.5)

        # --- Make a DAT-based Parent/Clone index ---
        # >> For 0.9.7 only use the DAT to make the PClone groups. In 0.9.8 decouple the audit
        # >> code from the PClone generation code.
        log_verb('Generating DAT-based Parent/Clone groups')
        self._updateProgress(0, 'Building DAT-based Parent/Clone index ...')
        roms_pclone_index = audit_generate_DAT_PClone_index(roms, roms_nointro, unknown_ROMs_are_parents)
        self._updateProgress(100)
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Make a Clone/Parent index ---
        # >> This is made exclusively from the Parent/Clone index
        self._updateProgress(0, 'Building Clone/Parent index ...')
        clone_parent_dic = {}
        for parent_id in roms_pclone_index:
            for clone_id in roms_pclone_index[parent_id]:
                clone_parent_dic[clone_id] = parent_id
        self._updateProgress(100)
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Set ROMs pclone_status flag and update launcher statistics ---
        self._updateProgress(0, 'Audit Step 4/4: Setting Parent/Clone status and cloneof fields...')
        num_items = len(roms)
        item_counter = 0
        audit_parents = audit_clones = 0
        for rom in roms:
            rom_id = rom.get_id()
            if rom_id in roms_pclone_index:
                rom.set_pclone_status(PCLONE_STATUS_PARENT)
                audit_parents += 1
            else:
                rom.set_clone(clone_parent_dic[rom_id])
                rom.set_pclone_status(PCLONE_STATUS_CLONE)
                audit_clones += 1
            item_counter += 1
            self._updateProgress((item_counter*100)/num_items)
            if __debug_progress_dialogs: time.sleep(__debug_time_step)
        self._updateProgress(100)

        launcher.set_audit_stats(len(roms), audit_parents, audit_clones, audit_have, audit_miss, audit_unknown)

        # --- Make a Parent only ROM list and save JSON ---
        # >> This is to speed up rendering of launchers in 1G1R display mode
        self._updateProgress(0, 'Building Parent/Clone index and Parent dictionary ...')
        parent_roms = audit_generate_parent_ROMs_dic(roms, roms_pclone_index)
        self._updateProgress(100)
        if __debug_progress_dialogs: time.sleep(0.5)

        # --- Save JSON databases ---
        self._updateProgress(0, 'Saving NO-Intro/Redump JSON databases ...')
        fs_write_JSON_file(ROMS_DIR, launcher['roms_base_noext'] + '_index_PClone', roms_pclone_index)
        self._updateProgress(30)
        fs_write_JSON_file(ROMS_DIR, launcher['roms_base_noext'] + '_index_CParent', clone_parent_dic)
        self._updateProgress(60)
        fs_write_JSON_file(ROMS_DIR, launcher['roms_base_noext'] + '_parents', parent_roms)
        self._updateProgress(100)
        self._endProgressPhase()

        # --- Update launcher number of ROMs ---
        self.audit_have    = audit_have
        self.audit_miss    = audit_miss
        self.audit_unknown = audit_unknown
        self.audit_total   = len(roms)
        self.audit_parents = audit_parents
        self.audit_clones  = audit_clones

        # --- Report ---
        log_info('********** No-Intro/Redump audit finished. Report ***********')
        log_info('Have ROMs    {0:6d}'.format(self.audit_have))
        log_info('Miss ROMs    {0:6d}'.format(self.audit_miss))
        log_info('Unknown ROMs {0:6d}'.format(self.audit_unknown))
        log_info('Total ROMs   {0:6d}'.format(self.audit_total))
        log_info('Parent ROMs  {0:6d}'.format(self.audit_parents))
        log_info('Clone ROMs   {0:6d}'.format(self.audit_clones))

        return True

    #
    # Resets the No-Intro status
    # 1) Remove all ROMs which does not exist.
    # 2) Set status of remaining ROMs to nointro_status = NOINTRO_STATUS_NONE
    #
    def roms_reset_NoIntro_status_roms_reset_NoIntro_status(self, launcher, roms):
        log_info('roms_reset_NoIntro_status() Launcher has {0} ROMs'.format(len(roms)))
        if len(roms) < 1: return

        # >> Step 1) Delete missing/dead ROMs
        num_removed_roms = self._roms_delete_missing_ROMs(roms)
        log_info('roms_reset_NoIntro_status() Removed {0} dead/missing ROMs'.format(num_removed_roms))

        # >> Step 2) Set No-Intro status to NOINTRO_STATUS_NONE and
        #            set PClone status to PCLONE_STATUS_NONE
        log_info('roms_reset_NoIntro_status() Resetting No-Intro status of all ROMs to None')
        for rom in roms: 
            rom.set_nointro_status(NOINTRO_STATUS_NONE)
            rom.set_pclone_status(PCLONE_STATUS_NONE)

        log_info('roms_reset_NoIntro_status() Now launcher has {0} ROMs'.format(len(roms)))

        # >> Step 3) Delete PClone index and Parent ROM list.
        launcher.reset_parent_and_clone_roms()

    # Deletes missing ROMs
    #
    def _roms_delete_missing_ROMs(self, roms):
        num_removed_roms = 0
        num_roms = len(roms)
        log_info('_roms_delete_missing_ROMs() Launcher has {0} ROMs'.format(num_roms))
        if num_roms > 0:
            log_verb('_roms_delete_missing_ROMs() Starting dead items scan')

            for rom in reversed(roms):
            
                ROMFileName = rom.get_file()
                if not rom_file:
                    log_debug('_roms_delete_missing_ROMs() Skip "{0}"'.format(rom.get_name()))
                    continue

                log_debug('_roms_delete_missing_ROMs() Test "{0}"'.format(ROMFileName.getBase()))
                # --- Remove missing ROMs ---
                if not ROMFileName.exists():
                    log_debug('_roms_delete_missing_ROMs() RM   "{0}"'.format(ROMFileName.getBase()))
                    roms.remove(rom)
                    num_removed_roms += 1

            if num_removed_roms > 0:
                log_info('_roms_delete_missing_ROMs() {0} dead ROMs removed successfully'.format(num_removed_roms))
            else:
                log_info('_roms_delete_missing_ROMs() No dead ROMs found.')
        else:
            log_info('_roms_delete_missing_ROMs() Launcher is empty. No dead ROM check.')

        return num_removed_roms

# #################################################################################################
# #################################################################################################
# Gamestream
# #################################################################################################
# #################################################################################################
class GameStreamServer(object):
    def __init__(self, host, certificates_path):
        self.host = host
        self.unique_id = random.getrandbits(16)

        if certificates_path:
            self.certificates_path = certificates_path
            self.certificate_file_path = self.certificates_path.pjoin('nvidia.crt')
            self.certificate_key_file_path = self.certificates_path.pjoin('nvidia.key')
        else:
            self.certificates_path = FileName('')
            self.certificate_file_path = FileName('')
            self.certificate_key_file_path = FileName('')

        log_debug('GameStreamServer() Using certificate key file {}'.format(self.certificate_key_file_path.getPath()))
        log_debug('GameStreamServer() Using certificate file {}'.format(self.certificate_file_path.getPath()))

        self.pem_cert_data = None
        self.key_cert_data = None

    def _perform_server_request(self, end_point,  useHttps=True, parameters = None):
        if useHttps:
            url = "https://{0}:47984/{1}?uniqueid={2}&uuid={3}".format(self.host, end_point, self.unique_id, uuid.uuid4().hex)
        else:
            url = "http://{0}:47989/{1}?uniqueid={2}&uuid={3}".format(self.host, end_point, self.unique_id, uuid.uuid4().hex)

        if parameters:
            for key, value in parameters.iteritems():
                url = url + "&{0}={1}".format(key, value)

        handler = HTTPSClientAuthHandler(self.certificate_key_file_path.getPath(), self.certificate_file_path.getPath())
        page_data = net_get_URL_using_handler(url, handler)
    
        if page_data is None:
            return None

        root = ET.fromstring(page_data)
        #log_debug(ET.tostring(root,encoding='utf8',method='xml'))
        return root

    def connect(self):
        log_debug('Connecting to gamestream server {}'.format(self.host))
        self.server_info = self._perform_server_request("serverinfo")
        
        if not self.is_connected():
            self.server_info = self._perform_server_request("serverinfo", False)
        
        return self.is_connected()

    def is_connected(self):
        if self.server_info is None:
            log_debug('No succesfull connection to the server has been made')
            return False

        if self.server_info.find('state') is None:
            log_debug('Server state {0}'.format(self.server_info.attrib['status_code']))
        else:
            log_debug('Server state {0}'.format(self.server_info.find('state').text))

        return self.server_info.attrib['status_code'] == '200'

    def get_server_version(self):
        appVersion = self.server_info.find('appversion')
        return VersionNumber(appVersion.text)
    
    def get_uniqueid(self):
        uniqueid = self.server_info.find('uniqueid').text
        return uniqueid
    
    def get_hostname(self):
        hostname = self.server_info.find('hostname').text
        return hostname

    def generatePincode(self):
        i1 = random.randint(1, 9)
        i2 = random.randint(1, 9)
        i3 = random.randint(1, 9)
        i4 = random.randint(1, 9)
    
        return '{0}{1}{2}{3}'.format(i1, i2, i3, i4)

    def is_paired(self):
        if not self.is_connected():
            log_warning('Connect first')
            return False

        pairStatus = self.server_info.find('PairStatus')
        return pairStatus.text == '1'

    def pairServer(self, pincode):
        if not self.is_connected():
            log_warning('Connect first')
            return False

        version = self.get_server_version()
        log_info("Pairing with server generation: {0}".format(version.getFullString()))

        majorVersion = version.getMajor()
        if majorVersion >= 7:
            # Gen 7+ uses SHA-256 hashing
            hashAlgorithm = HashAlgorithm(256)
        else:
            # Prior to Gen 7, SHA-1 is used
            hashAlgorithm = HashAlgorithm(1)
        log_debug('Pin {0}'.format(pincode))

        # Generate a salt for hashing the PIN
        salt = randomBytes(16)
        # Combine the salt and pin
        saltAndPin = salt + bytearray(pincode, 'utf-8')
        # Create an AES key from them
        aes_cypher = AESCipher(saltAndPin, hashAlgorithm)

        # get certificates ready
        log_debug('Getting local certificate files')
        client_certificate      = self.getCertificateBytes()
        client_key_certificate  = self.getCertificateKeyBytes()
        certificate_signature   = getCertificateSignature(client_certificate)

        # Start pairing with server
        log_debug('Start pairing with server')
        pairing_result = self._perform_server_request('pair', False, {
            'devicename': 'ael', 
            'updateState': 1, 
            'phrase': 'getservercert', 
            'salt': binascii.hexlify(salt),
            'clientcert': binascii.hexlify(client_certificate)
            })

        if pairing_result is None:
            log_error('Failed to pair with server. No XML received.')
            return False

        isPaired = pairing_result.find('paired').text
        if isPaired != '1':
            log_error('Failed to pair with server. Server returned failed state.')
            return False

        server_cert_data = pairing_result.find('plaincert').text
        if server_cert_data is None:
            log_error('Failed to pair with server. A different pairing session might be in progress.')
            return False
        
        # Generate a random challenge and encrypt it with our AES key
        challenge = randomBytes(16)
        encrypted_challenge = aes_cypher.encryptToHex(challenge)
        
        # Send the encrypted challenge to the server
        log_debug('Sending encrypted challenge to the server')
        pairing_challenge_result = self._perform_server_request('pair', False, {
            'devicename': 'ael', 
            'updateState': 1, 
            'clientchallenge': encrypted_challenge })
        
        if pairing_challenge_result is None:
            log_error('Failed to pair with server. No XML received.')
            return False

        isPaired = pairing_challenge_result.find('paired').text
        if isPaired != '1':
            log_error('Failed to pair with server. Server returned failed state.')
            self._perform_server_request('unpair', False)
            return False

        # Decode the server's response and subsequent challenge
        log_debug('Decoding server\'s response and challenge response')
        server_challenge_hex = pairing_challenge_result.find('challengeresponse').text
        server_challenge_bytes = bytearray.fromhex(server_challenge_hex)
        server_challenge_decrypted = aes_cypher.decrypt(server_challenge_bytes)
        
        server_challenge_firstbytes = server_challenge_decrypted[:hashAlgorithm.digest_size()]
        server_challenge_lastbytes  = server_challenge_decrypted[hashAlgorithm.digest_size():hashAlgorithm.digest_size()+16]

        # Using another 16 bytes secret, compute a challenge response hash using the secret, our cert sig, and the challenge
        client_secret               = randomBytes(16)
        challenge_response          = server_challenge_lastbytes + certificate_signature + client_secret
        challenge_response_hashed   = hashAlgorithm.hash(challenge_response)
        challenge_response_encrypted= aes_cypher.encryptToHex(challenge_response_hashed)
        
        # Send the challenge response to the server
        log_debug('Sending the challenge response to the server')
        pairing_secret_response = self._perform_server_request('pair', False, {
            'devicename': 'ael', 
            'updateState': 1, 
            'serverchallengeresp': challenge_response_encrypted })
        
        if pairing_secret_response is None:
            log_error('Failed to pair with server. No XML received.')
            return False

        isPaired = pairing_secret_response.find('paired').text
        if isPaired != '1':
            log_error('Failed to pair with server. Server returned failed state.')
            self._perform_server_request('unpair', False)
            return False

        # Get the server's signed secret
        log_debug('Verifiying server signature')
        server_secret_response  = bytearray.fromhex(pairing_secret_response.find('pairingsecret').text)
        server_secret           = server_secret_response[:16]
        server_signature        = server_secret_response[16:272]

        server_cert = server_cert_data.decode('hex')
        is_verified = verify_signature(str(server_secret), server_signature, server_cert)

        if not is_verified:
            # Looks like a MITM, Cancel the pairing process
            log_error('Failed to verify signature. (MITM warning)')
            self._perform_server_request('unpair', False)
            return False

        # Ensure the server challenge matched what we expected (aka the PIN was correct)
        log_debug('Confirming PIN with entered value')
        server_cert_signature       = getCertificateSignature(server_cert)
        server_secret_combination   = challenge + server_cert_signature + server_secret
        server_secret_hashed        = hashAlgorithm.hash(server_secret_combination)

        if server_secret_hashed != server_challenge_firstbytes:
            # Probably got the wrong PIN
            log_error("Wrong PIN entered")
            self._perform_server_request('unpair', False)
            return False

        log_debug('Pin is confirmed')

        # Send the server our signed secret
        log_debug('Sending server our signed secret')
        signed_client_secret = sign_data(client_secret, client_key_certificate)
        client_pairing_secret = client_secret + signed_client_secret

        client_pairing_secret_response = self._perform_server_request('pair', False, {
            'devicename': 'ael', 
            'updateState': 1, 
            'clientpairingsecret':  binascii.hexlify(client_pairing_secret)})
        
        isPaired = client_pairing_secret_response.find('paired').text
        if isPaired != '1':
            log_error('Failed to pair with server. Server returned failed state.')
            self._perform_server_request('unpair', False)
            return False

        # Do the initial challenge over https
        log_debug('Initial challenge again')
        pair_challenge_response = self._perform_server_request('pair', True, {
            'devicename': 'ael', 
            'updateState': 1, 
            'phrase':  'pairchallenge'})

        isPaired = pair_challenge_response.find('paired').text
        if isPaired != '1':
            log_error('Failed to pair with server. Server returned failed state.')
            self._perform_server_request('unpair', False)
            return False

        return True

    def getApps(self):
        apps_response = self._perform_server_request('applist', True)
        appnodes = apps_response.findall('App')
        apps = []
        for appnode in appnodes:
            app = {}
            for appnode_attr in appnode:
                if len(list(appnode_attr)) > 1:
                    continue
                
                xml_text = appnode_attr.text if appnode_attr.text is not None else ''
                xml_text = text_unescape_XML(xml_text)
                xml_tag  = appnode_attr.tag
           
                app[xml_tag] = xml_text
            apps.append(app)

        return apps

    def getCertificateBytes(self):
        if self.pem_cert_data:
            return self.pem_cert_data

        if not self.certificate_file_path.exists():
            log_info('Client certificate file does not exist. Creating')
            create_self_signed_cert("NVIDIA GameStream Client", self.certificate_file_path, self.certificate_key_file_path)

        log_info('Loading client certificate data from {0}'.format(self.certificate_file_path.getPath()))
        self.pem_cert_data = self.certificate_file_path.readAll()

        return self.pem_cert_data

    def getCertificateKeyBytes(self):
        if self.key_cert_data:
            return self.key_cert_data

        if not self.certificate_key_file_path.exists():
            log_info('Client certificate file does not exist. Creating')
            create_self_signed_cert("NVIDIA GameStream Client", self.certificate_file_path, self.certificate_key_file_path)
        log_info('Loading client certificate data from {0}'.format(self.certificate_key_file_path.getPath()))
        self.key_cert_data = self.certificate_key_file_path.readAll()

        return self.key_cert_data

    def validate_certificates(self):
        if self.certificate_file_path.exists() and self.certificate_key_file_path.exists():
            log_debug('validate_certificates(): Certificate files exist. Done')
            return True

        certificate_files = self.certificates_path.scanFilesInPathAsFileNameObjects('*.crt')
        key_files = self.certificates_path.scanFilesInPathAsFileNameObjects('*.key')

        if len(certificate_files) < 1:
            log_warning('validate_certificates(): No .crt files found at given location.')
            return False

        if not self.certificate_file_path.exists():
            log_debug('validate_certificates(): Copying .crt file to nvidia.crt')
            certificate_files[0].copy(self.certificate_file_path)

        if len(key_files) < 1:
            log_warning('validate_certificates(): No .key files found at given location.')
            return False

        if not self.certificate_key_file_path.exists():
            log_debug('validate_certificates(): Copying .key file to nvidia.key')
            key_files[0].copy(certificate_key_file_path)

        return True

    @staticmethod
    def try_to_resolve_path_to_nvidia_certificates():
        home = expanduser("~")
        homePath = FileName(home)

        possiblePath = homePath.pjoin('Moonlight/')
        if possiblePath.exists():
            return possiblePath.getPath()

        possiblePath = homePath.pjoin('Limelight/')
        if possiblePath.exists():
            return possiblePath.getPath()

        return homePath.getPath()

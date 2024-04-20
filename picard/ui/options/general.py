# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
#
# Copyright (C) 2006-2007, 2014 Lukáš Lalinský
# Copyright (C) 2008, 2018-2023 Philipp Wolfer
# Copyright (C) 2011, 2013 Michael Wiencek
# Copyright (C) 2011, 2019 Wieland Hoffmann
# Copyright (C) 2013-2014 Sophist-UK
# Copyright (C) 2013-2014, 2018, 2020-2021, 2023-2024 Laurent Monin
# Copyright (C) 2016-2017 Sambhav Kothari
# Copyright (C) 2017 Frederik “Freso” S. Olesen
# Copyright (C) 2018 virusMac
# Copyright (C) 2018, 2023 Bob Swift
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from PyQt6 import QtCore

from picard.config import (
    BoolOption,
    IntOption,
    TextOption,
    get_config,
)
from picard.const import (
    DEFAULT_PROGRAM_UPDATE_LEVEL,
    MUSICBRAINZ_SERVERS,
    PROGRAM_UPDATE_LEVELS,
)
from picard.i18n import (
    N_,
    _,
    gettext_constants,
)
from picard.util.mbserver import is_official_server

from picard.ui.options import (
    OptionsPage,
    register_options_page,
)
from picard.ui.ui_options_general import Ui_GeneralOptionsPage


class GeneralOptionsPage(OptionsPage):

    NAME = 'general'
    TITLE = N_("General")
    PARENT = None
    SORT_ORDER = 1
    ACTIVE = True
    HELP_URL = "/config/options_general.html"

    options = [
        TextOption('setting', 'server_host', MUSICBRAINZ_SERVERS[0], title=N_("Server address")),
        IntOption('setting', 'server_port', 443, title=N_("Port")),
        BoolOption('setting', 'use_server_for_submission', False),
        BoolOption('setting', 'analyze_new_files', False, title=N_("Automatically scan all new files")),
        BoolOption('setting', 'cluster_new_files', False, title=N_("Automatically cluster all new files")),
        BoolOption('setting', 'ignore_file_mbids', False, title=N_("Ignore MBIDs when loading new files")),
        TextOption('persist', 'oauth_refresh_token', ''),
        TextOption('persist', 'oauth_refresh_token_scopes', ''),
        TextOption('persist', 'oauth_access_token', ''),
        IntOption('persist', 'oauth_access_token_expires', 0),
        TextOption('persist', 'oauth_username', ''),
        BoolOption('setting', 'check_for_updates', True, title=N_("Check for program updates during startup")),
        IntOption('setting', 'update_check_days', 7, title=N_("Days between update checks")),
        IntOption('setting', 'update_level', DEFAULT_PROGRAM_UPDATE_LEVEL, title=N_("Updates to check")),
        IntOption('persist', 'last_update_check', 0),
        BoolOption('setting', 'check_for_plugin_updates', False, title=N_("Check for plugin updates during startup")),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_GeneralOptionsPage()
        self.ui.setupUi(self)
        self.ui.server_host.addItems(MUSICBRAINZ_SERVERS)
        self.ui.server_host.currentTextChanged.connect(self.update_server_host)
        self.ui.login.clicked.connect(self.login)
        self.ui.logout.clicked.connect(self.logout)
        self.ui.analyze_new_files.toggled.connect(self._update_cluster_new_files)
        self.ui.cluster_new_files.toggled.connect(self._update_analyze_new_files)
        self.ui.login_error.setStyleSheet(self.STYLESHEET_ERROR)
        self.ui.login_error.hide()
        self.update_login_logout()

    def load(self):
        config = get_config()
        self.ui.server_host.setEditText(config.setting['server_host'])
        self.ui.server_port.setValue(config.setting['server_port'])
        self.ui.use_server_for_submission.setChecked(config.setting['use_server_for_submission'])
        self.update_server_host()
        self.ui.analyze_new_files.setChecked(config.setting['analyze_new_files'])
        self.ui.cluster_new_files.setChecked(config.setting['cluster_new_files'])
        self.ui.ignore_file_mbids.setChecked(config.setting['ignore_file_mbids'])
        self.ui.check_for_plugin_updates.setChecked(config.setting['check_for_plugin_updates'])
        self.ui.check_for_updates.setChecked(config.setting['check_for_updates'])
        self.set_update_level(config.setting['update_level'])
        self.ui.update_check_days.setValue(config.setting['update_check_days'])
        if not self.tagger.autoupdate_enabled:
            self.ui.program_update_check_group.hide()

    def set_update_level(self, value):
        if value not in PROGRAM_UPDATE_LEVELS:
            value = DEFAULT_PROGRAM_UPDATE_LEVEL
        self.ui.update_level.clear()
        for level, description in PROGRAM_UPDATE_LEVELS.items():
            # TODO: Remove temporary workaround once https://github.com/python-babel/babel/issues/415 has been resolved.
            babel_415_workaround = description['title']
            self.ui.update_level.addItem(gettext_constants(babel_415_workaround), level)
        idx = self.ui.update_level.findData(value)
        if idx == -1:
            idx = self.ui.update_level.findData(DEFAULT_PROGRAM_UPDATE_LEVEL)
        self.ui.update_level.setCurrentIndex(idx)

    def save(self):
        config = get_config()
        config.setting['server_host'] = self.ui.server_host.currentText().strip()
        config.setting['server_port'] = self.ui.server_port.value()
        config.setting['use_server_for_submission'] = self.ui.use_server_for_submission.isChecked()
        config.setting['analyze_new_files'] = self.ui.analyze_new_files.isChecked()
        config.setting['cluster_new_files'] = self.ui.cluster_new_files.isChecked()
        config.setting['ignore_file_mbids'] = self.ui.ignore_file_mbids.isChecked()
        config.setting['check_for_plugin_updates'] = self.ui.check_for_plugin_updates.isChecked()
        config.setting['check_for_updates'] = self.ui.check_for_updates.isChecked()
        config.setting['update_level'] = self.ui.update_level.currentData(QtCore.Qt.ItemDataRole.UserRole)
        config.setting['update_check_days'] = self.ui.update_check_days.value()

    def update_server_host(self):
        host = self.ui.server_host.currentText().strip()
        if host and is_official_server(host):
            self.ui.server_host_primary_warning.hide()
        else:
            self.ui.server_host_primary_warning.show()

    def update_login_logout(self, error_msg=None):
        if self.deleted:
            return
        if self.tagger.webservice.oauth_manager.is_logged_in():
            config = get_config()
            self.ui.logged_in.setText(_("Logged in as <b>%s</b>.") % config.persist['oauth_username'])
            self.ui.logged_in.show()
            self.ui.login_error.hide()
            self.ui.login.hide()
            self.ui.logout.show()
        elif error_msg:
            self.ui.logged_in.hide()
            self.ui.login_error.setText(_("Login failed: %s") % error_msg)
            self.ui.login_error.show()
            self.ui.login.show()
            self.ui.logout.hide()
        else:
            self.ui.logged_in.hide()
            self.ui.login_error.hide()
            self.ui.login.show()
            self.ui.logout.hide()

    def login(self):
        self.tagger.mb_login(self.on_login_finished, self)

    def restore_defaults(self):
        super().restore_defaults()
        self.logout()

    def on_login_finished(self, successful, error_msg=None):
        self.update_login_logout(error_msg)

    def logout(self):
        self.tagger.mb_logout()
        self.update_login_logout()

    def _update_analyze_new_files(self, cluster_new_files):
        if cluster_new_files:
            self.ui.analyze_new_files.setChecked(False)

    def _update_cluster_new_files(self, analyze_new_files):
        if analyze_new_files:
            self.ui.cluster_new_files.setChecked(False)


register_options_page(GeneralOptionsPage)

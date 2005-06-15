# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# (C) Copyright 2005 Unilog <http://unilog.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# G. de la Rochemace <gdelaroch@unilog.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""A module which provides unit tests for translations.

This module actually provides unit tests on the well-formedness and quality of
.pot and .po files.

This module was inspired by the plone-i18n work, references:
http://i18n.kde.org/translation-howto/check-gui.html#check-msgfmt
http://cvs.sourceforge.net/viewcvs.py/plone-i18n/i18n/tests/
"""

import os, os.path, sys, re
import unittest
from gettext import GNUTranslations
from msgfmt import Msgfmt, PoSyntaxError


def canonizeLang(lang):
    """Return a canonized language name so that language names can easily be
    compared.
    """
    return lang.lower().replace('_', '-')


def getLanguageFromPoFile(file_path):
    """Check that the same of the .po file corresponds to the contained
    translations.
    """
    # get file
    file = file_path.split('/')[-1]
    # strip of .po
    file = file[:-3]
    # This code was for CPSSkins which has .po of the form cpsskins-en.po
    #lang = file.split('-')[1:][-1:]
    #return '-'.join(lang)
    return file


def getI18nDirPath(product_name):
    import Products
    product_file = getattr(Products, product_name).__file__
    product_path = os.path.dirname(product_file)
    po_path = os.path.join(product_path, 'i18n')
    return po_path


def getPotFiles(product_name):
    i18n_dir_path = getI18nDirPath(product_name)
    pot_files = [f for f in os.listdir(i18n_dir_path) if f.endswith('.pot')]
    return pot_files


def getPoFiles(product_name):
    i18n_dir_path = getI18nDirPath(product_name)
    po_files = [f for f in os.listdir(i18n_dir_path) if f.endswith('.po')]
    return po_files


class TranslationsTestCase(unittest.TestCase):
    """Inherit from this class to test the .pot and .po files of your products.
    """

    def setUp(self):
        self.product_name = __name__.split('.')[0]

    def testPotFiles(self):
        for pot_filename in getPotFiles(self.product_name):
            test_ensemble = TestPotFile(pot_filename, self.product_name)
            test_ensemble.testNoDuplicateMsgId()

    def testPoFiles(self):
        for po_filename in getPoFiles(self.product_name):
            test_ensemble = TestPoFile(po_filename, self.product_name)
            test_ensemble.testPoFile()


# DOTALL: Make the "." special character match any character at all, including a
# newline; without this flag, "." will match anything except a newline.
#
# for example:
#
# msgid "button_back"
# msgstr ""
#
# returns 'button_back'
#
MSGID_REGEXP = re.compile('msgid "(.*?)".*?msgstr "', re.DOTALL)

class TestPotFile(unittest.TestCase):

    def __init__(self, pot_filename, product_name):
        self.pot_filename = pot_filename
        self.product_name = product_name

    def testNoDuplicateMsgId(self):
        """Check that there are no duplicate msgid:s in the pot files"""

        pot = self.pot_filename

        file = open(os.path.join(getI18nDirPath(self.product_name), pot), 'r')
        file_content = file.read()
        file.close()

        # Check for duplicate msgids
        matches = re.finditer(MSGID_REGEXP, file_content)

        msgids = []

        for match in matches:
            msgid = match.group(0)
            if msgid in msgids:
                assert 0, "Duplicate msgid:s were found in the file %s :\n\n%s" \
                       % (pot, msgid)
            else:
                msgids.append(msgid)


# DOTALL: Make the "." special character match any character at all, including a
# newline; without this flag, "." will match anything except a newline.
#
# #, fuzzy
# msgid ""
# msgstr ""
#
FUZZY_HEADER_ENTRY_REGEXP = re.compile('#, fuzzy\nmsgid ""\nmsgstr ""',
                                       re.DOTALL)

# IGNORECASE: Perform case-insensitive matching; expressions like [A-Z] will
# match lowercase letters, too. This is not affected by the current locale.
#
# MULTILINE: When specified, the pattern character "^" matches at the beginning
# of the string and at the beginning of each line (immediately following each
# newline); and the pattern character "$" matches at the end of the string and
# at the end of each line (immediately preceding each newline). By default, "^"
# matches only at the beginning of the string, and "$" only at the end of the
# string and immediately before the newline (if any) at the end of the string.
#
# Check the charset:
#
# for example
#
# "Content-Type: text/plain; charset=ISO-8859-15\n"
#
CHARSET_REGEXP = re.compile('^"Content-Type: text/plain; charset=ISO-8859-15',
                            re.MULTILINE | re.IGNORECASE)

class TestPoFile(unittest.TestCase):

    def __init__(self, po_filename, product_name):
        self.po_filename = po_filename
        self.product_name = product_name

    def testPoFile(self):
        po = self.po_filename

        po_name = po
        file = open(os.path.join(getI18nDirPath(self.product_name), po), 'r')
        file_content = file.read()
        file.seek(0)
        try:
            lines = file.readlines()
        except IOError, msg:
            self.fail('Can\'t read po file %s:\n%s' % (po_name, msg))
        file.close()

        # Checking that the .po file has a non-fuzzy header entry, so that it
        # cannot be deleted by error.
        match_fuzzy = re.findall(FUZZY_HEADER_ENTRY_REGEXP, file_content)

        match_charset = re.findall(CHARSET_REGEXP, file_content)

        if len(match_fuzzy) != 0:
            assert 0, "Fuzzy header entry found in file %s! " \
               "Remove the fuzzy flag on this entry.\n\n" \
               % po_name

        if len(match_charset) != 1:
            assert 0, "Invalid charset found in file %s! \n the correct " \
               "line is : 'Content-Type: text/plain; charset=ISO-8859-15'\n\n" \
               % po_name

        try:
            mo = Msgfmt(lines)
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (po_name, msg))
        except SyntaxError, msg:
            self.fail('SyntaxError: Invalid po data syntax in file %s \
                      (Can\'t parse file with eval():\n%s' % (po_name, msg))
        except Exception, msg:
            self.fail('Unknown error while parsing the po file %s:\n%s' \
                      % (po_name, msg))

        try:
            tro = GNUTranslations(mo.getAsFile())
            #print "tro = %s" % tro
        except UnicodeDecodeError, msg:
            self.fail('UnicodeDecodeError in file %s:\n%s' % (po_name, msg))
        except PoSyntaxError, msg:
            self.fail('PoSyntaxError: Invalid po data syntax in file %s:\n%s' \
                      % (po_name, msg))

        domain = tro._info.get('domain', None)
        #print "domain = %s" % domain
        self.failUnless(domain, 'Po file %s has no domain!' % po)

        language_new = tro._info.get('language-code', None) # new way
        #print "language_new = %s" % language_new
        language_old = tro._info.get('language', None) # old way
        #print "language_old = %s" % language_old
        language = language_new or language_old

        self.failIf(language_old, 'The file %s has the old style language flag \
                                   set to %s. Please remove it!' \
                                  % (po_name, language_old))

        self.failUnless(language, 'Po file %s has no language!' % po)

        fileLang = getLanguageFromPoFile(po)
        #print "getLanguageFromPoFile = %s" % fileLang
        fileLang = canonizeLang(fileLang)
        #print "canonizeLang = %s" % fileLang
        language = canonizeLang(language)
        #print "language canonizeLang(language) = %s" % language
        self.assertEquals(fileLang, language,
                          "Your file %s has a wrong file name "
                          "or states a wrong language code.\n"
                          "Your file %s should either "
                          "be named \"%s.po\" "
                          "or have a line stating \"Language-code: %s\n\""
                          % (po_name, po_name, language, fileLang))


        # i18n completeness chart generation mechanism relies on case sensitive
        # Language-Code and Language-Name.
        for meta_info in ['"Language-Code: ',
                          '"Language-Name: ',
                          '"Domain: ',
                          ]:
            # XXX: Get rid of this "grep"!
            import commands
            cmd = """grep '%s' %s/%s""" % (
                meta_info, getI18nDirPath(self.product_name), po_name)
            #print "cmd = %s" % cmd
            statusoutput = commands.getstatusoutput(cmd)
            #print "status = %s" % statusoutput[0]
            #print "output = %s" % statusoutput[1]
            self.assert_(statusoutput[0] == 0,
                         "Wrong case used for metadata in file %s! "
                         "Check that your metadata is "
                         "Language-Code, Language-Name and Domain.\n\n%s"
                         % (po_name, statusoutput[1]))


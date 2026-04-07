# Build customizations
# Change this file instead of SConstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _


addon_info = AddonInfo(
	addon_name="ClipboardContentEditor",
	# Translators: Summary/title for this add-on
	addon_summary=_("Clipboard Content Editor"),
	# Translators: Long description for this add-on
	addon_description=_(
		"Edits the current clipboard text in a simple editor so pasted content reflects the changes. "
		"Shortcuts: NVDA+E opens the editor, NVDA+Z restores the previous clipboard, and NVDA+I shows clipboard info."
	),
	addon_version="1.2.3",
	# Translators: What's new content for the add-on version
	addon_changelog=_(
		"- Added Arabic language support.\n"
		"- No other feature update."
	),
	addon_author="Fauzan January <surel@fauzanaja.com>",
	addon_url="https://fauzanaja.com/nvda-addon/",
	addon_sourceURL="https://github.com/fauzan-january/clipboard-content-editor/",
	addon_docFileName="readme.html",
	addon_minimumNVDAVersion="2024.1",
	addon_lastTestedNVDAVersion="2025.3",
	addon_updateChannel=None,
	addon_license="GPL-2.0",
	addon_licenseURL="https://www.gnu.org/licenses/gpl-2.0.html",
)

pythonSources: list[str] = [
	"addon/installTasks.py",
	"addon/globalPlugins/ClipboardContentEditor/*.py",
]

i18nSources: list[str] = pythonSources + ["buildVars.py"]

excludedFiles: list[str] = []

baseLanguage: str = "en"

markdownExtensions: list[str] = []

brailleTables: BrailleTables = {}

symbolDictionaries: SymbolDictionaries = {}


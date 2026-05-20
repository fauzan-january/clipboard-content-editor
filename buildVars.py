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
		"A powerful clipboard editor and manager for NVDA users. Review, analyze, edit, and manage clipboard content before pasting. Use Ctrl+Alt+C to activate the command layer and press F1 to show the list of available commands."
	),
	addon_version="1.3.0",
	# Translators: What's new content for the add-on version
	addon_changelog=_(
		"- Added full compatibility for NVDA 2026.1 (Python 64-bit).\n"
		"- Refactored all global shortcuts into a unified Command Layer (Ctrl+Alt+C) to prevent conflicts. Press F1 after the command layer trigger to view all available commands.\n"
		"- Introduced an unlimited Clipboard History manager with complete CRUD capabilities (H in the command layer).\n"
		"- Added Append Mode (A in the command layer) to seamlessly collect multiple texts by concatenating new copies.\n"
		"- Restructured the Editor dialog by moving tools into a dedicated Tools menu.\n"
		"- Restored the ability to speak clipboard content without character limit (S in the command layer).\n"
		"- Added settings to configure the maximum Clipboard History size and override the addon's display language independently of NVDA.\n"
		"- Fixed a bug where the Editor dialog would freeze or hang after successfully saving a file via 'Save As...'.\n"
		"- Integrated a Development Support (PayPal donation) dialog into the installation flow."
		"- Added paragraph counting to the Information feature (characters, words, lines, and paragraphs)."
	),
	addon_author="Fauzan January <surel@fauzanaja.com>",
	addon_url="https://fauzanaja.com/nvda-addon/",
	addon_sourceURL="https://github.com/fauzan-january/clipboard-content-editor/",
	addon_docFileName="readme.html",
	addon_minimumNVDAVersion="2024.1",
	addon_lastTestedNVDAVersion="2026.1",
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


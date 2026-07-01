import unreal

from main import run

@unreal.uclass()
class AssetValidatorMenuEntry(unreal.ToolMenuEntryScript):

    @unreal.ufunction(override=True)
    def execute(self, context):
        run()


def setup_ui():
    menus = unreal.ToolMenus().get()

    asset_context_menu = menus.find_menu("ContentBrowser.AssetContextMenu")

    menu_entry = AssetValidatorMenuEntry()
    menu_entry.init_entry(
        owner_name=asset_context_menu.menu_name,
        menu=asset_context_menu.menu_name,
        section="GetAssetActions",
        name="AssetValidator",
        label="Validate Selected Assets",
        tool_tip="Run asset validation rules on the currently selected assets"
    )
    menu_entry.register_menu_entry()

    menus.refresh_all_widgets()

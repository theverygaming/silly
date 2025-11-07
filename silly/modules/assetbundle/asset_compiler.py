import sillyorm
import silly


class AssetCompiler(silly.model.AbstractModel):
    _name = "assetbundle.asset_compiler"

    def _compile_asset(self, asset):
        pass

    def _bundle_js(self, assets):
        out_txt = "/* JS asset bundle */\n"
        for asset in assets:
            out_txt += f"""/* module: {asset.module} - {asset.path} */
{_compile_asset(asset)}
/* END */
"""

    def _bundle(self, btype, assets):
        match btype:
            case "js":
                return _bundle_js(assets)
            case _:
                raise silly.exceptions.SillyException(f"unknown asset bundle type {btype}")

    def get_assetbundle(self, name):
        res = {}
        for btype, assets in silly.modload.assets.get(name, {}).items():
            res[btype] = self._bundle(btype, assets)
        return res

import sillyorm
import silly


class AssetCompiler(silly.model.AbstractModel):
    _extends = "core.asset_compiler"

    def _compile_assetbundle(self, t):
        pass

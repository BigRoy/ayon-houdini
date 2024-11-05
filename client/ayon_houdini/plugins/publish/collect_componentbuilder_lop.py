import os

import pyblish.api

from ayon_core.pipeline import AYONPyblishPluginMixin
from ayon_houdini.api import plugin

from pxr import Sdf, Usd, UsdUtils

class Resource:
    source: str
    files: str


class CollectComponentBuilderLOPs(plugin.HoudiniInstancePlugin,
                                  AYONPyblishPluginMixin):

    order = pyblish.api.CollectorOrder + 0.05
    families = ["componentbuilder"]
    label = "Collect Componentbuilder LOPs"

    def process(self, instance):

        node = hou.node(instance.data["instance_node"])

        # Use existing files for now
        filepath = node.evalParm("lopoutput")

        # Render the component builder LOPs
        # TODO: Do we want this? or use existing frames? Usually a Collector
        #  should not 'extract' but in this case we need the resulting USD
        #  file.
        # node.parm("execute").pressButton()

        # Compose the resulting stage
        stage = Usd.Stage.Open(filepath)
        instance.data["stage"] = stage

        # Define the main asset usd file
        representations = instance.data.setdefault("representations", [])
        representations.append({
            "name": "usd",
            "ext": "usd",
            "files": os.path.basename(filepath),
            "stagingDir": os.path.dirname(filepath),
        })

        # Get all its files and dependencies
        layers, assets, unresolved_paths = UsdUtils.ComputeAllDependencies(
            filepath)
        layers: list[Sdf.Layer]
        assets: list[str]
        unresolved_paths: list[str]

        # TODO: Ignore any files that are not 'relative' to the USD file

        # We keep the relative paths to the USD file
        transfers = instance.data.setdefault("transfers", [])
        publish_root = instance.data["publishDir"]
        for layer in layers:
            src = layer.realPath
            dest = os.path.relpath(layer.realPath, publish_root)
            transfers.append((src, dest))

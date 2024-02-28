import bpy
from mathutils import Vector

bl_info = {
    "name": "Edit Instanced Collection",
    "description": "Edit a Collection Instance's source Collection (even if it is not in the Scene).",
    "author": "FLEB",
    "version": (0, 2, 3),
    "blender": (3, 1, 0),
    "location": "Object > Edit Instanced Collection",
    "doc_url": "https://github.com/SuperFLEB/BlenderEditCollectionAddon",
    "tracker_url": "https://github.com/SuperFLEB/BlenderEditCollectionAddon/issues",
    "support": "COMMUNITY",
    "category": "Object",
}

addon_keymaps = []
package_name = __package__
seen_popup = False

class EditCollection(bpy.types.Operator):
    """Edit the Collection referenced by this Collection Instance in a new Scene"""
    bl_idname = "object.edit_collection"
    bl_label = "Edit Instanced Collection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = context.preferences.addons[package_name].preferences
        coll = bpy.context.active_object.instance_collection


        if not coll:
            print("Active item is not a collection instance")
            self.report({"WARNING"}, "Active item is not a collection instance")
            return {"CANCELLED"}

        # settings["original_scene"] = context.scene.name[:64] #.substring(0, 64)
        settings["original_scene"].append(context.scene.name[:64]) #.substring(0, 64)
        scene_name = f"temp:{str(coll.name)[:50]}"
        # print("Scene_name %s" % scene_name)
        # print("Scene_name %s" % str(tmp_name)[:10])
        # print("Scene_name %s" % scene_name[:10])
        # print("Scene_name %s" % scene_name[:20])
        # print("Scene_name %s" % scene_name[:30])
        bpy.ops.scene.new(type="EMPTY")
        new_scene = bpy.context.scene
        new_scene.name = scene_name
        bpy.context.window.scene = new_scene
        new_scene.collection.children.link(coll)

        settings["tmp_scene"].append(scene_name)

        if prefs.world_texture != "none":
            world = bpy.data.worlds.new(bpy.context.scene.name)
            new_scene.world = world
            world.use_nodes = True
            tree = world.node_tree

            if prefs.world_texture in ["checker", "checker_view"]:
                checker_texture = tree.nodes.new("ShaderNodeTexChecker")
                checker_texture.inputs["Scale"].default_value = 20
                checker_texture.location = Vector((-250, 0))
                if prefs.world_texture == "checker_view":
                    coord = tree.nodes.new("ShaderNodeTexCoord")
                    coord.location = Vector((-500, 0))
                    for op in coord.outputs:
                        op.hide = True
                    tree.links.new(coord.outputs["Window"], checker_texture.inputs["Vector"])
                tree.links.new(checker_texture.outputs["Color"], tree.nodes["Background"].inputs["Color"])
            elif prefs.world_texture == "gray":
                tree.nodes["Background"].inputs["Color"].default_value = (.3, .3, .3, 1)

        # Select the collection
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[coll.name]

        def message(self_2, _):
            global seen_popup

            self_2.layout.label(text="When you're done, simply delete the scene using the X")
            self_2.layout.label(text="and run File > Clean Up > Unused Data Blocks to clean up")
            self_2.layout.label(
                text=f"Be sure to keep all changes you wish to apply within the \"{coll.name}\" collection.")
            # Only show the message about it being able to be turned off the first time
            if not seen_popup:
                seen_popup = True
                self_2.layout.separator()
                self_2.layout.label(
                    text=f"(This message can be turned off in the {bl_info['name']} addon preferences panel.)",
                    icon="INFO"
                )

        if not prefs.hide_scene_popup:
            bpy.context.window_manager.popup_menu(message,
                                                  title=f"Temporary Scene \"{scene_name}\" Created",
                                                  icon="COLLECTION_NEW")
        # Center view
        bpy.ops.view3d.view_all(center=True)

        return {"FINISHED"}

settings = {
    "original_scene": [],
    "tmp_scene": [],
    # "linked_objects": [],
    # "linked_nodes": []
    }

class EIC_OP_ReturntoScene(bpy.types.Operator):
    """Return to main scene"""
    bl_idname = "object.eic_return_to_scene"
    bl_label = "Return to Scene"
    bl_options = {"REGISTER", "UNDO"}

    scene : bpy.props.StringProperty()

    def execute(self, context):
        if (self.scene == "previous"):
            settings["tmp_scene"].remove(context.scene.name)
            if (settings["tmp_scene"] == 0):
                settings["original_scene"] =[]
            else:
                settings["original_scene"].pop(len(settings["original_scene"])-1)

            bpy.ops.scene.delete()
            bpy.ops.view3d.view_selected(use_all_regions=False)
            # logger.info("Back to the original!")
        if (self.scene == "main"):
            for scn in settings["tmp_scene"]:
                bpy.context.window.scene = bpy.data.scenes[scn]
                bpy.ops.scene.delete()
            bpy.ops.view3d.view_selected(use_all_regions=False)
            settings["original_scene"] = []
            settings["tmp_scene"] = []
            # logger.info("Back to the original!")
        return {'FINISHED'}

class EIC_PT_PanelLinkedEdit(bpy.types.Panel):
    bl_label = "Edit Instanced Collection"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context: bpy.context):
        # print(context.active_object)
        # return settings["original_scene"] != ""
        return (context.active_object is not None) or (settings["original_scene"] != [])

    # def draw_common(self, scene, layout, props):
    #     if props is not None:
    #         props.use_autosave = scene.use_autosave
    #         props.use_instance = scene.use_instance

    #         layout.prop(scene, "use_autosave")
    #         layout.prop(scene, "use_instance")

    def draw(self, context: bpy.context):
        scene = context.scene
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        # layout.operator("object.eic_return_to_scene")

        target = None

        icon = 'OUTLINER_COLLECTION'
        try:
            # icon = "OUTLINER_DATA_" + context.active_object.type.replace("LIGHT_PROBE", "LIGHTPROBE")
            target = context.active_object
        
            if settings["original_scene"] == "" or settings["original_scene"] != "" and (target.instance_collection is not None):
            # if settings["original_scene"] == "" and (target is not None):
                    # (target and
                    # target.library is not None) or
                    # context.active_object.library is not None or
                    # (context.active_object.override_library is not None and
                    # context.active_object.override_library.reference is not None)):

                if (target.instance_collection is not None):
                    props = layout.operator("object.edit_collection", icon="LINK_BLEND",
                                            text="Edit Collection") # %s" % target.name)
            #     elif (context.active_object.library):
            #         props = layout.operator("object.edit_linked", icon="LINK_BLEND",
            #                                 text="Edit Library: %s" % context.active_object.name)
            #     else:
            #         props = layout.operator("object.edit_linked", icon="LINK_BLEND",
            #                                 text="Edit Override Library: %s" % context.active_object.override_library.reference.name)

            #     self.draw_common(scene, layout, props)

            #     if (target is not None):
            #         layout.label(text="Path: %s" %
            #                     target.library.filepath)
            #     elif (context.active_object.library):
            #         layout.label(text="Path: %s" %
            #                     context.active_object.library.filepath)
            #     else:
            #         layout.label(text="Path: %s" %
            #                     context.active_object.override_library.reference.library.filepath)
            else:
                layout.label(text="%s is not linked" % context.active_object.name,icon=icon)
            
            
            #         layout.separator()

            #         # XXX - This is for nested linked assets... but it only works
            #         # when launching a new Blender instance. Nested links don't
            #         # currently work when using a single instance of Blender.
            #         if context.active_object.instance_collection is not None:
            #             props = layout.operator("object.edit_linked",
            #                     text="Edit Library: %s" % context.active_object.instance_collection.name,
            #                     icon="LINK_BLEND")
            #         else:
            #             props = None

            #         self.draw_common(scene, layout, props)

            #         if context.active_object.instance_collection is not None:
            #             layout.label(text="Path: %s" %
            #                     context.active_object.instance_collection.library.filepath)

            #     else:
            #         props = layout.operator("wm.return_to_original", icon="LOOP_BACK")
            #         props.use_autosave = scene.use_autosave

            #         layout.prop(scene, "use_autosave")
        except:
            pass
        if settings["original_scene"] != []:
            if settings["tmp_scene"] != [] and len(settings["tmp_scene"]) != 1:
                props = layout.operator("object.eic_return_to_scene", text = 'Previous Collection', icon=icon)
                props.scene = 'previous'
            if len(settings["tmp_scene"]) >= 1:
                props = layout.operator("object.eic_return_to_scene", text='Return to Main Scene', icon='SCENE_DATA')
                props.scene = 'main'

class EditInstancedCollectionPreferences(bpy.types.AddonPreferences):
    bl_idname = package_name
    hide_scene_popup: bpy.props.BoolProperty(
        name="Don't show instructional popup message",
        description="Do not show the informational pop-up when editing a Collection",
        default=False
    )
    world_texture: bpy.props.EnumProperty(
        name="Background",
        description="Background (World) texture of the temporary scene",
        items=[
            ("checker", "Checker (generated map)", "Checker-like texture using a Generated map"),
            ("checker_view", "Checker (view aligned)", "Checkerboard texture aligned to the view"),
            ("gray", "Gray", "Solid Gray Background"),
            ("none", "None", "No World/background (black)")
        ]
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "world_texture")
        layout.prop(self, "hide_scene_popup")


def menu_function(self, context):
    if bpy.context.active_object.instance_collection:
        self.layout.operator(EditCollection.bl_idname)


classes = [
    EIC_OP_ReturntoScene,
    EIC_PT_PanelLinkedEdit
]
def register():
    global seen_popup
    seen_popup = False

    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(EditCollection)
    bpy.utils.register_class(EditInstancedCollectionPreferences)

    # Add menu items
    bpy.types.VIEW3D_MT_object.append(menu_function)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_function)

    # Add keymaps
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type="EMPTY")
        kmi = km.keymap_items.new(EditCollection.bl_idname, "C", "PRESS", ctrl=True, alt=True)
        # kmi.properties.total = 4
        addon_keymaps.append((km, kmi))


def unregister():
    # Unregister classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(EditCollection)
    bpy.utils.unregister_class(EditInstancedCollectionPreferences)

    # Remove menu items
    bpy.types.VIEW3D_MT_object.remove(menu_function)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_function)

    # Clear keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()

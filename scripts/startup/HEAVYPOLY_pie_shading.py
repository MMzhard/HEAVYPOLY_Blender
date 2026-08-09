bl_info = {
    "name": "Pie Shading",
    "description": "Shading Modes",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (5, 2, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Pie Menu"
}

import bpy
from bpy.types import Menu

class HP_MT_pie_shading(Menu):
    bl_label = "Shading"
    bl_space_type = 'VIEW_3D'
    def draw(self, context):

        layout = self.layout

        view = context.space_data
        shading = view.shading
        obj = context.active_object
        overlay = view.overlay
        tool_settings = context.tool_settings
        object_mode = 'OBJECT' if obj is None else obj.mode
        pie = layout.menu_pie()
        #LEFT
        pie.prop_enum(view.shading, "type", value='WIREFRAME', icon = 'NONE', text = 'WIRE')
        #RIGHT
        
        split = pie.split()

        view = context.space_data
        
        pie.operator('view3d.localview', text='ISOLATE').frame_selected = False
        #TOP
        pie.prop_enum(view.shading, "type", value='MATERIAL', icon = 'NONE', text = 'MATERIAL')

        #TOP LEFT
        pie.prop_enum(view.shading, "type", value='SOLID', icon = 'NONE', text = 'SOLID')

        #TOP RIGHT
        pie.prop_enum(view.shading, "type", value='RENDERED', icon = 'NONE', text = 'RENDERED')

        #BOTTOM LEFT
        split = pie.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("scene.light_cache_bake", text='Bake Lighting')
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("scene.light_cache_free", text='Free Lighting')

        #BOTTOM RIGHT
        split = pie.split()
        col = split.column(align=True)
        col.scale_y=1.4

        box = col.box()
        box.prop(overlay, "show_overlays", text="OVERLAYS")
        box.prop(overlay, "show_extras", text="EXTRAS")
        box.prop(context.scene.eevee, "use_soft_shadows", text="SOFT SHADOWS")
        box.prop(overlay, "show_cursor", text="3D CURSOR")
        box.operator("object.toggle_shade_smooth", text = 'Shade Smooth')


class HP_OT_shading_wire(bpy.types.Operator):
    bl_idname = "shading.wire"
    bl_label = "hp_shading_wire"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.data.screens["Default"].shading.type = 'SOLID'
        bpy.ops.view3d.toggle_shading(type='WIREFRAME')
        bpy.context.space_data.shading.show_xray = True
        bpy.context.space_data.shading.xray_alpha = 1
        bpy.context.space_data.shading.show_object_outline = 1
        return {'FINISHED'}
    
class HP_OT_shading_material(bpy.types.Operator):
    bl_idname = "shading.material"
    bl_label = "hp_shading_material"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.view3d.toggle_shading(type='MATERIAL')
        bpy.context.space_data.shading.show_xray = False
        bpy.context.space_data.shading.xray_alpha = 0
        return {'FINISHED'}
    
class HP_OT_shading_solid(bpy.types.Operator):
    bl_idname = "shading.solid"
    bl_label = "hp_shading_wire"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.view3d.toggle_shading(type='SOLID')
        bpy.context.space_data.shading.show_xray = False
        bpy.context.space_data.shading.xray_alpha = 0
        return {'FINISHED'}
        
class HP_OT_shading_rendered(bpy.types.Operator):
    bl_idname = "shading.rendered"
    bl_label = "hp_shading_rendered"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.view3d.toggle_shading(type='RENDERED')
        bpy.context.space_data.shading.show_xray = False
        bpy.context.space_data.shading.xray_alpha = 0
        return {'FINISHED'}
        
class HP_OT_shading_bg_wire(bpy.types.Operator):
    bl_idname = "shading.bg_wire"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        for ob in bpy.context.selected_objects:
            ob.display_type = 'TEXTURED'
        bpy.ops.object.select_all(action='INVERT')
        for ob in bpy.context.selected_objects:
            ob.display_type = 'WIRE'
        bpy.ops.object.select_all(action='INVERT')
        return {'FINISHED'}
    
####### Toggle Smooth / Flat Operator

class HP_OT_toggle_shade_smooth(bpy.types.Operator):
    bl_idname = "object.toggle_shade_smooth"
    bl_label = "Shade Smooth"
    bl_description = "Toggle Shade Smooth with Smooth by Angle modifier and set Ignore Sharpness"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            self.report({'WARNING'}, "No mesh objects selected.")
            return {'CANCELLED'}

        for obj in selected_meshes:
            # 既存の "Smooth by Angle" モディファイアを検索
            mod = next(
                (m for m in obj.modifiers if m.type == 'NODES' and m.node_group and "Smooth by Angle" in m.node_group.name),
                None
            )

            # すでにモディファイアが存在していれば削除（トグルオフ）
            if mod:
                obj.modifiers.remove(mod)
                context.view_layer.objects.active = obj
                bpy.ops.object.shade_flat()
            else:
                # 1. ベースメッシュは Flat に維持
                context.view_layer.objects.active = obj
                bpy.ops.object.shade_flat()

                # 2. Smooth by Angle モディファイアを追加
                try:
                    bpy.ops.object.modifier_add_node_group(
                        asset_library_type='ESSENTIALS',
                        asset_library_identifier="",
                        relative_asset_identifier="nodes\\geometry_nodes_essentials.blend\\NodeTree\\Smooth by Angle"
                    )
                except Exception:
                    try:
                        bpy.ops.object.modifier_add_node_group(
                            asset_library_type='ESSENTIALS',
                            asset_library_identifier="",
                            relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle"
                        )
                    except Exception as e:
                        self.report({'WARNING'}, f"Failed to add Smooth by Angle modifier: {e}")
                        continue

                # 3. 追加されたモディファイアを取得
                mod = next(
                    (m for m in obj.modifiers if m.type == 'NODES' and m.node_group and "Smooth by Angle" in m.node_group.name),
                    None
                )

                # 4. "Ignore Sharpness" (シャープを無視) を True に設定
                if mod:
                    socket_id = None
                    if mod.node_group and hasattr(mod.node_group, "interface"):
                        for item in mod.node_group.interface.items_tree:
                            if getattr(item, "item_type", "") == 'SOCKET' and getattr(item, "in_out", "") == 'INPUT':
                                if "ignore" in item.name.lower() or "シャープ" in item.name:
                                    socket_id = item.identifier
                                    break
                    
                    if not socket_id:
                        socket_id = "Socket_1"

                    try:
                        mod.properties.inputs[socket_id]["value"] = True
                    except Exception:
                        try:
                            mod.properties["inputs"][socket_id]["value"] = True
                        except Exception:
                            pass

                    # 5. ビューポート描画の即時反映処理
                    mod.show_viewport = False
                    mod.show_viewport = True
                    obj.update_tag()

        context.view_layer.update()
        return {'FINISHED'}

classes = (
    HP_MT_pie_shading,
    HP_OT_shading_wire,
    HP_OT_shading_material,
    HP_OT_shading_solid,
    HP_OT_shading_rendered,
    HP_OT_shading_bg_wire,
    HP_OT_toggle_shade_smooth
)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()

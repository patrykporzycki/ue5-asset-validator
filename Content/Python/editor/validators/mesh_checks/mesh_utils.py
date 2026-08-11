import unreal

def _static_mesh_subsystem():
    return unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)

def _skeletal_mesh_subsystem():
    return unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)

def _iter_lod_build_settings(asset):
    if isinstance(asset, unreal.StaticMesh):
        subsys = _static_mesh_subsystem()
        for lod in range(subsys.get_lod_count(asset)):
            yield subsys.get_lod_build_settings(asset, lod)
    else:
        for model in asset.get_editor_property("source_models"):
            yield model.get_editor_property("build_settings")

def get_build_setting(asset, build_property):
    for build_settings in _iter_lod_build_settings(asset):
        if build_settings.get_editor_property(build_property):
            return True
    return False

def get_mikk_t_space(asset):
    for build_settings in _iter_lod_build_settings(asset):
        if not build_settings.get_editor_property("use_mikk_t_space"):
            return False
    return True

def get_materials_properties(asset):
    if isinstance(asset, unreal.StaticMesh):
        subsys = _static_mesh_subsystem()
        prop_name = "static_materials"
    else:
        subsys = _skeletal_mesh_subsystem()
        prop_name = "materials"

    slot_section_usage = {}
    for lod in range(subsys.get_lod_count(asset)):
        for section in range(subsys.get_num_sections(asset, lod)):
            slot_index = subsys.get_lod_material_slot(asset, lod, section)
            if slot_index >= 0:
                if slot_index not in slot_section_usage:
                    slot_section_usage[slot_index] = set()
                slot_section_usage[slot_index].add(section)

    materials = asset.get_editor_property(prop_name)
    material_slots = []
    for material in materials:
        material_interface = material.get_editor_property("material_interface")
        material_slots.append({
            "slot_name": material.get_editor_property("material_slot_name"),
            "material": material_interface.get_name() if material_interface else None,
        })

    return material_slots, slot_section_usage

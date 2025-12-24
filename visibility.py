from models import Unit, VisibilityLevel

def get_visible_unit(unit: Unit, viewer_id: str): # No normalization, viewer_id is used as-is, remind to validate
    level = unit.visibility.get(viewer_id, VisibilityLevel.UNKNOWN)
    if viewer_id not in unit.visibility: # Debugging aid
        print(f"[WARN] Viewer '{viewer_id}' has no visibility entry for unit {unit.id}")


    if level == VisibilityLevel.UNKNOWN:
        return None

    data = {
        "id": unit.id,
        "position": unit.position,
        "symbol": unit.symbol,
        "visibility": level.name,
    }

    if level.value >= VisibilityLevel.DETAILED.value:
        data["faction"] = unit.faction_id

    return data

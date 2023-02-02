def parentize(child: str, parent: dict = None) -> dict:
    return {
        "_id": child,
        "parent": parent
    } if parent is not None else {
        "_id": child
    }
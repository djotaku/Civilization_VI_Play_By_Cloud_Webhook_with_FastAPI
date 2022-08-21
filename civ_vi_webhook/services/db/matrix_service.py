from ...models.db.matrix import Matrix


async def write_next_batch(next_batch: str):
    """Write the next batch info for the Matrix listener."""
    matrix = Matrix(next_batch=next_batch)
    await matrix.save()


async def get_next_batch() -> str:
    """Get the next batch info for the Matrix listener"""
    matrix = await Matrix.find_one()
    return matrix.next_batch

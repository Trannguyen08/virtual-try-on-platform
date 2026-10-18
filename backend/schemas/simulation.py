from backend.schemas.common import AssetSchema, ContractModel


class SimulationSchema(ContractModel):
    body_mesh: AssetSchema | None
    garment_mesh: AssetSchema | None
    tryon_mesh: AssetSchema | None

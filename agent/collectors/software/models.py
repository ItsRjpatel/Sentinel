from pydantic import BaseModel, Field

class SoftwareInventoryData(BaseModel):
    """Pydantic validated DTO containing installed software application details."""
    application_name: str = Field(..., max_length=255)
    publisher: str = Field(..., max_length=255)
    version: str = Field(..., max_length=100)
    install_date: str = Field(..., max_length=50)
    install_location: str = Field(..., max_length=500)
    estimated_size_kb: int = Field(..., ge=0)
    uninstall_string: str = Field(..., max_length=500)
    install_source: str = Field(..., max_length=500)
    architecture: str = Field(..., max_length=50)
    language: str = Field(..., max_length=50)
    product_code: str = Field(..., max_length=100)
    system_component: bool
    windows_installer: bool
    url_info: str = Field(..., max_length=500)
    help_link: str = Field(..., max_length=500)
    modify_path: str = Field(..., max_length=500)
    install_scope: str = Field(..., max_length=50)
    registry_key: str = Field(..., max_length=500)

"""add_unique_constraints_to_inventory

Revision ID: 926c11bab7b4
Revises: 47132bd48eb0
Create Date: 2026-08-09 02:33:53.745010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '926c11bab7b4'
down_revision: Union[str, Sequence[str], None] = '47132bd48eb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Network Adapter Inventory
    op.execute("""
        DELETE FROM network_adapter_inventory 
        WHERE id NOT IN (
            SELECT min(id::text)::uuid FROM network_adapter_inventory 
            GROUP BY endpoint_id, interface_guid
        )
    """)
    op.create_unique_constraint(
        "uq_network_adapter_endpoint_guid", 
        "network_adapter_inventory", 
        ["endpoint_id", "interface_guid"]
    )

    # 2. Physical Disk Inventory
    op.execute("""
        DELETE FROM physical_disk_inventory 
        WHERE id NOT IN (
            SELECT min(id::text)::uuid FROM physical_disk_inventory 
            GROUP BY endpoint_id, serial_number
        )
    """)
    op.create_unique_constraint(
        "uq_physical_disk_endpoint_serial", 
        "physical_disk_inventory", 
        ["endpoint_id", "serial_number"]
    )

    # 3. Logical Volume Inventory
    op.execute("""
        DELETE FROM logical_volume_inventory 
        WHERE id NOT IN (
            SELECT min(id::text)::uuid FROM logical_volume_inventory 
            GROUP BY disk_id, volume_guid
        )
    """)
    op.create_unique_constraint(
        "uq_logical_volume_disk_guid", 
        "logical_volume_inventory", 
        ["disk_id", "volume_guid"]
    )

    # 4. Software Inventory
    op.execute("""
        DELETE FROM software_inventory 
        WHERE id NOT IN (
            SELECT min(id::text)::uuid FROM software_inventory 
            GROUP BY endpoint_id, application_name, publisher, version
        )
    """)
    op.create_unique_constraint(
        "uq_software_endpoint_app_pub_ver", 
        "software_inventory", 
        ["endpoint_id", "application_name", "publisher", "version"]
    )

    # 5. Windows Update Inventory
    op.execute("""
        DELETE FROM windows_update_inventory 
        WHERE id NOT IN (
            SELECT min(id::text)::uuid FROM windows_update_inventory 
            GROUP BY endpoint_id, kb_number
        )
    """)
    op.create_unique_constraint(
        "uq_windows_update_endpoint_kb", 
        "windows_update_inventory", 
        ["endpoint_id", "kb_number"]
    )

    # 6. Windows Service Inventory
    op.execute("""
        DELETE FROM windows_service_inventory 
        WHERE id NOT IN (
            SELECT min(id::text)::uuid FROM windows_service_inventory 
            GROUP BY endpoint_id, service_name
        )
    """)
    op.create_unique_constraint(
        "uq_windows_service_endpoint_name", 
        "windows_service_inventory", 
        ["endpoint_id", "service_name"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_windows_service_endpoint_name", "windows_service_inventory", type_="unique")
    op.drop_constraint("uq_windows_update_endpoint_kb", "windows_update_inventory", type_="unique")
    op.drop_constraint("uq_software_endpoint_app_pub_ver", "software_inventory", type_="unique")
    op.drop_constraint("uq_logical_volume_disk_guid", "logical_volume_inventory", type_="unique")
    op.drop_constraint("uq_physical_disk_endpoint_serial", "physical_disk_inventory", type_="unique")
    op.drop_constraint("uq_network_adapter_endpoint_guid", "network_adapter_inventory", type_="unique")

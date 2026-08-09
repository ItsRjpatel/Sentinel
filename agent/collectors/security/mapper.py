from agent.collectors.security.models import SecurityInventoryData

def map_raw_security(raw_data: dict) -> SecurityInventoryData:
    return SecurityInventoryData(
        defender_enabled=bool(raw_data.get("defender_enabled", False)),
        real_time_protection_enabled=bool(raw_data.get("real_time_protection_enabled", False)),
        defender_service_status=str(raw_data.get("defender_service_status", "Stopped")),
        antivirus_signature_version=str(raw_data.get("antivirus_signature_version", "Unknown")),
        firewall_domain_enabled=bool(raw_data.get("firewall_domain_enabled", False)),
        firewall_private_enabled=bool(raw_data.get("firewall_private_enabled", False)),
        firewall_public_enabled=bool(raw_data.get("firewall_public_enabled", False))
    )

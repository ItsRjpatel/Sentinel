import os
import base64
import ctypes
from typing import Optional

IS_WINDOWS = os.name == "nt"

if IS_WINDOWS:
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_char))
        ]


def _encrypt_dpapi(data: bytes, entropy: bytes = b"") -> bytes:
    """Windows-specific DPAPI encryption using crypt32.dll."""
    crypt32 = ctypes.windll.crypt32
    
    data_in = DATA_BLOB()
    data_in.cbData = len(data)
    data_in.pbData = ctypes.cast(
        ctypes.create_string_buffer(data),
        ctypes.POINTER(ctypes.c_char)
    )
    
    entropy_in = None
    if entropy:
        entropy_in = DATA_BLOB()
        entropy_in.cbData = len(entropy)
        entropy_in.pbData = ctypes.cast(
            ctypes.create_string_buffer(entropy),
            ctypes.POINTER(ctypes.c_char)
        )
        
    data_out = DATA_BLOB()
    flags = 1 | 4 # CRYPTPROTECT_UI_FORBIDDEN (1) | CRYPTPROTECT_LOCAL_MACHINE (4)
    
    success = crypt32.CryptProtectData(
        ctypes.byref(data_in),
        None,  # Description
        ctypes.byref(entropy_in) if entropy_in else None,
        None,  # Reserved
        None,  # Prompt struct
        flags,
        ctypes.byref(data_out)
    )
    
    if not success:
        raise OSError("Windows DPAPI encryption failed.")
        
    try:
        encrypted = ctypes.string_at(data_out.pbData, data_out.cbData)
        return encrypted
    finally:
        ctypes.windll.kernel32.LocalFree(data_out.pbData)


def _decrypt_dpapi(encrypted_data: bytes, entropy: bytes = b"") -> bytes:
    """Windows-specific DPAPI decryption using crypt32.dll."""
    crypt32 = ctypes.windll.crypt32
    
    data_in = DATA_BLOB()
    data_in.cbData = len(encrypted_data)
    data_in.pbData = ctypes.cast(
        ctypes.create_string_buffer(encrypted_data),
        ctypes.POINTER(ctypes.c_char)
    )
    
    entropy_in = None
    if entropy:
        entropy_in = DATA_BLOB()
        entropy_in.cbData = len(entropy)
        entropy_in.pbData = ctypes.cast(
            ctypes.create_string_buffer(entropy),
            ctypes.POINTER(ctypes.c_char)
        )
        
    data_out = DATA_BLOB()
    flags = 1 | 4 # CRYPTPROTECT_UI_FORBIDDEN (1) | CRYPTPROTECT_LOCAL_MACHINE (4)
    
    success = crypt32.CryptUnprotectData(
        ctypes.byref(data_in),
        None,
        ctypes.byref(entropy_in) if entropy_in else None,
        None,
        None,
        flags,
        ctypes.byref(data_out)
    )
    
    if not success:
        raise OSError("Windows DPAPI decryption failed.")
        
    try:
        decrypted = ctypes.string_at(data_out.pbData, data_out.cbData)
        return decrypted
    finally:
        ctypes.windll.kernel32.LocalFree(data_out.pbData)


def encrypt(data: bytes, entropy: bytes = b"") -> bytes:
    """Encrypts data. Uses Windows DPAPI if on Windows, else falls back to Base64."""
    if IS_WINDOWS:
        return _encrypt_dpapi(data, entropy)
    # Fallback encryption for local test suites on non-Windows dev machines
    return base64.b64encode(data)


def decrypt(encrypted_data: bytes, entropy: bytes = b"") -> bytes:
    """Decrypts data. Uses Windows DPAPI if on Windows, else falls back to Base64."""
    if IS_WINDOWS:
        return _decrypt_dpapi(encrypted_data, entropy)
    return base64.b64decode(encrypted_data)
